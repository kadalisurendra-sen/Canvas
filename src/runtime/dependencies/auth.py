"""FastAPI dependency for JWT validation — get_current_user."""
import logging
import uuid

import httpx
from fastapi import Depends, HTTPException, Request
from jose import jwt as jose_jwt, JWTError

from src.config.settings import get_settings
from src.service.keycloak_client import KeycloakClient
from src.types.auth import UserContext
from src.types.enums import UserRole

logger = logging.getLogger(__name__)

# JWKS cache (module-level, shared across requests)
_jwks_cache: dict[str, list[dict[str, str]]] | None = None

# Dev mode user
_DEV_USER = UserContext(
    user_id=uuid.UUID("a0000000-0000-0000-0000-000000000001"),
    email="admin@helio.local",
    name="Alex Rivera",
    roles=[UserRole.ADMIN],
    tenant_id=uuid.UUID("a0000000-0000-0000-0000-000000000001"),
)


async def _get_jwks() -> dict[str, list[dict[str, str]]]:
    """Fetch and cache JWKS from Keycloak."""
    global _jwks_cache
    if _jwks_cache is None:
        kc = KeycloakClient()
        async with httpx.AsyncClient() as client:
            resp = await client.get(kc.jwks_url, timeout=10.0)
            _jwks_cache = resp.json()
    return _jwks_cache


async def get_current_user(request: Request) -> UserContext:
    """Extract and validate JWT, returning a typed UserContext."""
    settings = get_settings()

    if settings.AUTH_MODE == "dev":
        return _DEV_USER

    token = _extract_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        jwks = await _get_jwks()
        header = jose_jwt.get_unverified_header(token)
        kid = header.get("kid")

        signing_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                signing_key = key
                break

        if not signing_key:
            global _jwks_cache
            _jwks_cache = None  # Force refresh on next call
            raise HTTPException(status_code=401, detail="Invalid token key")

        payload = jose_jwt.decode(
            token, signing_key, algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except JWTError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    # Extract roles
    realm_access = payload.get("realm_access", {})
    roles_raw = realm_access.get("roles", []) if isinstance(realm_access, dict) else []
    roles = []
    for r in roles_raw:
        try:
            roles.append(UserRole(r))
        except ValueError:
            pass

    default_tenant = "a0000000-0000-0000-0000-000000000001"
    return UserContext(
        user_id=uuid.UUID(payload.get("sub", default_tenant)),
        email=str(payload.get("email", "")),
        name=str(payload.get("name", "")),
        roles=roles,
        tenant_id=uuid.UUID(default_tenant),
    )


def _extract_token(request: Request) -> str:
    """Extract Bearer token from header or cookie."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return request.cookies.get("access_token", "")


def require_role(*roles: UserRole):  # type: ignore[no-untyped-def]
    """Create a dependency that requires specific roles."""

    async def role_checker(
        user: UserContext = Depends(get_current_user),
    ) -> UserContext:
        if not any(role in user.roles for role in roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user

    return role_checker

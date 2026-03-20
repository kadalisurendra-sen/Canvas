"""Authentication routes — login, callback, logout, me, refresh, register."""
import logging
import time

from fastapi import APIRouter, Cookie, Header, HTTPException, Response
from pydantic import BaseModel

from src.config.settings import get_settings
from src.service.keycloak_client import KeycloakClient

# Cache JWKS keys and realm lookups to avoid repeated HTTP calls
_jwks_cache: dict[str, tuple[dict, float]] = {}
_realm_cache: dict[str, tuple[str, float]] = {}
_JWKS_TTL = 300  # 5 minutes
_REALM_TTL = 300  # 5 minutes

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

ACCESS_TOKEN_MAX_AGE = 900       # 15 minutes
REFRESH_TOKEN_MAX_AGE = 28800    # 8 hours


class LoginRequest(BaseModel):
    """Login request with username and password."""

    username: str
    password: str


class RegisterRequest(BaseModel):
    """Registration request."""

    email: str
    username: str
    password: str
    first_name: str = ""
    last_name: str = ""


def _set_auth_cookies(
    response: Response, access_token: str, refresh_token: str,
) -> None:
    """Set access and refresh token cookies."""
    is_secure = get_settings().APP_ENV != "development"

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        max_age=ACCESS_TOKEN_MAX_AGE,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=is_secure,
        samesite="lax",
        path="/api/v1/auth",  # only sent to auth endpoints
        max_age=REFRESH_TOKEN_MAX_AGE,
    )


@router.post("/login")
async def login(
    body: LoginRequest,
    response: Response,
    x_tenant_id: str = Header(default="", alias="X-Tenant-ID"),
) -> dict[str, str]:
    """Authenticate user via Keycloak direct access grant."""
    realm = await _lookup_realm(x_tenant_id) if x_tenant_id else get_settings().KEYCLOAK_REALM
    logger.info(
        "Login attempt: user=%s, tenant_header=%s, resolved_realm=%s",
        body.username, x_tenant_id, realm,
    )
    kc = KeycloakClient(realm_override=realm)

    try:
        tokens = await kc.password_grant(body.username, body.password)
    except Exception as exc:
        logger.warning(
            "Login failed for user=%s realm=%s: %s",
            body.username, realm, exc,
        )
        raise HTTPException(
            status_code=401, detail="Invalid username or password"
        ) from exc

    _set_auth_cookies(
        response,
        tokens.get("access_token", ""),
        tokens.get("refresh_token", ""),
    )

    from src.repo.analytics_repository import create_tenant_audit_log_by_id
    await create_tenant_audit_log_by_id(
        tenant_id=x_tenant_id,
        user_id=None, user_name=body.username,
        event_type="AUTH", action="user_login",
        details=f"Login successful for '{body.username}'",
    )

    return {"message": "Login successful", "redirect": "/templates"}


@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: str = Cookie(default=""),
    x_tenant_id: str = Header(default="", alias="X-Tenant-ID"),
) -> dict[str, str]:
    """Use refresh token to get a new access token silently."""
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    realm = await _lookup_realm(x_tenant_id) if x_tenant_id else get_settings().KEYCLOAK_REALM
    kc = KeycloakClient(realm_override=realm)

    try:
        tokens = await kc.refresh_grant(refresh_token)
    except Exception as exc:
        logger.warning("Token refresh failed: %s", exc)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token", path="/api/v1/auth")
        raise HTTPException(
            status_code=401, detail="Refresh token expired. Please log in again."
        ) from exc

    _set_auth_cookies(
        response,
        tokens.get("access_token", ""),
        tokens.get("refresh_token", ""),
    )

    return {"message": "Token refreshed"}


@router.post("/register")
async def register(
    body: RegisterRequest,
    x_tenant_id: str = Header(default="", alias="X-Tenant-ID"),
) -> dict[str, str]:
    """Register via Keycloak Admin API."""
    settings = get_settings()
    kc_url = settings.KEYCLOAK_URL.rstrip("/")
    realm = await _lookup_realm(x_tenant_id) if x_tenant_id else settings.KEYCLOAK_REALM
    logger.info(
        "Register attempt: user=%s, tenant_header=%s, resolved_realm=%s",
        body.username, x_tenant_id, realm,
    )

    import httpx

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            f"{kc_url}/realms/master/protocol/openid-connect/token",
            data={
                "grant_type": "password",
                "client_id": "admin-cli",
                "username": "admin",
                "password": "admin",
            },
            timeout=10.0,
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=500, detail="Registration service unavailable"
            )

        admin_token = token_resp.json()["access_token"]

        user_resp = await client.post(
            f"{kc_url}/admin/realms/{realm}/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "username": body.username,
                "email": body.email,
                "firstName": body.first_name or body.username,
                "lastName": body.last_name or "User",
                "enabled": True,
                "emailVerified": True,
                "credentials": [
                    {
                        "type": "password",
                        "value": body.password,
                        "temporary": False,
                    }
                ],
            },
            timeout=10.0,
        )

        if user_resp.status_code == 409:
            raise HTTPException(
                status_code=409, detail="Username or email already exists"
            )
        if user_resp.status_code != 201:
            logger.error("Registration failed: %s", user_resp.text)
            raise HTTPException(
                status_code=500, detail="Registration failed"
            )

        # Keycloak 24+ ignores credentials in create payload — set password explicitly
        location = user_resp.headers.get("Location", "")
        user_id = location.rsplit("/", 1)[-1] if location else ""
        if user_id:
            pwd_resp = await client.put(
                f"{kc_url}/admin/realms/{realm}/users/{user_id}/reset-password",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "type": "password",
                    "value": body.password,
                    "temporary": False,
                },
                timeout=10.0,
            )
            if pwd_resp.status_code != 204:
                logger.error(
                    "Password set failed for %s: %s", user_id, pwd_resp.text
                )

    from src.repo.analytics_repository import create_tenant_audit_log_by_id
    await create_tenant_audit_log_by_id(
        tenant_id=x_tenant_id,
        user_id=None, user_name=body.username,
        event_type="AUTH", action="user_registered",
        details=f"New user registered: '{body.username}' ({body.email})",
    )

    return {"message": "Registration successful. You can now sign in."}


@router.post("/logout")
async def logout(
    response: Response,
    access_token: str = Cookie(default=""),
    refresh_token: str = Cookie(default=""),
    x_tenant_id: str = Header(default="", alias="X-Tenant-ID"),
) -> dict[str, str]:
    """Clear session cookies and revoke tokens."""
    if refresh_token:
        try:
            kc = KeycloakClient()
            await kc.revoke_token(refresh_token)
        except Exception as exc:
            logger.warning("Token revocation failed: %s", exc)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/api/v1/auth")

    from src.repo.analytics_repository import create_tenant_audit_log_by_id
    await create_tenant_audit_log_by_id(
        tenant_id=x_tenant_id,
        user_id=None, user_name=None,
        event_type="AUTH", action="user_logout",
        details="User logged out",
    )

    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_profile(
    access_token: str = Cookie(default=""),
    x_tenant_id: str = Header(default="", alias="X-Tenant-ID"),
) -> dict[str, str | list[str]]:
    """Return current user profile from JWT."""
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    settings = get_settings()

    # Use cached realm lookup
    if x_tenant_id:
        cached_realm = _realm_cache.get(x_tenant_id)
        if cached_realm and cached_realm[1] > time.monotonic():
            realm = cached_realm[0]
        else:
            realm = await _lookup_realm(x_tenant_id)
            _realm_cache[x_tenant_id] = (realm, time.monotonic() + _REALM_TTL)
    else:
        realm = settings.KEYCLOAK_REALM

    from jose import jwt as jose_jwt, JWTError

    kc = KeycloakClient(realm_override=realm)
    try:
        # Use cached JWKS
        cached_jwks = _jwks_cache.get(realm)
        if cached_jwks and cached_jwks[1] > time.monotonic():
            jwks_data = cached_jwks[0]
        else:
            import httpx
            async with httpx.AsyncClient() as client:
                jwks_resp = await client.get(kc.jwks_url, timeout=10.0)
                jwks_data = jwks_resp.json()
            _jwks_cache[realm] = (jwks_data, time.monotonic() + _JWKS_TTL)

        header = jose_jwt.get_unverified_header(access_token)
        kid = header.get("kid")

        signing_key = None
        for key in jwks_data.get("keys", []):
            if key.get("kid") == kid:
                signing_key = key
                break

        if not signing_key:
            # Refresh cache and retry
            import httpx
            async with httpx.AsyncClient() as client:
                jwks_resp = await client.get(kc.jwks_url, timeout=10.0)
                jwks_data = jwks_resp.json()
            _jwks_cache[realm] = (jwks_data, time.monotonic() + _JWKS_TTL)
            for key in jwks_data.get("keys", []):
                if key.get("kid") == kid:
                    signing_key = key
                    break
            if not signing_key:
                raise HTTPException(status_code=401, detail="Invalid token signing key")

        payload = jose_jwt.decode(
            access_token,
            signing_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
    except JWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}") from exc

    realm_access = payload.get("realm_access", {})
    roles = realm_access.get("roles", []) if isinstance(realm_access, dict) else []
    app_roles = [r for r in roles if r in ("system_admin", "admin", "contributor", "viewer")]

    return {
        "id": payload.get("sub", ""),
        "email": payload.get("email", ""),
        "name": payload.get("name", ""),
        "roles": app_roles,
    }


async def _lookup_realm(tenant_id: str) -> str:
    """Look up Keycloak realm for a tenant by ID or slug."""
    from sqlalchemy import text
    from src.repo.database import create_platform_engine

    if not tenant_id:
        logger.info("_lookup_realm: no tenant_id, using default realm")
        return get_settings().KEYCLOAK_REALM

    try:
        _, session_factory = create_platform_engine()
        async with session_factory() as session:
            result = await session.execute(
                text(
                    "SELECT keycloak_realm FROM tenants "
                    "WHERE id::text = :tid OR slug = :tid"
                ),
                {"tid": tenant_id},
            )
            row = result.first()
            if row:
                logger.info(
                    "_lookup_realm: tenant=%s -> realm=%s",
                    tenant_id, row.keycloak_realm,
                )
                return row.keycloak_realm
            logger.warning(
                "_lookup_realm: tenant '%s' not found in DB, using default",
                tenant_id,
            )
    except Exception as exc:
        logger.error("_lookup_realm DB error: %s", exc)

    return get_settings().KEYCLOAK_REALM

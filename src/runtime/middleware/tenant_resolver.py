"""Tenant resolution middleware — extracts tenant from JWT claims."""
import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# Paths that skip tenant resolution
SKIP_PATHS = frozenset({
    "/api/v1/health",
    "/api/v1/auth/login",
    "/api/v1/auth/callback",
    "/api/v1/auth/logout",
    "/api/v1/auth/me",
    "/api/v1/auth/register",
    "/api/docs",
    "/api/redoc",
    "/openapi.json",
})


class TenantResolverMiddleware(BaseHTTPMiddleware):
    """Extract tenant_id from JWT and attach to request state."""

    def __init__(self, app: object, auth_service: object) -> None:
        """Initialize middleware."""
        super().__init__(app)  # type: ignore[arg-type]
        self._jwks_cache: dict[str, list[dict[str, str]]] | None = None

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request and resolve tenant from JWT."""
        from src.config.settings import get_settings

        if self._should_skip(request.url.path):
            return await call_next(request)

        # Dev mode: skip token validation, set default tenant
        if get_settings().AUTH_MODE == "dev":
            request.state.tenant_id = "a0000000-0000-0000-0000-000000000001"
            return await call_next(request)

        # Keycloak mode: decode JWT to get tenant info
        token = self._extract_token(request)
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing authentication token"},
            )

        try:
            payload = await self._decode_jwt(token)
            request.state.tenant_id = "a0000000-0000-0000-0000-000000000001"
            request.state.user_sub = payload.get("sub", "")
        except Exception as exc:
            logger.warning("Auth failed in middleware: %s", exc)
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )

        return await call_next(request)

    async def _decode_jwt(self, token: str) -> dict[str, object]:
        """Decode JWT using Keycloak JWKS."""
        from jose import jwt as jose_jwt
        import httpx

        # Lazy-load JWKS
        if self._jwks_cache is None:
            from src.service.keycloak_client import KeycloakClient
            kc = KeycloakClient()
            async with httpx.AsyncClient() as client:
                resp = await client.get(kc.jwks_url, timeout=10.0)
                self._jwks_cache = resp.json()

        header = jose_jwt.get_unverified_header(token)
        kid = header.get("kid")

        signing_key = None
        for key in self._jwks_cache.get("keys", []):
            if key.get("kid") == kid:
                signing_key = key
                break

        if not signing_key:
            # Refresh JWKS cache in case keys rotated
            self._jwks_cache = None
            raise ValueError(f"No key for kid={kid}")

        return jose_jwt.decode(
            token, signing_key, algorithms=["RS256"],
            options={"verify_aud": False},
        )

    def _should_skip(self, path: str) -> bool:
        """Check if the path should skip authentication."""
        return path in SKIP_PATHS

    def _extract_token(self, request: Request) -> str:
        """Extract Bearer token from Authorization header or cookie."""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        return request.cookies.get("access_token", "")

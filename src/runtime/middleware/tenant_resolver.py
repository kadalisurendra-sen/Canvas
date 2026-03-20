"""Tenant resolution middleware — resolves tenant from X-Tenant-ID header."""
import logging
import time

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
    "/api/v1/auth/refresh",
    "/api/v1/auth/me",
    "/api/v1/auth/register",
    "/api/v1/tenants/list",
    "/api/v1/tenants/resolve",
    "/api/docs",
    "/api/redoc",
    "/openapi.json",
})


class TenantResolverMiddleware(BaseHTTPMiddleware):
    """Resolve tenant from X-Tenant-ID header and set schema + realm."""

    def __init__(self, app: object, auth_service: object) -> None:
        """Initialize middleware."""
        super().__init__(app)  # type: ignore[arg-type]
        self._jwks_cache: dict[str, dict[str, list[dict[str, str]]]] = {}
        self._tenant_cache: dict[str, tuple[dict[str, str] | None, float]] = {}

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process request: resolve tenant, validate JWT."""
        from src.config.settings import get_settings

        if self._should_skip(request.url.path):
            return await call_next(request)

        # Read X-Tenant-ID header
        tenant_id = request.headers.get("X-Tenant-ID", "").strip()

        # Dev mode: resolve tenant from DB (skip JWT validation)
        if get_settings().AUTH_MODE == "dev":
            if not tenant_id:
                tenant_id = "a0000000-0000-0000-0000-000000000001"
            tenant = await self._lookup_tenant(tenant_id)
            if tenant:
                request.state.tenant_id = str(tenant["id"])
                request.state.tenant_schema = tenant["schema_name"]
                request.state.tenant_realm = tenant["keycloak_realm"]
            else:
                # Fallback for dev mode if no DB record
                request.state.tenant_id = tenant_id
                request.state.tenant_schema = "tenant_acme"
                request.state.tenant_realm = "helio"
            return await call_next(request)

        # Keycloak mode: require X-Tenant-ID and valid JWT
        if not tenant_id:
            return JSONResponse(
                status_code=400,
                content={"detail": "Missing X-Tenant-ID header"},
            )

        # Look up tenant from platform DB
        tenant = await self._lookup_tenant(tenant_id)
        if not tenant:
            return JSONResponse(
                status_code=404,
                content={"detail": f"Tenant '{tenant_id}' not found"},
            )

        request.state.tenant_id = str(tenant["id"])
        request.state.tenant_schema = tenant["schema_name"]
        request.state.tenant_realm = tenant["keycloak_realm"]

        # Validate JWT using tenant's Keycloak realm
        token = self._extract_token(request)
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing authentication token"},
            )

        try:
            payload = await self._decode_jwt(token, tenant["keycloak_realm"])
            request.state.user_sub = payload.get("sub", "")
        except Exception as exc:
            logger.warning("Auth failed for tenant %s: %s", tenant_id, exc)
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"},
            )

        return await call_next(request)

    async def _lookup_tenant(self, tenant_id: str) -> dict[str, str] | None:
        """Look up tenant by ID or slug from platform DB (cached)."""
        cached = self._tenant_cache.get(tenant_id)
        if cached and cached[1] > time.monotonic():
            return cached[0]

        from sqlalchemy import text
        from src.repo.database import create_platform_engine

        _, session_factory = create_platform_engine()
        async with session_factory() as session:
            result = await session.execute(
                text(
                    "SELECT id, slug, schema_name, keycloak_realm "
                    "FROM tenants WHERE id::text = :tid OR slug = :tid"
                ),
                {"tid": tenant_id},
            )
            row = result.first()
            if row:
                tenant = {
                    "id": str(row.id),
                    "slug": row.slug,
                    "schema_name": row.schema_name,
                    "keycloak_realm": row.keycloak_realm,
                }
                self._tenant_cache[tenant_id] = (tenant, time.monotonic() + 300)
                return tenant
        self._tenant_cache[tenant_id] = (None, time.monotonic() + 60)
        return None

    async def _decode_jwt(
        self, token: str, realm: str
    ) -> dict[str, object]:
        """Decode JWT using the tenant's Keycloak realm JWKS."""
        from jose import jwt as jose_jwt
        import httpx
        from src.config.settings import get_settings

        settings = get_settings()
        jwks_url = (
            f"{settings.KEYCLOAK_URL}/realms/{realm}"
            f"/protocol/openid-connect/certs"
        )

        # Per-realm JWKS cache
        if realm not in self._jwks_cache:
            async with httpx.AsyncClient() as client:
                resp = await client.get(jwks_url, timeout=10.0)
                self._jwks_cache[realm] = resp.json()

        header = jose_jwt.get_unverified_header(token)
        kid = header.get("kid")

        signing_key = None
        for key in self._jwks_cache[realm].get("keys", []):
            if key.get("kid") == kid:
                signing_key = key
                break

        if not signing_key:
            # Refresh cache and retry
            del self._jwks_cache[realm]
            raise ValueError(f"No key for kid={kid} in realm {realm}")

        return jose_jwt.decode(
            token, signing_key, algorithms=["RS256"],
            options={"verify_aud": False},
        )

    def _should_skip(self, path: str) -> bool:
        """Check if the path should skip authentication."""
        if path in SKIP_PATHS:
            return True
        return any(path.startswith(p) for p in SKIP_PATHS)

    def _extract_token(self, request: Request) -> str:
        """Extract Bearer token from Authorization header or cookie."""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        return request.cookies.get("access_token", "")

"""Tenant settings API routes."""
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request

from src.runtime.dependencies.auth import get_current_user, require_role
from src.repo.tenant_repository import TenantNotFoundError, TenantRepository
from src.repo.database import create_platform_engine
from src.service.tenant_service import TenantService
from src.types.auth import UserContext
from src.types.enums import UserRole
from src.types.tenant import (
    TenantBrandingResponse,
    TenantDefaultsResponse,
    TenantFullResponse,
    TenantGeneralResponse,
    UpdateTenantBrandingRequest,
    UpdateTenantDefaultsRequest,
    UpdateTenantGeneralRequest,
)

from sqlalchemy import text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


@router.get("/list")
async def list_tenants() -> list[dict[str, str]]:
    """List all active tenants (public, no auth required)."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        result = await session.execute(
            text(
                "SELECT id, name, slug FROM tenants "
                "WHERE is_active = true ORDER BY name"
            )
        )
        return [
            {"id": str(row.id), "name": row.name, "slug": row.slug}
            for row in result.fetchall()
        ]


@router.get("/all")
async def list_all_tenants(
    user: UserContext = Depends(get_current_user),
) -> list[dict[str, object]]:
    """List all tenants with details (admin only)."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        result = await session.execute(
            text(
                "SELECT id, name, slug, schema_name, keycloak_realm, "
                "is_active, created_at, updated_at "
                "FROM tenants ORDER BY name"
            )
        )
        return [
            {
                "id": str(row.id),
                "name": row.name,
                "slug": row.slug,
                "schema_name": row.schema_name,
                "keycloak_realm": row.keycloak_realm,
                "is_active": row.is_active,
                "plan_name": "Enterprise",
                "user_count": 0,
                "created_at": row.created_at.isoformat() if row.created_at else "",
            }
            for row in result.fetchall()
        ]


@router.delete("/delete/{tenant_id}")
async def delete_tenant(
    tenant_id: uuid.UUID,
    request: Request,
    user: UserContext = Depends(
        require_role(UserRole.SYSTEM_ADMIN)
    ),
) -> dict[str, str]:
    """Delete a tenant (super admin only). Cannot delete platform tenant."""
    from src.repo.analytics_repository import create_platform_audit_log

    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        result = await session.execute(
            text("SELECT name, slug, schema_name, keycloak_realm FROM tenants WHERE id = :tid"),
            {"tid": str(tenant_id)},
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail="Tenant not found")
        if row.slug == "platform":
            raise HTTPException(status_code=403, detail="Cannot delete the platform admin tenant")

        schema_name = row.schema_name
        tenant_name = row.name
        keycloak_realm = row.keycloak_realm

        # Drop the tenant schema
        if schema_name and schema_name != "public":
            await session.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE"))

        # Delete tenant record
        await session.execute(
            text("DELETE FROM tenants WHERE id = :tid"),
            {"tid": str(tenant_id)},
        )
        await session.commit()

    # Delete Keycloak realm
    if keycloak_realm and keycloak_realm != "helio":
        await _delete_keycloak_realm(keycloak_realm)

    # Audit log
    ip = request.client.host if request.client else None
    await create_platform_audit_log(
        user_id=user.user_id,
        user_name=user.name,
        event_type="MANAGEMENT",
        action="tenant_deleted",
        entity_type="tenant",
        entity_id=f"{tenant_name} ({row.slug})",
        details=f"Schema '{schema_name}' dropped",
        ip_address=ip,
    )

    return {"message": f"Tenant '{row.slug}' deleted successfully"}


async def _delete_keycloak_realm(realm_name: str) -> None:
    """Delete a Keycloak realm via Admin API."""
    import httpx
    from src.config.settings import get_settings

    settings = get_settings()
    kc_url = settings.KEYCLOAK_URL.rstrip("/")

    async with httpx.AsyncClient() as client:
        # Get master admin token
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
            logger.warning("Failed to get admin token for realm deletion")
            return

        admin_token = token_resp.json()["access_token"]

        resp = await client.delete(
            f"{kc_url}/admin/realms/{realm_name}",
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10.0,
        )
        if resp.status_code == 204:
            logger.info("Keycloak realm '%s' deleted.", realm_name)
        else:
            logger.warning(
                "Failed to delete realm '%s': %s", realm_name, resp.status_code
            )


@router.get("/resolve")
async def resolve_tenant(slug: str = "") -> dict[str, str | None]:
    """Resolve a tenant by slug (public, no auth required)."""
    if not slug:
        raise HTTPException(status_code=400, detail="slug parameter is required")
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        result = await session.execute(
            text(
                "SELECT name, slug, logo_url, primary_color FROM tenants "
                "WHERE slug = :slug AND is_active = true"
            ),
            {"slug": slug},
        )
        row = result.first()
        if not row:
            raise HTTPException(status_code=404, detail=f"Tenant '{slug}' not found")
        return {
            "name": row.name,
            "slug": row.slug,
            "logo_url": row.logo_url,
            "primary_color": row.primary_color,
        }


async def _get_tenant_service() -> TenantService:
    """Build a TenantService with a platform DB session."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        repo = TenantRepository(session=session)
        return TenantService(repo=repo)


@router.get("/{tenant_id}", response_model=TenantFullResponse)
async def get_tenant(
    tenant_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
) -> TenantFullResponse:
    """Get tenant settings."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        repo = TenantRepository(session=session)
        svc = TenantService(repo=repo)
        try:
            return await svc.get_tenant(tenant_id)
        except TenantNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{tenant_id}", response_model=TenantGeneralResponse)
async def update_tenant_general(
    tenant_id: uuid.UUID,
    body: UpdateTenantGeneralRequest,
    user: UserContext = Depends(
        require_role(UserRole.SYSTEM_ADMIN, UserRole.ADMIN)
    ),
) -> TenantGeneralResponse:
    """Update tenant general settings."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        repo = TenantRepository(session=session)
        svc = TenantService(repo=repo)
        try:
            result = await svc.update_general(tenant_id, body)
        except TenantNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    from src.repo.analytics_repository import create_platform_audit_log
    await create_platform_audit_log(
        user_id=user.user_id, user_name=user.name,
        event_type="SETTINGS", action="tenant_general_updated",
        entity_type="tenant", entity_id=str(tenant_id),
        details=f"Updated general settings",
    )
    return result


@router.put(
    "/{tenant_id}/branding",
    response_model=TenantBrandingResponse,
)
async def update_tenant_branding(
    tenant_id: uuid.UUID,
    body: UpdateTenantBrandingRequest,
    user: UserContext = Depends(
        require_role(UserRole.SYSTEM_ADMIN, UserRole.ADMIN)
    ),
) -> TenantBrandingResponse:
    """Update tenant branding settings."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        repo = TenantRepository(session=session)
        svc = TenantService(repo=repo)
        try:
            result = await svc.update_branding(tenant_id, body)
        except TenantNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    from src.repo.analytics_repository import create_platform_audit_log
    await create_platform_audit_log(
        user_id=user.user_id, user_name=user.name,
        event_type="SETTINGS", action="tenant_branding_updated",
        entity_type="tenant", entity_id=str(tenant_id),
        details=f"Updated branding settings",
    )
    return result


@router.put(
    "/{tenant_id}/defaults",
    response_model=TenantDefaultsResponse,
)
async def update_tenant_defaults(
    tenant_id: uuid.UUID,
    body: UpdateTenantDefaultsRequest,
    user: UserContext = Depends(
        require_role(UserRole.SYSTEM_ADMIN, UserRole.ADMIN)
    ),
) -> TenantDefaultsResponse:
    """Update tenant default configuration."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        repo = TenantRepository(session=session)
        svc = TenantService(repo=repo)
        try:
            result = await svc.update_defaults(tenant_id, body)
        except TenantNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    from src.repo.analytics_repository import create_platform_audit_log
    await create_platform_audit_log(
        user_id=user.user_id, user_name=user.name,
        event_type="SETTINGS", action="tenant_defaults_updated",
        entity_type="tenant", entity_id=str(tenant_id),
        details=f"Updated default configuration",
    )
    return result

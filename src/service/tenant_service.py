"""Tenant settings business logic."""
import logging
import uuid

from src.repo.tenant_repository import TenantNotFoundError, TenantRepository
from src.types.tenant import (
    TenantBrandingResponse,
    TenantDefaultsResponse,
    TenantFullResponse,
    TenantGeneralResponse,
    UpdateTenantBrandingRequest,
    UpdateTenantDefaultsRequest,
    UpdateTenantGeneralRequest,
)

logger = logging.getLogger(__name__)


class TenantServiceError(Exception):
    """Raised when a tenant service operation fails."""


def _to_full_response(tenant: object) -> TenantFullResponse:
    """Map a Tenant ORM object to TenantFullResponse."""
    return TenantFullResponse(
        id=str(tenant.id),  # type: ignore[attr-defined]
        name=tenant.name,  # type: ignore[attr-defined]
        slug=tenant.slug,  # type: ignore[attr-defined]
        logo_url=tenant.logo_url,  # type: ignore[attr-defined]
        timezone=tenant.timezone,  # type: ignore[attr-defined]
        default_language=tenant.default_language,  # type: ignore[attr-defined]
        is_active=tenant.is_active,  # type: ignore[attr-defined]
        primary_color=tenant.primary_color or "#5F2CFF",  # type: ignore[attr-defined]
        favicon_url=tenant.favicon_url,  # type: ignore[attr-defined]
        font_family=tenant.font_family or "Montserrat",  # type: ignore[attr-defined]
        email_signature=tenant.email_signature,  # type: ignore[attr-defined]
    )


def _to_general_response(tenant: object) -> TenantGeneralResponse:
    """Map a Tenant ORM object to TenantGeneralResponse."""
    return TenantGeneralResponse(
        id=str(tenant.id),  # type: ignore[attr-defined]
        name=tenant.name,  # type: ignore[attr-defined]
        slug=tenant.slug,  # type: ignore[attr-defined]
        logo_url=tenant.logo_url,  # type: ignore[attr-defined]
        timezone=tenant.timezone,  # type: ignore[attr-defined]
        default_language=tenant.default_language,  # type: ignore[attr-defined]
        is_active=tenant.is_active,  # type: ignore[attr-defined]
    )


def _to_branding_response(tenant: object) -> TenantBrandingResponse:
    """Map a Tenant ORM object to TenantBrandingResponse."""
    return TenantBrandingResponse(
        primary_color=tenant.primary_color or "#5F2CFF",  # type: ignore[attr-defined]
        favicon_url=tenant.favicon_url,  # type: ignore[attr-defined]
        font_family=tenant.font_family or "Montserrat",  # type: ignore[attr-defined]
        email_signature=tenant.email_signature,  # type: ignore[attr-defined]
    )


class TenantService:
    """Service for tenant settings management."""

    def __init__(self, repo: TenantRepository) -> None:
        """Initialize with a tenant repository."""
        self._repo = repo

    async def get_tenant(self, tenant_id: uuid.UUID) -> TenantFullResponse:
        """Get full tenant settings."""
        tenant = await self._repo.get_by_id(tenant_id)
        return _to_full_response(tenant)

    async def update_general(
        self, tenant_id: uuid.UUID, data: UpdateTenantGeneralRequest,
    ) -> TenantGeneralResponse:
        """Update general settings."""
        update_data = data.model_dump(exclude_none=True)
        tenant = await self._repo.update_general(tenant_id, update_data)
        return _to_general_response(tenant)

    async def update_branding(
        self, tenant_id: uuid.UUID, data: UpdateTenantBrandingRequest,
    ) -> TenantBrandingResponse:
        """Update branding settings."""
        update_data = data.model_dump(exclude_none=True)
        tenant = await self._repo.update_branding(tenant_id, update_data)
        return _to_branding_response(tenant)

    async def update_defaults(
        self, tenant_id: uuid.UUID, data: UpdateTenantDefaultsRequest,
    ) -> TenantDefaultsResponse:
        """Update tenant defaults."""
        return TenantDefaultsResponse(
            default_currency=data.default_currency or "USD",
            standard_roi_period=data.standard_roi_period or "3 Years",
            min_feasibility_threshold=data.min_feasibility_threshold or 65,
            required_ethics_level=(
                data.required_ethics_level or "Level 3 - Enterprise Standard"
            ),
        )

"""Tenant repository — CRUD for tenant settings in platform DB."""
import logging
import uuid
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.repo.platform_models import Tenant

logger = logging.getLogger(__name__)


class TenantNotFoundError(Exception):
    """Raised when a tenant is not found."""


GENERAL_FIELDS = {"name", "timezone", "default_language", "logo_url"}
BRANDING_FIELDS = {"primary_color", "favicon_url", "font_family", "email_signature"}
DEFAULTS_FIELDS = {
    "default_currency", "standard_roi_period",
    "min_feasibility_threshold", "required_ethics_level",
}


def _filter_data(data: dict[str, Any], allowed: set[str]) -> dict[str, Any]:
    """Filter data dict to only include allowed non-None keys."""
    return {k: v for k, v in data.items() if k in allowed and v is not None}


class TenantRepository:
    """Repository for tenant CRUD in the platform database."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize with an async database session."""
        self._session = session

    async def get_by_id(self, tenant_id: uuid.UUID) -> Tenant:
        """Fetch a single tenant by ID."""
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await self._session.execute(stmt)
        tenant = result.scalar_one_or_none()
        if tenant is None:
            raise TenantNotFoundError(f"Tenant {tenant_id} not found")
        return tenant

    async def update_general(
        self, tenant_id: uuid.UUID, data: dict[str, Any],
    ) -> Tenant:
        """Update general settings for a tenant."""
        filtered = _filter_data(data, GENERAL_FIELDS)
        if filtered:
            stmt = update(Tenant).where(Tenant.id == tenant_id).values(**filtered)
            await self._session.execute(stmt)
            await self._session.commit()
        return await self.get_by_id(tenant_id)

    async def update_branding(
        self, tenant_id: uuid.UUID, data: dict[str, Any],
    ) -> Tenant:
        """Update branding settings for a tenant."""
        filtered = _filter_data(data, BRANDING_FIELDS)
        if filtered:
            stmt = update(Tenant).where(Tenant.id == tenant_id).values(**filtered)
            await self._session.execute(stmt)
            await self._session.commit()
        return await self.get_by_id(tenant_id)

    async def update_defaults(
        self, tenant_id: uuid.UUID, data: dict[str, Any],
    ) -> Tenant:
        """Update default configuration for a tenant."""
        filtered = _filter_data(data, DEFAULTS_FIELDS)
        if filtered:
            stmt = update(Tenant).where(Tenant.id == tenant_id).values(**filtered)
            await self._session.execute(stmt)
            await self._session.commit()
        return await self.get_by_id(tenant_id)

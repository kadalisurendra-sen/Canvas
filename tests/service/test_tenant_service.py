"""Tests for TenantService business logic."""
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.repo.tenant_repository import TenantNotFoundError, TenantRepository
from src.service.tenant_service import TenantService
from src.types.tenant import (
    UpdateTenantBrandingRequest,
    UpdateTenantDefaultsRequest,
    UpdateTenantGeneralRequest,
)


def _make_tenant_mock(
    name: str = "Acme Corp",
    slug: str = "acme",
    timezone: str = "UTC",
) -> MagicMock:
    """Create a mock Tenant ORM object."""
    t = MagicMock()
    t.id = uuid.uuid4()
    t.name = name
    t.slug = slug
    t.logo_url = None
    t.timezone = timezone
    t.default_language = "en"
    t.is_active = True
    t.primary_color = "#5F2CFF"
    t.favicon_url = None
    t.font_family = "Montserrat"
    t.email_signature = None
    return t


class TestGetTenant:
    """Tests for get_tenant."""

    @pytest.mark.asyncio
    async def test_returns_full_response(self) -> None:
        tenant = _make_tenant_mock()
        repo = MagicMock(spec=TenantRepository)
        repo.get_by_id = AsyncMock(return_value=tenant)
        svc = TenantService(repo)
        result = await svc.get_tenant(tenant.id)
        assert result.name == "Acme Corp"
        assert result.primary_color == "#5F2CFF"

    @pytest.mark.asyncio
    async def test_not_found_raises(self) -> None:
        repo = MagicMock(spec=TenantRepository)
        repo.get_by_id = AsyncMock(
            side_effect=TenantNotFoundError("not found")
        )
        svc = TenantService(repo)
        with pytest.raises(TenantNotFoundError):
            await svc.get_tenant(uuid.uuid4())


class TestUpdateGeneral:
    """Tests for update_general."""

    @pytest.mark.asyncio
    async def test_updates_name(self) -> None:
        tenant = _make_tenant_mock(name="New Name")
        repo = MagicMock(spec=TenantRepository)
        repo.update_general = AsyncMock(return_value=tenant)
        svc = TenantService(repo)
        req = UpdateTenantGeneralRequest(name="New Name")
        result = await svc.update_general(tenant.id, req)
        assert result.name == "New Name"

    @pytest.mark.asyncio
    async def test_updates_timezone(self) -> None:
        tenant = _make_tenant_mock(timezone="US/Pacific")
        repo = MagicMock(spec=TenantRepository)
        repo.update_general = AsyncMock(return_value=tenant)
        svc = TenantService(repo)
        req = UpdateTenantGeneralRequest(timezone="US/Pacific")
        result = await svc.update_general(tenant.id, req)
        assert result.timezone == "US/Pacific"


class TestUpdateBranding:
    """Tests for update_branding."""

    @pytest.mark.asyncio
    async def test_updates_color(self) -> None:
        tenant = _make_tenant_mock()
        tenant.primary_color = "#FF0000"
        repo = MagicMock(spec=TenantRepository)
        repo.update_branding = AsyncMock(return_value=tenant)
        svc = TenantService(repo)
        req = UpdateTenantBrandingRequest(primary_color="#FF0000")
        result = await svc.update_branding(tenant.id, req)
        assert result.primary_color == "#FF0000"

    @pytest.mark.asyncio
    async def test_updates_font(self) -> None:
        tenant = _make_tenant_mock()
        tenant.font_family = "Inter"
        repo = MagicMock(spec=TenantRepository)
        repo.update_branding = AsyncMock(return_value=tenant)
        svc = TenantService(repo)
        req = UpdateTenantBrandingRequest(font_family="Inter")
        result = await svc.update_branding(tenant.id, req)
        assert result.font_family == "Inter"


class TestUpdateDefaults:
    """Tests for update_defaults."""

    @pytest.mark.asyncio
    async def test_returns_defaults(self) -> None:
        repo = MagicMock(spec=TenantRepository)
        svc = TenantService(repo)
        req = UpdateTenantDefaultsRequest(
            default_currency="EUR",
            min_feasibility_threshold=80,
        )
        result = await svc.update_defaults(uuid.uuid4(), req)
        assert result.default_currency == "EUR"
        assert result.min_feasibility_threshold == 80

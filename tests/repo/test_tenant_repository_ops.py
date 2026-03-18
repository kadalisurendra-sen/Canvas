"""Tests for TenantRepository async methods and _filter_data."""
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.repo.tenant_repository import (
    BRANDING_FIELDS,
    GENERAL_FIELDS,
    TenantNotFoundError,
    TenantRepository,
    _filter_data,
)


class TestFilterData:
    """Tests for _filter_data helper."""

    def test_filters_allowed_keys(self) -> None:
        data = {"name": "Acme", "timezone": "UTC", "extra": "nope"}
        result = _filter_data(data, GENERAL_FIELDS)
        assert "name" in result
        assert "timezone" in result
        assert "extra" not in result

    def test_excludes_none_values(self) -> None:
        data = {"name": "Acme", "timezone": None}
        result = _filter_data(data, GENERAL_FIELDS)
        assert "name" in result
        assert "timezone" not in result

    def test_empty_data(self) -> None:
        result = _filter_data({}, GENERAL_FIELDS)
        assert result == {}

    def test_branding_fields(self) -> None:
        data = {
            "primary_color": "#FF0000",
            "favicon_url": "http://example.com/fav.ico",
            "name": "should_not_appear",
        }
        result = _filter_data(data, BRANDING_FIELDS)
        assert "primary_color" in result
        assert "favicon_url" in result
        assert "name" not in result


class TestTenantRepositoryGetById:
    """Tests for TenantRepository.get_by_id."""

    @pytest.mark.asyncio
    async def test_returns_tenant(self) -> None:
        mock_tenant = MagicMock()
        mock_tenant.id = uuid.uuid4()
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_tenant
        session.execute.return_value = result_mock

        repo = TenantRepository(session=session)
        tenant = await repo.get_by_id(mock_tenant.id)
        assert tenant is mock_tenant

    @pytest.mark.asyncio
    async def test_raises_not_found(self) -> None:
        session = AsyncMock()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        repo = TenantRepository(session=session)
        with pytest.raises(TenantNotFoundError):
            await repo.get_by_id(uuid.uuid4())


class TestTenantRepositoryUpdateGeneral:
    """Tests for TenantRepository.update_general."""

    @pytest.mark.asyncio
    async def test_updates_with_valid_data(self) -> None:
        tenant_id = uuid.uuid4()
        mock_tenant = MagicMock()
        mock_tenant.id = tenant_id
        session = AsyncMock()
        # First call for update, second for get_by_id
        result_get = MagicMock()
        result_get.scalar_one_or_none.return_value = mock_tenant
        session.execute.return_value = result_get

        repo = TenantRepository(session=session)
        result = await repo.update_general(
            tenant_id, {"name": "New Name", "timezone": "US/Pacific"}
        )
        assert result is mock_tenant

    @pytest.mark.asyncio
    async def test_skips_update_when_no_valid_fields(self) -> None:
        tenant_id = uuid.uuid4()
        mock_tenant = MagicMock()
        mock_tenant.id = tenant_id
        session = AsyncMock()
        result_get = MagicMock()
        result_get.scalar_one_or_none.return_value = mock_tenant
        session.execute.return_value = result_get

        repo = TenantRepository(session=session)
        result = await repo.update_general(tenant_id, {"invalid_key": "val"})
        assert result is mock_tenant
        # commit should not be called if no valid fields
        session.commit.assert_not_awaited()


class TestTenantRepositoryUpdateBranding:
    """Tests for TenantRepository.update_branding."""

    @pytest.mark.asyncio
    async def test_updates_branding(self) -> None:
        tenant_id = uuid.uuid4()
        mock_tenant = MagicMock()
        mock_tenant.id = tenant_id
        session = AsyncMock()
        result_get = MagicMock()
        result_get.scalar_one_or_none.return_value = mock_tenant
        session.execute.return_value = result_get

        repo = TenantRepository(session=session)
        result = await repo.update_branding(
            tenant_id, {"primary_color": "#FF0000"}
        )
        assert result is mock_tenant

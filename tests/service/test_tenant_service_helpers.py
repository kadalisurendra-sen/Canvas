"""Tests for tenant service helper functions and edge cases."""
import uuid
from unittest.mock import MagicMock

import pytest

from src.service.tenant_service import (
    TenantServiceError,
    _to_branding_response,
    _to_full_response,
    _to_general_response,
)


def _make_tenant(
    primary_color: str | None = "#5F2CFF",
    font_family: str | None = "Montserrat",
) -> MagicMock:
    t = MagicMock()
    t.id = uuid.uuid4()
    t.name = "Acme"
    t.slug = "acme"
    t.logo_url = "http://example.com/logo.png"
    t.timezone = "UTC"
    t.default_language = "en"
    t.is_active = True
    t.primary_color = primary_color
    t.favicon_url = "http://example.com/fav.ico"
    t.font_family = font_family
    t.email_signature = "Best regards"
    return t


class TestToFullResponse:
    """Tests for _to_full_response."""

    def test_maps_all_fields(self) -> None:
        tenant = _make_tenant()
        result = _to_full_response(tenant)
        assert result.name == "Acme"
        assert result.primary_color == "#5F2CFF"
        assert result.font_family == "Montserrat"

    def test_defaults_when_none(self) -> None:
        tenant = _make_tenant(primary_color=None, font_family=None)
        result = _to_full_response(tenant)
        assert result.primary_color == "#5F2CFF"
        assert result.font_family == "Montserrat"


class TestToGeneralResponse:
    """Tests for _to_general_response."""

    def test_maps_general_fields(self) -> None:
        tenant = _make_tenant()
        result = _to_general_response(tenant)
        assert result.name == "Acme"
        assert result.slug == "acme"
        assert result.timezone == "UTC"
        assert result.is_active is True


class TestToBrandingResponse:
    """Tests for _to_branding_response."""

    def test_maps_branding_fields(self) -> None:
        tenant = _make_tenant()
        result = _to_branding_response(tenant)
        assert result.primary_color == "#5F2CFF"
        assert result.font_family == "Montserrat"
        assert result.email_signature == "Best regards"

    def test_defaults_when_none(self) -> None:
        tenant = _make_tenant(primary_color=None, font_family=None)
        result = _to_branding_response(tenant)
        assert result.primary_color == "#5F2CFF"
        assert result.font_family == "Montserrat"


class TestTenantServiceError:
    """Tests for TenantServiceError."""

    def test_is_exception(self) -> None:
        err = TenantServiceError("test error")
        assert isinstance(err, Exception)
        assert str(err) == "test error"

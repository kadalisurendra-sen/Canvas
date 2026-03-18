"""Tests for tenant type schemas."""
from src.types.tenant import (
    TenantBrandingResponse,
    TenantDefaultsResponse,
    TenantFullResponse,
    TenantGeneralResponse,
    UpdateTenantBrandingRequest,
    UpdateTenantDefaultsRequest,
    UpdateTenantGeneralRequest,
)


class TestTenantGeneralResponse:
    """Tests for TenantGeneralResponse schema."""

    def test_defaults(self) -> None:
        resp = TenantGeneralResponse(
            id="t1", name="Acme", slug="acme"
        )
        assert resp.timezone == "UTC"
        assert resp.default_language == "en"
        assert resp.is_active is True

    def test_custom_values(self) -> None:
        resp = TenantGeneralResponse(
            id="t1", name="Acme", slug="acme",
            timezone="US/Eastern", default_language="es",
        )
        assert resp.timezone == "US/Eastern"


class TestTenantBrandingResponse:
    """Tests for TenantBrandingResponse schema."""

    def test_defaults(self) -> None:
        resp = TenantBrandingResponse()
        assert resp.primary_color == "#5F2CFF"
        assert resp.font_family == "Montserrat"
        assert resp.favicon_url is None
        assert resp.email_signature is None


class TestTenantDefaultsResponse:
    """Tests for TenantDefaultsResponse schema."""

    def test_defaults(self) -> None:
        resp = TenantDefaultsResponse()
        assert resp.default_currency == "USD"
        assert resp.min_feasibility_threshold == 65

    def test_custom_values(self) -> None:
        resp = TenantDefaultsResponse(
            default_currency="EUR",
            min_feasibility_threshold=80,
        )
        assert resp.default_currency == "EUR"


class TestTenantFullResponse:
    """Tests for TenantFullResponse schema."""

    def test_includes_defaults(self) -> None:
        resp = TenantFullResponse(
            id="t1", name="Acme", slug="acme"
        )
        assert resp.defaults.default_currency == "USD"


class TestUpdateTenantGeneralRequest:
    """Tests for UpdateTenantGeneralRequest schema."""

    def test_all_optional(self) -> None:
        req = UpdateTenantGeneralRequest()
        assert req.name is None
        assert req.timezone is None

    def test_partial_update(self) -> None:
        req = UpdateTenantGeneralRequest(name="New Name")
        assert req.name == "New Name"
        assert req.timezone is None


class TestUpdateTenantBrandingRequest:
    """Tests for UpdateTenantBrandingRequest schema."""

    def test_all_optional(self) -> None:
        req = UpdateTenantBrandingRequest()
        assert req.primary_color is None

    def test_set_color(self) -> None:
        req = UpdateTenantBrandingRequest(primary_color="#FF0000")
        assert req.primary_color == "#FF0000"


class TestUpdateTenantDefaultsRequest:
    """Tests for UpdateTenantDefaultsRequest schema."""

    def test_all_optional(self) -> None:
        req = UpdateTenantDefaultsRequest()
        assert req.default_currency is None

    def test_set_threshold(self) -> None:
        req = UpdateTenantDefaultsRequest(min_feasibility_threshold=75)
        assert req.min_feasibility_threshold == 75

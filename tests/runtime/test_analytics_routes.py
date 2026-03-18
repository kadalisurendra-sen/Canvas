"""Tests for analytics API routes."""
import uuid

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.runtime.app import create_app
from src.runtime.dependencies.auth import get_current_user
from src.runtime.routes.analytics import _parse_date, router as analytics_router
from src.types.auth import UserContext
from src.types.enums import UserRole


def _make_test_app():
    """Create a lightweight app with auth dependency overridden (no middleware)."""
    application = FastAPI()
    application.include_router(analytics_router)
    fake_user = UserContext(
        user_id=uuid.uuid4(),
        email="test@example.com",
        name="Test User",
        roles=[UserRole.ADMIN],
        tenant_id=uuid.uuid4(),
    )
    application.dependency_overrides[get_current_user] = lambda: fake_user
    return application


class TestParseDate:
    """Tests for _parse_date helper."""

    def test_valid_iso_date(self) -> None:
        result = _parse_date("2026-03-15")
        assert result is not None
        assert result.year == 2026
        assert result.month == 3

    def test_valid_iso_datetime(self) -> None:
        result = _parse_date("2026-03-15T12:30:00")
        assert result is not None
        assert result.hour == 12

    def test_none_input(self) -> None:
        assert _parse_date(None) is None

    def test_empty_string(self) -> None:
        assert _parse_date("") is None

    def test_invalid_format(self) -> None:
        assert _parse_date("not-a-date") is None

    def test_partial_date(self) -> None:
        # "2026-13-01" is invalid month
        assert _parse_date("2026-13-01") is None


class TestAnalyticsRouteRegistration:
    """Verify analytics routes are registered."""

    def _get_routes(self) -> list[str]:
        application = create_app()
        return [route.path for route in application.routes]

    def test_dashboard_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/analytics/dashboard" in routes

    def test_top_users_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/analytics/top-users" in routes

    def test_audit_logs_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/analytics/audit-logs" in routes

    def test_export_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/analytics/export" in routes

    def test_audit_export_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/analytics/audit-logs/export" in routes


class TestDashboardEndpoint:
    """Tests for dashboard HTTP endpoint."""

    @pytest.mark.asyncio
    async def test_get_dashboard_ok(self) -> None:
        test_app = _make_test_app()
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/analytics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        assert "stage_distribution" in data

    @pytest.mark.asyncio
    async def test_get_dashboard_with_dates(self) -> None:
        test_app = _make_test_app()
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get(
                "/api/v1/analytics/dashboard",
                params={"from": "2026-01-01", "to": "2026-06-30"},
            )
        assert response.status_code == 200


class TestTopUsersEndpoint:
    """Tests for top users HTTP endpoint."""

    @pytest.mark.asyncio
    async def test_get_top_users_ok(self) -> None:
        test_app = _make_test_app()
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/analytics/top-users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


class TestExportEndpoint:
    """Tests for CSV export endpoints."""

    @pytest.mark.asyncio
    async def test_export_dashboard_csv(self) -> None:
        test_app = _make_test_app()
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/v1/analytics/export")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "attachment" in response.headers.get("content-disposition", "")

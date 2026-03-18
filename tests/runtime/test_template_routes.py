"""Tests for template API routes — registration verification."""
import pytest

from src.runtime.app import app


class TestTemplateRouteRegistration:
    """Verify all template routes are registered on the FastAPI app."""

    def _get_routes(self) -> list[str]:
        """Extract all route paths from the FastAPI app."""
        return [route.path for route in app.routes]

    def test_list_templates_registered(self) -> None:
        """GET /api/v1/templates route exists."""
        routes = self._get_routes()
        assert "/api/v1/templates" in routes

    def test_create_template_registered(self) -> None:
        """POST /api/v1/templates route exists."""
        routes = self._get_routes()
        assert "/api/v1/templates" in routes

    def test_get_template_registered(self) -> None:
        """GET /api/v1/templates/{template_id} route exists."""
        routes = self._get_routes()
        assert "/api/v1/templates/{template_id}" in routes

    def test_update_template_registered(self) -> None:
        """PUT /api/v1/templates/{template_id} route exists."""
        routes = self._get_routes()
        assert "/api/v1/templates/{template_id}" in routes

    def test_delete_template_registered(self) -> None:
        """DELETE /api/v1/templates/{template_id} route exists."""
        routes = self._get_routes()
        assert "/api/v1/templates/{template_id}" in routes

    def test_stages_route_registered(self) -> None:
        """PUT /api/v1/templates/{template_id}/stages route exists."""
        routes = self._get_routes()
        assert "/api/v1/templates/{template_id}/stages" in routes

    def test_fields_route_registered(self) -> None:
        """PUT /api/v1/templates/{template_id}/fields route exists."""
        routes = self._get_routes()
        assert "/api/v1/templates/{template_id}/fields" in routes

    def test_scoring_route_registered(self) -> None:
        """PUT /api/v1/templates/{template_id}/scoring route exists."""
        routes = self._get_routes()
        assert "/api/v1/templates/{template_id}/scoring" in routes

    def test_publish_route_registered(self) -> None:
        """POST /api/v1/templates/{template_id}/publish route exists."""
        routes = self._get_routes()
        assert "/api/v1/templates/{template_id}/publish" in routes


class TestRouteMethodConstraints:
    """Verify routes accept the correct HTTP methods."""

    def _get_route_methods(self, path: str) -> set[str]:
        """Get allowed methods for a specific path."""
        methods: set[str] = set()
        for route in app.routes:
            if hasattr(route, "path") and route.path == path:
                if hasattr(route, "methods"):
                    methods.update(route.methods)
        return methods

    def test_templates_list_accepts_get(self) -> None:
        """Templates list accepts GET."""
        methods = self._get_route_methods("/api/v1/templates")
        assert "GET" in methods

    def test_templates_create_accepts_post(self) -> None:
        """Templates create accepts POST."""
        methods = self._get_route_methods("/api/v1/templates")
        assert "POST" in methods

    def test_template_delete_accepts_delete(self) -> None:
        """Template detail accepts DELETE."""
        methods = self._get_route_methods("/api/v1/templates/{template_id}")
        assert "DELETE" in methods

    def test_publish_accepts_post(self) -> None:
        """Publish accepts POST."""
        methods = self._get_route_methods("/api/v1/templates/{template_id}/publish")
        assert "POST" in methods

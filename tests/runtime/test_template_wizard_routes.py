"""Tests for template wizard API route registration."""
import pytest

from src.runtime.app import app


class TestWizardRouteRegistration:
    """Verify template wizard routes are registered."""

    def _get_routes(self) -> list[str]:
        return [route.path for route in app.routes]

    def test_stages_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/templates/{template_id}/stages" in routes

    def test_fields_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/templates/{template_id}/fields" in routes

    def test_scoring_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/templates/{template_id}/scoring" in routes

    def test_publish_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/templates/{template_id}/publish" in routes


class TestWizardRouteMethods:
    """Verify correct HTTP methods for wizard routes."""

    def _get_route_methods(self, path: str) -> set[str]:
        methods: set[str] = set()
        for route in app.routes:
            if hasattr(route, "path") and route.path == path:
                if hasattr(route, "methods"):
                    methods.update(route.methods)
        return methods

    def test_stages_accepts_put(self) -> None:
        methods = self._get_route_methods("/api/v1/templates/{template_id}/stages")
        assert "PUT" in methods

    def test_fields_accepts_put(self) -> None:
        methods = self._get_route_methods("/api/v1/templates/{template_id}/fields")
        assert "PUT" in methods

    def test_scoring_accepts_put(self) -> None:
        methods = self._get_route_methods("/api/v1/templates/{template_id}/scoring")
        assert "PUT" in methods

    def test_publish_accepts_post(self) -> None:
        methods = self._get_route_methods("/api/v1/templates/{template_id}/publish")
        assert "POST" in methods

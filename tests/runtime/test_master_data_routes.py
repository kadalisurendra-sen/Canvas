"""Tests for master data API route registration."""
import pytest

from src.runtime.app import app


class TestMasterDataRouteRegistration:
    """Verify master data routes are registered."""

    def _get_routes(self) -> list[str]:
        return [route.path for route in app.routes]

    def test_categories_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/master-data/categories" in routes

    def test_values_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/master-data/categories/{cat_id}/values" in routes

    def test_update_value_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/master-data/values/{value_id}" in routes

    def test_reorder_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/master-data/categories/{cat_id}/reorder" in routes

    def test_import_route(self) -> None:
        routes = self._get_routes()
        assert "/api/v1/master-data/categories/{cat_id}/import" in routes


class TestMasterDataRouteMethods:
    """Verify correct HTTP methods."""

    def _get_route_methods(self, path: str) -> set[str]:
        methods: set[str] = set()
        for route in app.routes:
            if hasattr(route, "path") and route.path == path:
                if hasattr(route, "methods"):
                    methods.update(route.methods)
        return methods

    def test_categories_get(self) -> None:
        methods = self._get_route_methods("/api/v1/master-data/categories")
        assert "GET" in methods

    def test_values_get_and_post(self) -> None:
        methods = self._get_route_methods(
            "/api/v1/master-data/categories/{cat_id}/values"
        )
        assert "GET" in methods
        assert "POST" in methods

    def test_value_put_and_delete(self) -> None:
        methods = self._get_route_methods("/api/v1/master-data/values/{value_id}")
        assert "PUT" in methods
        assert "DELETE" in methods

    def test_reorder_put(self) -> None:
        methods = self._get_route_methods(
            "/api/v1/master-data/categories/{cat_id}/reorder"
        )
        assert "PUT" in methods

    def test_import_post(self) -> None:
        methods = self._get_route_methods(
            "/api/v1/master-data/categories/{cat_id}/import"
        )
        assert "POST" in methods

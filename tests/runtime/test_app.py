"""Tests for FastAPI application factory."""
import pytest

from src.runtime.app import app, create_app


class TestCreateApp:
    """Tests for create_app function."""

    def test_returns_fastapi_instance(self) -> None:
        from fastapi import FastAPI
        assert isinstance(app, FastAPI)

    def test_app_title(self) -> None:
        assert app.title == "Helio Canvas"

    def test_docs_url(self) -> None:
        assert app.docs_url == "/api/docs"

    def test_redoc_url(self) -> None:
        assert app.redoc_url == "/api/redoc"

    def test_routes_registered(self) -> None:
        paths = [route.path for route in app.routes]
        assert "/api/v1/health" in paths
        assert "/api/v1/auth/login" in paths
        assert "/api/v1/users" in paths

    def test_create_app_returns_new_instance(self) -> None:
        new_app = create_app()
        from fastapi import FastAPI
        assert isinstance(new_app, FastAPI)

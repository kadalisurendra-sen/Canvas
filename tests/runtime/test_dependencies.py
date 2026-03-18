"""Tests for FastAPI auth dependencies."""
import pytest
from fastapi import FastAPI, Depends
from httpx import ASGITransport, AsyncClient

from src.runtime.dependencies.auth import (
    get_current_user,
    require_role,
    _extract_token,
)
from src.types.auth import UserContext
from src.types.enums import UserRole


def _create_app_with_protected_route() -> FastAPI:
    """Create a test app with a protected route."""
    test_app = FastAPI()

    @test_app.get("/protected")
    async def protected(
        user: UserContext = Depends(get_current_user),
    ) -> dict[str, str]:
        return {"user_id": str(user.user_id)}

    return test_app


@pytest.mark.asyncio
async def test_no_token_returns_401(monkeypatch: pytest.MonkeyPatch) -> None:
    """Protected route without token returns 401."""
    monkeypatch.setenv("AUTH_MODE", "keycloak")
    from src.config.settings import get_settings
    get_settings.cache_clear()
    app = _create_app_with_protected_route()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/protected")
    assert response.status_code == 401
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_invalid_bearer_returns_401(monkeypatch: pytest.MonkeyPatch) -> None:
    """Protected route with invalid bearer token returns 401."""
    monkeypatch.setenv("AUTH_MODE", "keycloak")
    from src.config.settings import get_settings
    get_settings.cache_clear()
    app = _create_app_with_protected_route()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/protected",
            headers={"Authorization": "Bearer garbage"},
        )
    assert response.status_code == 401
    get_settings.cache_clear()


class TestExtractToken:
    """Tests for the _extract_token helper."""

    def test_extract_from_bearer_header(self) -> None:
        from unittest.mock import MagicMock
        request = MagicMock()
        request.headers = {"Authorization": "Bearer mytoken123"}
        request.cookies = {}
        assert _extract_token(request) == "mytoken123"

    def test_extract_from_cookie(self) -> None:
        from unittest.mock import MagicMock
        request = MagicMock()
        request.headers = {}
        request.cookies = {"access_token": "cookie-token"}
        assert _extract_token(request) == "cookie-token"

    def test_returns_empty_when_no_token(self) -> None:
        from unittest.mock import MagicMock
        request = MagicMock()
        request.headers = {}
        request.cookies = {}
        assert _extract_token(request) == ""

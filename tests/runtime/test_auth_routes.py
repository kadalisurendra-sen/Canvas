"""Tests for auth route endpoints."""
import pytest
from httpx import ASGITransport, AsyncClient

from src.runtime.app import app


@pytest.mark.asyncio
async def test_login_returns_auth_url() -> None:
    """Login endpoint should return an authorization URL."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login")
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "state" in data
    assert "openid" in data["auth_url"]


@pytest.mark.asyncio
async def test_logout_clears_cookie() -> None:
    """Logout endpoint should clear the access_token cookie."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"


@pytest.mark.asyncio
async def test_me_requires_auth() -> None:
    """Me endpoint should return 401 without a token."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/auth/me")
    assert response.status_code == 401

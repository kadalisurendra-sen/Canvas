"""Tests for the health check endpoint."""
import pytest
from httpx import ASGITransport, AsyncClient

from src.runtime.app import app


@pytest.mark.asyncio
async def test_health_returns_200() -> None:
    """Health endpoint should return 200 with status ok."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_returns_json() -> None:
    """Health endpoint should return application/json content type."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert "application/json" in response.headers["content-type"]

"""Tests for tenant resolver middleware."""
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import FastAPI, Request

from src.runtime.middleware.tenant_resolver import TenantResolverMiddleware
from src.service.auth_service import AuthService


def _create_test_app(auth_service: AuthService) -> FastAPI:
    """Create a minimal FastAPI app with tenant resolver middleware."""
    test_app = FastAPI()
    test_app.add_middleware(
        TenantResolverMiddleware, auth_service=auth_service
    )

    @test_app.get("/api/v1/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @test_app.get("/api/v1/protected")
    async def protected(request: Request) -> dict[str, str]:
        return {"tenant": getattr(request.state, "tenant_id", "")}

    return test_app


@pytest.mark.asyncio
async def test_skip_health_endpoint() -> None:
    """Health endpoint should bypass middleware."""
    svc = AuthService()
    app = _create_test_app(svc)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_missing_token_returns_401() -> None:
    """Protected endpoint without token should return 401."""
    svc = AuthService()
    app = _create_test_app(svc)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/protected")
    assert response.status_code == 401
    assert "Missing authentication token" in response.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_token_returns_401() -> None:
    """Protected endpoint with bad token should return 401."""
    svc = AuthService()
    svc.set_jwks({"keys": []})
    app = _create_test_app(svc)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/protected",
            headers={"Authorization": "Bearer bad.token.here"},
        )
    assert response.status_code == 401

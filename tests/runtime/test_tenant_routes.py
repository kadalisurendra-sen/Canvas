"""Tests for tenant settings API routes."""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from src.runtime.app import app


@pytest.mark.asyncio
async def test_get_tenant_requires_auth() -> None:
    """Unauthenticated request to get tenant should return 401."""
    transport = ASGITransport(app=app)
    tenant_id = uuid.uuid4()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/tenants/{tenant_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_tenant_general_requires_auth() -> None:
    """Unauthenticated update should return 401."""
    transport = ASGITransport(app=app)
    tenant_id = uuid.uuid4()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put(
            f"/api/v1/tenants/{tenant_id}",
            json={"name": "New Name"},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_branding_requires_auth() -> None:
    """Unauthenticated branding update should return 401."""
    transport = ASGITransport(app=app)
    tenant_id = uuid.uuid4()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put(
            f"/api/v1/tenants/{tenant_id}/branding",
            json={"primary_color": "#FF0000"},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_defaults_requires_auth() -> None:
    """Unauthenticated defaults update should return 401."""
    transport = ASGITransport(app=app)
    tenant_id = uuid.uuid4()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.put(
            f"/api/v1/tenants/{tenant_id}/defaults",
            json={"default_currency": "EUR"},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_tenant_invalid_uuid() -> None:
    """Invalid UUID should return 401 (auth checked first) or 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/tenants/not-a-uuid")
    # Auth check runs before path validation
    assert response.status_code in (401, 422)

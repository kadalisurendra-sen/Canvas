"""Tenant settings API routes."""
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException

from src.runtime.dependencies.auth import get_current_user, require_role
from src.repo.tenant_repository import TenantNotFoundError, TenantRepository
from src.repo.database import create_platform_engine
from src.service.tenant_service import TenantService
from src.types.auth import UserContext
from src.types.enums import UserRole
from src.types.tenant import (
    TenantBrandingResponse,
    TenantDefaultsResponse,
    TenantFullResponse,
    TenantGeneralResponse,
    UpdateTenantBrandingRequest,
    UpdateTenantDefaultsRequest,
    UpdateTenantGeneralRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tenants", tags=["tenants"])


async def _get_tenant_service() -> TenantService:
    """Build a TenantService with a platform DB session."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        repo = TenantRepository(session=session)
        return TenantService(repo=repo)


@router.get("/{tenant_id}", response_model=TenantFullResponse)
async def get_tenant(
    tenant_id: uuid.UUID,
    user: UserContext = Depends(get_current_user),
) -> TenantFullResponse:
    """Get tenant settings."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        repo = TenantRepository(session=session)
        svc = TenantService(repo=repo)
        try:
            return await svc.get_tenant(tenant_id)
        except TenantNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{tenant_id}", response_model=TenantGeneralResponse)
async def update_tenant_general(
    tenant_id: uuid.UUID,
    body: UpdateTenantGeneralRequest,
    user: UserContext = Depends(
        require_role(UserRole.SYSTEM_ADMIN, UserRole.ADMIN)
    ),
) -> TenantGeneralResponse:
    """Update tenant general settings."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        repo = TenantRepository(session=session)
        svc = TenantService(repo=repo)
        try:
            return await svc.update_general(tenant_id, body)
        except TenantNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put(
    "/{tenant_id}/branding",
    response_model=TenantBrandingResponse,
)
async def update_tenant_branding(
    tenant_id: uuid.UUID,
    body: UpdateTenantBrandingRequest,
    user: UserContext = Depends(
        require_role(UserRole.SYSTEM_ADMIN, UserRole.ADMIN)
    ),
) -> TenantBrandingResponse:
    """Update tenant branding settings."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        repo = TenantRepository(session=session)
        svc = TenantService(repo=repo)
        try:
            return await svc.update_branding(tenant_id, body)
        except TenantNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put(
    "/{tenant_id}/defaults",
    response_model=TenantDefaultsResponse,
)
async def update_tenant_defaults(
    tenant_id: uuid.UUID,
    body: UpdateTenantDefaultsRequest,
    user: UserContext = Depends(
        require_role(UserRole.SYSTEM_ADMIN, UserRole.ADMIN)
    ),
) -> TenantDefaultsResponse:
    """Update tenant default configuration."""
    _, session_factory = create_platform_engine()
    async with session_factory() as session:
        repo = TenantRepository(session=session)
        svc = TenantService(repo=repo)
        try:
            return await svc.update_defaults(tenant_id, body)
        except TenantNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

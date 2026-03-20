"""Master data management API routes."""
import logging
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File

from src.runtime.dependencies.auth import get_current_user
from src.runtime.dependencies.db import get_tenant_session
from src.repo.analytics_repository import create_audit_log
from src.service import master_data_service as svc
from src.types.auth import UserContext
from src.types.master_data import (
    CategoryOut,
    ImportResult,
    PaginatedValues,
    ReorderRequest,
    ValueCreate,
    ValueOut,
    ValueUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/master-data", tags=["master-data"])

MAX_CSV_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(
    request: Request,
    user_context: UserContext = Depends(get_current_user),
) -> list[CategoryOut]:
    """List all master data categories with item counts."""
    async with get_tenant_session(request) as session:
        return await svc.get_categories(session)


@router.get(
    "/categories/{cat_id}/values",
    response_model=PaginatedValues,
)
async def list_values(
    request: Request,
    cat_id: uuid.UUID,
    search: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user_context: UserContext = Depends(get_current_user),
) -> PaginatedValues:
    """List paginated values for a category."""
    async with get_tenant_session(request) as session:
        return await svc.get_values(
            session, cat_id, search, page, page_size
        )


@router.post(
    "/categories/{cat_id}/values",
    response_model=ValueOut,
    status_code=201,
)
async def create_value(
    request: Request,
    cat_id: uuid.UUID,
    body: ValueCreate,
    user_context: UserContext = Depends(get_current_user),
) -> ValueOut:
    """Create a new value in a category."""
    async with get_tenant_session(request) as session:
        result = await svc.create_value(session, cat_id, body)
        ip = request.client.host if request.client else None
        await create_audit_log(
            session, user_context.user_id, user_context.name,
            "DATA", "value_created",
            details=f"Created value '{body.value}' in category {cat_id}",
            ip_address=ip,
        )
        await session.commit()
        return result


@router.put("/values/{value_id}", response_model=ValueOut)
async def update_value(
    request: Request,
    value_id: uuid.UUID,
    body: ValueUpdate,
    user_context: UserContext = Depends(get_current_user),
) -> ValueOut:
    """Update an existing master data value."""
    async with get_tenant_session(request) as session:
        result = await svc.update_value(session, value_id, body)
        if not result:
            raise HTTPException(status_code=404, detail="Value not found")
        ip = request.client.host if request.client else None
        await create_audit_log(
            session, user_context.user_id, user_context.name,
            "DATA", "value_updated",
            details=f"Updated value {value_id}",
            ip_address=ip,
        )
        await session.commit()
        return result


@router.delete("/values/{value_id}", status_code=204)
async def delete_value(
    request: Request,
    value_id: uuid.UUID,
    user_context: UserContext = Depends(get_current_user),
) -> None:
    """Delete a master data value."""
    async with get_tenant_session(request) as session:
        deleted = await svc.delete_value(session, value_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Value not found")
        ip = request.client.host if request.client else None
        await create_audit_log(
            session, user_context.user_id, user_context.name,
            "DATA", "value_deleted",
            details=f"Deleted value {value_id}",
            ip_address=ip,
        )
        await session.commit()


@router.put("/categories/{cat_id}/reorder", status_code=200)
async def reorder_values(
    request: Request,
    cat_id: uuid.UUID,
    body: ReorderRequest,
    user_context: UserContext = Depends(get_current_user),
) -> dict[str, str]:
    """Reorder values within a category."""
    async with get_tenant_session(request) as session:
        await svc.reorder_values(session, cat_id, body.value_ids)
        ip = request.client.host if request.client else None
        await create_audit_log(
            session, user_context.user_id, user_context.name,
            "DATA", "values_reordered",
            details=f"Reordered values in category {cat_id}",
            ip_address=ip,
        )
        await session.commit()
        return {"status": "ok"}


@router.post(
    "/categories/{cat_id}/import",
    response_model=ImportResult,
)
async def import_csv(
    request: Request,
    cat_id: uuid.UUID,
    file: UploadFile = File(...),
    user_context: UserContext = Depends(get_current_user),
) -> ImportResult:
    """Import values from a CSV file."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files accepted")
    content = await file.read()
    if len(content) > MAX_CSV_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"CSV file exceeds maximum size of {MAX_CSV_SIZE_BYTES // (1024 * 1024)}MB",
        )
    async with get_tenant_session(request) as session:
        result = await svc.import_csv(session, cat_id, content)
        ip = request.client.host if request.client else None
        await create_audit_log(
            session, user_context.user_id, user_context.name,
            "DATA", "csv_imported",
            details=f"Imported CSV to category {cat_id}: {result.imported} added, {result.skipped} skipped",
            ip_address=ip,
        )
        await session.commit()
        return result

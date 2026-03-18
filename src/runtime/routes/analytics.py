"""Analytics and audit log API routes."""
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from src.runtime.dependencies.auth import get_current_user
from src.runtime.dependencies.db import get_tenant_session
from src.service import analytics_service as svc
from src.types.analytics import (
    DashboardData,
    PaginatedAuditLogs,
    TopUser,
)
from src.types.auth import UserContext

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard(
    from_date: Optional[str] = Query(default=None, alias="from"),
    to_date: Optional[str] = Query(default=None, alias="to"),
    user_context: UserContext = Depends(get_current_user),
) -> DashboardData:
    """Return analytics dashboard metrics and chart data."""
    fd = _parse_date(from_date)
    td = _parse_date(to_date)
    return await svc.get_dashboard(fd, td)


@router.get("/top-users", response_model=list[TopUser])
async def get_top_users(
    user_context: UserContext = Depends(get_current_user),
) -> list[TopUser]:
    """Return top users by activity."""
    return await svc.get_top_users()


@router.get("/audit-logs", response_model=PaginatedAuditLogs)
async def get_audit_logs(
    request: Request,
    user_id: Optional[uuid.UUID] = Query(default=None),
    action: Optional[str] = Query(default=None),
    event_type: Optional[str] = Query(default=None),
    from_date: Optional[str] = Query(default=None),
    to_date: Optional[str] = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user_context: UserContext = Depends(get_current_user),
) -> PaginatedAuditLogs:
    """Return paginated audit logs with filters."""
    fd = _parse_date(from_date)
    td = _parse_date(to_date)
    async with get_tenant_session(request) as session:
        return await svc.get_audit_logs(
            session, user_id, action, event_type,
            fd, td, page, page_size,
        )


@router.get("/export")
async def export_dashboard(
    from_date: Optional[str] = Query(default=None, alias="from"),
    to_date: Optional[str] = Query(default=None, alias="to"),
    user_context: UserContext = Depends(get_current_user),
) -> StreamingResponse:
    """Export analytics report as CSV download."""
    fd = _parse_date(from_date)
    td = _parse_date(to_date)
    csv_content = await svc.export_dashboard_csv(fd, td)
    today = datetime.utcnow().strftime("%Y%m%d")
    filename = f"analytics_report_{today}.csv"
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/audit-logs/export")
async def export_audit_logs(
    request: Request,
    user_id: Optional[uuid.UUID] = Query(default=None),
    action: Optional[str] = Query(default=None),
    event_type: Optional[str] = Query(default=None),
    from_date: Optional[str] = Query(default=None),
    to_date: Optional[str] = Query(default=None),
    user_context: UserContext = Depends(get_current_user),
) -> StreamingResponse:
    """Export filtered audit logs as CSV download."""
    fd = _parse_date(from_date)
    td = _parse_date(to_date)
    async with get_tenant_session(request) as session:
        csv_content = await svc.export_audit_csv(
            session, user_id, action, event_type, fd, td,
        )
    today = datetime.utcnow().strftime("%Y%m%d")
    filename = f"audit_log_{today}.csv"
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _parse_date(val: Optional[str]) -> Optional[datetime]:
    """Parse a date string to datetime, or None."""
    if not val:
        return None
    try:
        return datetime.fromisoformat(val)
    except ValueError:
        return None

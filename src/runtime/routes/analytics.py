"""Analytics and audit log API routes."""
import logging
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import text

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
    request: Request,
    from_date: Optional[str] = Query(default=None, alias="from"),
    to_date: Optional[str] = Query(default=None, alias="to"),
    user_context: UserContext = Depends(get_current_user),
) -> DashboardData:
    """Return analytics dashboard metrics from real tenant data."""
    is_super_admin = "system_admin" in [r.value for r in user_context.roles]

    if is_super_admin:
        return await _get_platform_dashboard()

    fd = _parse_date(from_date)
    td = _parse_date(to_date)
    async with get_tenant_session(request) as session:
        return await svc.get_dashboard(session, fd, td)


@router.get("/top-users", response_model=list[TopUser])
async def get_top_users(
    request: Request,
    user_context: UserContext = Depends(get_current_user),
) -> list[TopUser]:
    """Return top users by activity from real audit data."""
    async with get_tenant_session(request) as session:
        return await svc.get_top_users(session)


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
    """Return paginated audit logs. Super admin sees platform logs."""
    from src.repo.analytics_repository import get_platform_audit_logs

    is_super_admin = "system_admin" in [r.value for r in user_context.roles]

    if is_super_admin:
        fd = _parse_date(from_date)
        td = _parse_date(to_date)
        items, total = await get_platform_audit_logs(fd, td, page, page_size)
        return PaginatedAuditLogs(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    fd = _parse_date(from_date)
    td = _parse_date(to_date)
    async with get_tenant_session(request) as session:
        return await svc.get_audit_logs(
            session, user_id, action, event_type,
            fd, td, page, page_size,
        )


@router.get("/export")
async def export_dashboard(
    request: Request,
    from_date: Optional[str] = Query(default=None, alias="from"),
    to_date: Optional[str] = Query(default=None, alias="to"),
    user_context: UserContext = Depends(get_current_user),
) -> StreamingResponse:
    """Export analytics report as CSV download."""
    fd = _parse_date(from_date)
    td = _parse_date(to_date)
    async with get_tenant_session(request) as session:
        csv_content = await svc.export_dashboard_csv(session, fd, td)
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


async def _get_platform_dashboard() -> DashboardData:
    """Build platform-wide dashboard for super admin across all tenant schemas."""
    from src.repo.database import create_platform_engine
    from src.repo.session_manager import TenantSessionManager

    _, platform_factory = create_platform_engine()
    async with platform_factory() as platform_session:
        result = await platform_session.execute(
            text(
                "SELECT slug, schema_name, name FROM tenants "
                "WHERE is_active = true AND slug != 'platform' "
                "ORDER BY name"
            )
        )
        tenants = result.fetchall()

    mgr = TenantSessionManager()
    sessions = {}
    tenant_names = {}
    try:
        for t in tenants:
            session = await mgr.get_tenant_session(t.schema_name)
            sessions[t.slug] = session
            tenant_names[t.slug] = t.name

        return await svc.get_platform_dashboard(sessions, tenant_names)
    finally:
        for s in sessions.values():
            await s.close()


def _parse_date(val: Optional[str]) -> Optional[datetime]:
    """Parse a date string to datetime, or None."""
    if not val:
        return None
    try:
        return datetime.fromisoformat(val)
    except ValueError:
        return None

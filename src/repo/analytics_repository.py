"""Repository for analytics dashboard and audit log queries."""
import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repo.master_data_models import AuditLog

logger = logging.getLogger(__name__)


async def get_audit_logs(
    session: AsyncSession,
    user_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
    event_type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[AuditLog], int]:
    """Return paginated, filtered audit logs."""
    base = select(AuditLog)
    count_q = select(func.count(AuditLog.id))

    if user_id:
        base = base.where(AuditLog.user_id == user_id)
        count_q = count_q.where(AuditLog.user_id == user_id)
    if action:
        base = base.where(AuditLog.action == action)
        count_q = count_q.where(AuditLog.action == action)
    if event_type:
        base = base.where(AuditLog.event_type == event_type)
        count_q = count_q.where(AuditLog.event_type == event_type)
    if from_date:
        base = base.where(AuditLog.created_at >= from_date)
        count_q = count_q.where(AuditLog.created_at >= from_date)
    if to_date:
        base = base.where(AuditLog.created_at <= to_date)
        count_q = count_q.where(AuditLog.created_at <= to_date)

    total = (await session.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    stmt = (
        base.order_by(AuditLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await session.execute(stmt)
    return list(result.scalars().all()), total


async def create_audit_log(
    session: AsyncSession,
    user_id: Optional[uuid.UUID],
    user_name: Optional[str],
    event_type: str,
    action: str,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Insert an audit log entry."""
    entry = AuditLog(
        id=uuid.uuid4(),
        user_id=user_id,
        user_name=user_name,
        event_type=event_type,
        action=action,
        details=details,
        ip_address=ip_address,
    )
    session.add(entry)
    await session.flush()
    return entry

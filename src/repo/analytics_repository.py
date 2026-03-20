"""Repository for analytics dashboard and audit log queries."""
import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select, text
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


async def create_tenant_audit_log_by_id(
    tenant_id: str,
    user_id: Optional[uuid.UUID],
    user_name: Optional[str],
    event_type: str,
    action: str,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Insert an audit log entry into a tenant's audit_logs table by tenant ID."""
    from src.repo.database import create_platform_engine
    from src.repo.session_manager import TenantSessionManager

    if not tenant_id:
        return

    # Look up schema name for tenant
    _, platform_factory = create_platform_engine()
    async with platform_factory() as platform_session:
        result = await platform_session.execute(
            text(
                "SELECT schema_name FROM tenants "
                "WHERE id::text = :tid OR slug = :tid"
            ),
            {"tid": tenant_id},
        )
        row = result.first()
        if not row:
            logger.warning("Tenant '%s' not found for audit log", tenant_id)
            return

    mgr = TenantSessionManager()
    session = await mgr.get_tenant_session(row.schema_name)
    try:
        await create_audit_log(
            session, user_id, user_name, event_type, action,
            details=details, ip_address=ip_address,
        )
        await session.commit()
    except Exception as exc:
        logger.warning("Failed to write tenant audit log: %s", exc)
        await session.rollback()
    finally:
        await session.close()


async def create_platform_audit_log(
    user_id: Optional[uuid.UUID],
    user_name: Optional[str],
    event_type: str,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Insert an audit log entry into the platform audit_logs table."""
    from src.repo.database import create_platform_engine

    _, factory = create_platform_engine()
    async with factory() as session:
        await session.execute(
            text(
                "INSERT INTO platform_audit_logs "
                "(user_id, user_name, event_type, action, entity_type, "
                "entity_id, details, ip_address) "
                "VALUES (:uid, :uname, :etype, :action, :entity_type, "
                ":entity_id, :details, :ip)"
            ),
            {
                "uid": str(user_id) if user_id else None,
                "uname": user_name,
                "etype": event_type,
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "details": details,
                "ip": ip_address,
            },
        )
        await session.commit()


async def get_platform_audit_logs(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[dict[str, object]], int]:
    """Return paginated platform audit logs."""
    from src.repo.database import create_platform_engine

    _, factory = create_platform_engine()
    async with factory() as session:
        where_clauses = []
        params: dict[str, object] = {}
        if from_date:
            where_clauses.append("created_at >= :from_date")
            params["from_date"] = from_date
        if to_date:
            where_clauses.append("created_at <= :to_date")
            params["to_date"] = to_date

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        count_result = await session.execute(
            text(f"SELECT count(*) FROM platform_audit_logs {where_sql}"),
            params,
        )
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await session.execute(
            text(
                f"SELECT id, user_id, user_name, event_type, action, "
                f"entity_type, entity_id, details, ip_address, created_at "
                f"FROM platform_audit_logs {where_sql} "
                f"ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            ),
            {**params, "limit": page_size, "offset": offset},
        )
        rows = result.fetchall()
        items = [
            {
                "id": str(r.id),
                "user_name": r.user_name,
                "event_type": r.event_type,
                "action": r.action,
                "details": f"{r.entity_type}: {r.entity_id}. {r.details or ''}" if r.entity_type else r.details,
                "ip_address": r.ip_address,
                "created_at": r.created_at.isoformat() if r.created_at else "",
            }
            for r in rows
        ]
        return items, total

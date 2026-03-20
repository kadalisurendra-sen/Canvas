"""Business logic for analytics dashboard and audit log."""
import csv
import io
import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.repo import analytics_repository as repo
from src.types.analytics import (
    AuditLogOut,
    DashboardData,
    MetricCard,
    PaginatedAuditLogs,
    StageDistribution,
    TemplateUsage,
    TimelinePoint,
    TopUser,
)

logger = logging.getLogger(__name__)


async def get_dashboard(
    session: AsyncSession,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> DashboardData:
    """Return dashboard metrics from real tenant data."""
    metrics = await _build_real_metrics(session)
    stages = await _build_real_stage_distribution(session)
    usage = await _build_real_template_usage(session)
    timeline = await _build_real_timeline(session)
    return DashboardData(
        metrics=metrics,
        stage_distribution=stages,
        template_usage=usage,
        evaluations_timeline=timeline,
    )


async def get_platform_dashboard(
    sessions: dict[str, AsyncSession],
    tenant_names: dict[str, str],
) -> DashboardData:
    """Return platform-wide dashboard for super admin."""
    total_templates = 0
    total_published = 0
    total_draft = 0
    total_audit_entries = 0
    tenant_template_counts: list[TemplateUsage] = []
    colors = ["#5F2CFF", "#02F576", "#8A5EFF", "#5EEAD4", "#F59E0B", "#EF4444"]

    for idx, (slug, session) in enumerate(sessions.items()):
        t_count = (await session.execute(text("SELECT count(*) FROM templates"))).scalar() or 0
        p_count = (await session.execute(text("SELECT count(*) FROM templates WHERE status='published'"))).scalar() or 0
        d_count = (await session.execute(text("SELECT count(*) FROM templates WHERE status='draft'"))).scalar() or 0
        a_count = (await session.execute(text("SELECT count(*) FROM audit_logs"))).scalar() or 0

        total_templates += t_count
        total_published += p_count
        total_draft += d_count
        total_audit_entries += a_count

        name = tenant_names.get(slug, slug)
        tenant_template_counts.append(
            TemplateUsage(
                category=name,
                percentage=t_count,
                color=colors[idx % len(colors)],
            )
        )

    # Normalize template usage to percentages
    if total_templates > 0:
        for item in tenant_template_counts:
            item.percentage = round((item.percentage / total_templates) * 100)

    metrics = [
        MetricCard(label="Total Tenants", value=str(len(sessions)), subtitle="Active organizations"),
        MetricCard(label="Total Templates", value=str(total_templates), subtitle="Across all tenants"),
        MetricCard(label="Published", value=str(total_published), subtitle="Live templates"),
        MetricCard(label="Drafts", value=str(total_draft), subtitle="Work in progress"),
        MetricCard(label="Audit Entries", value=str(total_audit_entries), subtitle="Total platform events"),
    ]

    return DashboardData(
        metrics=metrics,
        stage_distribution=[],
        template_usage=tenant_template_counts,
        evaluations_timeline=[],
    )


async def get_top_users(session: AsyncSession) -> list[TopUser]:
    """Return top users by audit log activity from real data."""
    result = await session.execute(
        text(
            "SELECT user_name, count(*) as cnt "
            "FROM audit_logs WHERE user_name IS NOT NULL "
            "GROUP BY user_name ORDER BY cnt DESC LIMIT 5"
        )
    )
    rows = result.fetchall()
    if not rows:
        return [TopUser(name="No activity yet", evaluations=0, last_active="-")]
    return [
        TopUser(name=r.user_name, evaluations=r.cnt, last_active="")
        for r in rows
    ]


async def get_audit_logs(
    session: AsyncSession,
    user_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
    event_type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedAuditLogs:
    """Return paginated audit logs."""
    items, total = await repo.get_audit_logs(
        session, user_id, action, event_type,
        from_date, to_date, page, page_size,
    )
    return PaginatedAuditLogs(
        items=[AuditLogOut.model_validate(e) for e in items],
        total=total,
        page=page,
        page_size=page_size,
    )


async def export_dashboard_csv(
    session: AsyncSession,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> str:
    """Generate CSV string for dashboard report."""
    data = await get_dashboard(session, from_date, to_date)
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["KPI Summary"])
    writer.writerow(["Metric", "Value", "Change"])
    for m in data.metrics:
        writer.writerow([m.label, m.value, m.change or ""])

    writer.writerow([])
    writer.writerow(["Template Usage"])
    writer.writerow(["Category", "Percentage"])
    for t in data.template_usage:
        writer.writerow([t.category, f"{t.percentage}%"])

    return output.getvalue()


async def export_audit_csv(
    session: AsyncSession,
    user_id: Optional[uuid.UUID] = None,
    action: Optional[str] = None,
    event_type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> str:
    """Generate CSV for audit log export."""
    items, _ = await repo.get_audit_logs(
        session, user_id, action, event_type,
        from_date, to_date, page=1, page_size=10000,
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Date/Time", "Actor", "Event Type", "Action", "Details", "IP Address",
    ])
    for entry in items:
        writer.writerow([
            entry.created_at.isoformat(),
            entry.user_name or "",
            entry.event_type,
            entry.action,
            entry.details or "",
            entry.ip_address or "",
        ])
    return output.getvalue()


async def _build_real_metrics(session: AsyncSession) -> list[MetricCard]:
    """Build KPI metrics from real tenant DB."""
    total = (await session.execute(text("SELECT count(*) FROM templates"))).scalar() or 0
    published = (await session.execute(text("SELECT count(*) FROM templates WHERE status='published'"))).scalar() or 0
    draft = (await session.execute(text("SELECT count(*) FROM templates WHERE status='draft'"))).scalar() or 0
    categories = (await session.execute(text("SELECT count(*) FROM master_data_categories"))).scalar() or 0
    audit_count = (await session.execute(text("SELECT count(*) FROM audit_logs"))).scalar() or 0

    return [
        MetricCard(label="Total Templates", value=str(total), subtitle="All templates"),
        MetricCard(label="Published", value=str(published), subtitle="Live templates"),
        MetricCard(label="Drafts", value=str(draft), subtitle="Work in progress"),
        MetricCard(label="Master Data Categories", value=str(categories), subtitle="Configured categories"),
        MetricCard(label="Audit Log Entries", value=str(audit_count), subtitle="Total events recorded"),
    ]


async def _build_real_stage_distribution(session: AsyncSession) -> list[StageDistribution]:
    """Build stage distribution from real template stages."""
    result = await session.execute(
        text(
            "SELECT ts.name, count(*) as cnt "
            "FROM template_stages ts "
            "JOIN templates t ON ts.template_id = t.id "
            "GROUP BY ts.name ORDER BY cnt DESC LIMIT 10"
        )
    )
    rows = result.fetchall()
    if not rows:
        return []
    max_count = max(r.cnt for r in rows) if rows else 1
    return [
        StageDistribution(
            stage=r.name,
            count=r.cnt,
            percentage=round((r.cnt / max_count) * 100),
        )
        for r in rows
    ]


async def _build_real_template_usage(session: AsyncSession) -> list[TemplateUsage]:
    """Build template usage by category from real data."""
    result = await session.execute(
        text(
            "SELECT category, count(*) as cnt "
            "FROM templates GROUP BY category ORDER BY cnt DESC"
        )
    )
    rows = result.fetchall()
    if not rows:
        return []
    total = sum(r.cnt for r in rows)
    colors = ["#5F2CFF", "#02F576", "#8A5EFF", "#5EEAD4", "#F59E0B"]
    return [
        TemplateUsage(
            category=r.category,
            percentage=round((r.cnt / total) * 100) if total > 0 else 0,
            color=colors[i % len(colors)],
        )
        for i, r in enumerate(rows)
    ]


async def _build_real_timeline(session: AsyncSession) -> list[TimelinePoint]:
    """Build template creation timeline from real data."""
    result = await session.execute(
        text(
            "SELECT to_char(created_at, 'Mon') as month, count(*) as cnt "
            "FROM templates GROUP BY to_char(created_at, 'Mon'), "
            "date_trunc('month', created_at) "
            "ORDER BY date_trunc('month', created_at) LIMIT 12"
        )
    )
    rows = result.fetchall()
    if not rows:
        return []
    return [TimelinePoint(month=r.month, count=r.cnt) for r in rows]

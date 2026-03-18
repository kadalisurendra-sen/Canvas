"""Business logic for analytics dashboard and audit log."""
import csv
import io
import logging
import uuid
from datetime import datetime
from typing import Optional

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
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> DashboardData:
    """Return dashboard metrics with mock/seed data."""
    metrics = _build_metrics()
    stages = _build_stage_distribution()
    usage = _build_template_usage()
    timeline = _build_timeline()
    return DashboardData(
        metrics=metrics,
        stage_distribution=stages,
        template_usage=usage,
        evaluations_timeline=timeline,
    )


async def get_top_users() -> list[TopUser]:
    """Return top users by activity (mock data)."""
    return [
        TopUser(name="Sarah Connor", evaluations=28, last_active="Today"),
        TopUser(name="James Miller", evaluations=24, last_active="2h ago"),
        TopUser(name="Elena R.", evaluations=19, last_active="Yesterday"),
        TopUser(name="Mark T.", evaluations=15, last_active="3d ago"),
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
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
) -> str:
    """Generate CSV string for dashboard report."""
    data = await get_dashboard(from_date, to_date)
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["KPI Summary"])
    writer.writerow(["Metric", "Value", "Change"])
    for m in data.metrics:
        writer.writerow([m.label, m.value, m.change or ""])

    writer.writerow([])
    writer.writerow(["Stage Distribution"])
    writer.writerow(["Stage", "Count", "Percentage"])
    for s in data.stage_distribution:
        writer.writerow([s.stage, s.count, f"{s.percentage}%"])

    writer.writerow([])
    writer.writerow(["Template Usage"])
    writer.writerow(["Category", "Percentage"])
    for t in data.template_usage:
        writer.writerow([t.category, f"{t.percentage}%"])

    writer.writerow([])
    writer.writerow(["Evaluations Timeline"])
    writer.writerow(["Month", "Count"])
    for p in data.evaluations_timeline:
        writer.writerow([p.month, p.count])

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


def _build_metrics() -> list[MetricCard]:
    """Build mock KPI metric cards."""
    return [
        MetricCard(label="Total Projects", value="24", change="+3", subtitle="v. last month"),
        MetricCard(label="Total Use Cases", value="156", change="+12", subtitle="v. last month"),
        MetricCard(label="Active Evaluations", value="38", subtitle="Currently in progress"),
        MetricCard(label="Completed Evaluations", value="92", subtitle="Historical total"),
        MetricCard(label="Average ROI", value="127%", subtitle="Projected overall"),
    ]


def _build_stage_distribution() -> list[StageDistribution]:
    """Build mock stage distribution data."""
    return [
        StageDistribution(stage="Desirable", count=45, percentage=80),
        StageDistribution(stage="Feasible", count=38, percentage=65),
        StageDistribution(stage="Viable", count=32, percentage=55),
        StageDistribution(stage="Prioritized", count=25, percentage=45),
        StageDistribution(stage="Not Started", count=16, percentage=25),
    ]


def _build_template_usage() -> list[TemplateUsage]:
    """Build mock template usage data."""
    return [
        TemplateUsage(category="AI/ML", percentage=45, color="#5F2CFF"),
        TemplateUsage(category="RPA", percentage=25, color="#02F576"),
        TemplateUsage(category="Agentic AI", percentage=15, color="#8A5EFF"),
        TemplateUsage(category="Data Science", percentage=10, color="#5EEAD4"),
        TemplateUsage(category="Custom", percentage=5, color="#99F6E4"),
    ]


def _build_timeline() -> list[TimelinePoint]:
    """Build mock evaluations timeline."""
    return [
        TimelinePoint(month="Jan", count=12),
        TimelinePoint(month="Feb", count=18),
        TimelinePoint(month="Mar", count=25),
        TimelinePoint(month="Apr", count=30),
        TimelinePoint(month="May", count=42),
        TimelinePoint(month="Jun", count=55),
    ]

"""Tests for analytics type schemas."""
import uuid
from datetime import datetime

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


def test_metric_card_construction() -> None:
    """MetricCard should store label, value, change."""
    mc = MetricCard(label="Total Projects", value="24", change="+3")
    assert mc.label == "Total Projects"
    assert mc.change == "+3"


def test_metric_card_optional_change() -> None:
    """MetricCard change field is optional."""
    mc = MetricCard(label="Active", value="38")
    assert mc.change is None


def test_stage_distribution() -> None:
    """StageDistribution should hold stage name, count, pct."""
    sd = StageDistribution(stage="Desirable", count=45, percentage=80.0)
    assert sd.count == 45


def test_template_usage() -> None:
    """TemplateUsage should hold category, percentage, color."""
    tu = TemplateUsage(category="AI/ML", percentage=45.0, color="#5F2CFF")
    assert tu.color == "#5F2CFF"


def test_timeline_point() -> None:
    """TimelinePoint should store month and count."""
    tp = TimelinePoint(month="Jan", count=12)
    assert tp.month == "Jan"


def test_top_user() -> None:
    """TopUser should have name, evaluations, last_active."""
    tu = TopUser(name="Sarah Connor", evaluations=28, last_active="Today")
    assert tu.evaluations == 28


def test_dashboard_data_structure() -> None:
    """DashboardData should aggregate all chart data."""
    dd = DashboardData(
        metrics=[],
        stage_distribution=[],
        template_usage=[],
        evaluations_timeline=[],
    )
    assert dd.metrics == []


def test_audit_log_out() -> None:
    """AuditLogOut should parse audit entry."""
    entry = AuditLogOut(
        id=uuid.uuid4(),
        created_at=datetime.utcnow(),
        user_name="Admin",
        event_type="MANAGEMENT",
        action="config_change",
        details='{"key": "value"}',
        ip_address="127.0.0.1",
    )
    assert entry.event_type == "MANAGEMENT"


def test_paginated_audit_logs() -> None:
    """PaginatedAuditLogs should have items, total, page."""
    pal = PaginatedAuditLogs(items=[], total=0, page=1, page_size=10)
    assert pal.total == 0

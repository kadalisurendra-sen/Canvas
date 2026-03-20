"""Pydantic schemas for analytics and audit log endpoints."""
import uuid
from datetime import datetime
from typing import Optional

from pydantic import Field

from src.types.base import BaseSchema


class MetricCard(BaseSchema):
    """Single KPI metric card data."""

    label: str
    value: str
    change: Optional[str] = None
    subtitle: str = ""


class StageDistribution(BaseSchema):
    """Bar chart data for use cases by stage."""

    stage: str
    count: int
    percentage: float


class TemplateUsage(BaseSchema):
    """Donut chart data for template usage."""

    category: str
    percentage: float
    color: str


class TimelinePoint(BaseSchema):
    """Single point on evaluations over time chart."""

    month: str
    count: int


class TopUser(BaseSchema):
    """Top user activity entry."""

    name: str
    avatar_url: Optional[str] = None
    evaluations: int
    last_active: str


class DashboardData(BaseSchema):
    """Full analytics dashboard payload."""

    metrics: list[MetricCard]
    stage_distribution: list[StageDistribution]
    template_usage: list[TemplateUsage]
    evaluations_timeline: list[TimelinePoint]


class AuditLogOut(BaseSchema):
    """Audit log entry for API response."""

    model_config = {"from_attributes": True}

    id: str | uuid.UUID
    created_at: str | datetime
    user_name: Optional[str] = None
    event_type: str
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None


class PaginatedAuditLogs(BaseSchema):
    """Paginated audit log response."""

    items: list[AuditLogOut | dict[str, object]]
    total: int
    page: int
    page_size: int

"""Tests for analytics service layer."""
import pytest

from src.service.analytics_service import (
    _build_metrics,
    _build_stage_distribution,
    _build_template_usage,
    _build_timeline,
    export_dashboard_csv,
    get_dashboard,
    get_top_users,
)


def test_build_metrics_returns_five_cards() -> None:
    """Should return five KPI metric cards."""
    metrics = _build_metrics()
    assert len(metrics) == 5
    labels = [m.label for m in metrics]
    assert "Total Projects" in labels
    assert "Average ROI" in labels


def test_build_stage_distribution_has_five_stages() -> None:
    """Should return five stage entries."""
    stages = _build_stage_distribution()
    assert len(stages) == 5
    assert stages[0].stage == "Desirable"


def test_build_template_usage_sums_to_100() -> None:
    """Template usage percentages should sum to 100."""
    usage = _build_template_usage()
    total = sum(u.percentage for u in usage)
    assert total == 100.0


def test_build_timeline_has_months() -> None:
    """Timeline should have monthly data points."""
    timeline = _build_timeline()
    assert len(timeline) >= 1
    assert timeline[0].month == "Jan"


@pytest.mark.asyncio
async def test_get_dashboard_returns_data() -> None:
    """get_dashboard should return complete DashboardData."""
    data = await get_dashboard()
    assert len(data.metrics) == 5
    assert len(data.stage_distribution) == 5
    assert len(data.template_usage) == 5
    assert len(data.evaluations_timeline) >= 1


@pytest.mark.asyncio
async def test_get_top_users_returns_list() -> None:
    """get_top_users should return mock user list."""
    users = await get_top_users()
    assert len(users) >= 1
    assert users[0].name == "Sarah Connor"


@pytest.mark.asyncio
async def test_export_dashboard_csv_content() -> None:
    """export_dashboard_csv should produce CSV text."""
    csv_text = await export_dashboard_csv()
    assert "KPI Summary" in csv_text
    assert "Stage Distribution" in csv_text
    assert "Total Projects" in csv_text

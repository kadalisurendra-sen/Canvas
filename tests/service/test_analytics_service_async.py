"""Tests for analytics service async functions — audit logs and CSV exports."""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.service.analytics_service import (
    export_audit_csv,
    export_dashboard_csv,
    get_audit_logs,
    get_dashboard,
    get_top_users,
)


def _mock_session() -> AsyncMock:
    return AsyncMock()


def _make_audit_entry(
    action: str = "CREATE_USER",
    event_type: str = "MANAGEMENT",
) -> MagicMock:
    entry = MagicMock()
    entry.id = uuid.uuid4()
    entry.created_at = datetime(2026, 3, 15, 12, 0, 0)
    entry.user_name = "Admin"
    entry.event_type = event_type
    entry.action = action
    entry.details = "some details"
    entry.ip_address = "10.0.0.1"
    return entry


class TestGetAuditLogs:
    """Tests for get_audit_logs service."""

    @pytest.mark.asyncio
    @patch("src.service.analytics_service.repo")
    async def test_returns_paginated_logs(self, mock_repo: MagicMock) -> None:
        entry = _make_audit_entry()
        mock_repo.get_audit_logs = AsyncMock(return_value=([entry], 1))
        result = await get_audit_logs(_mock_session())
        assert result.total == 1
        assert len(result.items) == 1
        assert result.page == 1

    @pytest.mark.asyncio
    @patch("src.service.analytics_service.repo")
    async def test_with_filters(self, mock_repo: MagicMock) -> None:
        mock_repo.get_audit_logs = AsyncMock(return_value=([], 0))
        result = await get_audit_logs(
            _mock_session(),
            user_id=uuid.uuid4(),
            action="DELETE",
            event_type="SECURITY",
            from_date=datetime(2026, 1, 1),
            to_date=datetime(2026, 12, 31),
            page=2,
            page_size=5,
        )
        assert result.total == 0
        assert result.page == 2


class TestExportDashboardCsv:
    """Tests for export_dashboard_csv."""

    @pytest.mark.asyncio
    async def test_csv_contains_all_sections(self) -> None:
        csv_text = await export_dashboard_csv()
        assert "KPI Summary" in csv_text
        assert "Stage Distribution" in csv_text
        assert "Template Usage" in csv_text
        assert "Evaluations Timeline" in csv_text

    @pytest.mark.asyncio
    async def test_csv_with_date_filters(self) -> None:
        csv_text = await export_dashboard_csv(
            from_date=datetime(2026, 1, 1),
            to_date=datetime(2026, 6, 30),
        )
        assert "Total Projects" in csv_text


class TestExportAuditCsv:
    """Tests for export_audit_csv."""

    @pytest.mark.asyncio
    @patch("src.service.analytics_service.repo")
    async def test_generates_csv_with_entries(self, mock_repo: MagicMock) -> None:
        entry = _make_audit_entry()
        mock_repo.get_audit_logs = AsyncMock(return_value=([entry], 1))
        csv_text = await export_audit_csv(_mock_session())
        assert "Date/Time" in csv_text
        assert "CREATE_USER" in csv_text
        assert "Admin" in csv_text

    @pytest.mark.asyncio
    @patch("src.service.analytics_service.repo")
    async def test_generates_csv_empty(self, mock_repo: MagicMock) -> None:
        mock_repo.get_audit_logs = AsyncMock(return_value=([], 0))
        csv_text = await export_audit_csv(_mock_session())
        assert "Date/Time" in csv_text
        # Only header row
        lines = csv_text.strip().split("\n")
        assert len(lines) == 1

    @pytest.mark.asyncio
    @patch("src.service.analytics_service.repo")
    async def test_handles_none_fields(self, mock_repo: MagicMock) -> None:
        entry = _make_audit_entry()
        entry.user_name = None
        entry.details = None
        entry.ip_address = None
        mock_repo.get_audit_logs = AsyncMock(return_value=([entry], 1))
        csv_text = await export_audit_csv(_mock_session())
        assert "Date/Time" in csv_text


class TestGetDashboardWithDates:
    """Tests for get_dashboard with date parameters."""

    @pytest.mark.asyncio
    async def test_accepts_date_range(self) -> None:
        data = await get_dashboard(
            from_date=datetime(2026, 1, 1),
            to_date=datetime(2026, 6, 30),
        )
        assert len(data.metrics) == 5

    @pytest.mark.asyncio
    async def test_none_dates(self) -> None:
        data = await get_dashboard(from_date=None, to_date=None)
        assert len(data.metrics) == 5


class TestGetTopUsers:
    """Tests for get_top_users."""

    @pytest.mark.asyncio
    async def test_returns_four_users(self) -> None:
        users = await get_top_users()
        assert len(users) == 4
        names = [u.name for u in users]
        assert "Sarah Connor" in names
        assert "James Miller" in names

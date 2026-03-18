"""Tests for analytics repository functions."""
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.repo.analytics_repository import create_audit_log, get_audit_logs


def _mock_session() -> AsyncMock:
    """Create a mock AsyncSession."""
    return AsyncMock()


class TestGetAuditLogs:
    """Tests for get_audit_logs."""

    @pytest.mark.asyncio
    async def test_returns_items_and_total(self) -> None:
        session = _mock_session()
        mock_entry = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [mock_entry]
        result_items = MagicMock()
        result_items.scalars.return_value = scalars_mock
        count_result = MagicMock()
        count_result.scalar.return_value = 1
        session.execute.side_effect = [count_result, result_items]

        items, total = await get_audit_logs(session)
        assert total == 1
        assert len(items) == 1

    @pytest.mark.asyncio
    async def test_with_all_filters(self) -> None:
        session = _mock_session()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        result_items = MagicMock()
        result_items.scalars.return_value = scalars_mock
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        session.execute.side_effect = [count_result, result_items]

        items, total = await get_audit_logs(
            session,
            user_id=uuid.uuid4(),
            action="CREATE",
            event_type="MANAGEMENT",
            from_date=datetime(2026, 1, 1),
            to_date=datetime(2026, 12, 31),
            page=2,
            page_size=5,
        )
        assert total == 0
        assert items == []

    @pytest.mark.asyncio
    async def test_no_total_returns_zero(self) -> None:
        session = _mock_session()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        result_items = MagicMock()
        result_items.scalars.return_value = scalars_mock
        count_result = MagicMock()
        count_result.scalar.return_value = None
        session.execute.side_effect = [count_result, result_items]

        items, total = await get_audit_logs(session)
        assert total == 0


class TestCreateAuditLog:
    """Tests for create_audit_log."""

    @pytest.mark.asyncio
    async def test_creates_entry(self) -> None:
        session = _mock_session()
        uid = uuid.uuid4()
        entry = await create_audit_log(
            session,
            user_id=uid,
            user_name="John Doe",
            event_type="MANAGEMENT",
            action="CREATE_USER",
            details="Created user jane@test.com",
            ip_address="192.168.1.1",
        )
        assert entry.user_id == uid
        assert entry.event_type == "MANAGEMENT"
        assert entry.action == "CREATE_USER"
        session.add.assert_called_once()
        session.flush.assert_awaited()

    @pytest.mark.asyncio
    async def test_creates_with_optional_none(self) -> None:
        session = _mock_session()
        entry = await create_audit_log(
            session,
            user_id=None,
            user_name=None,
            event_type="SYSTEM",
            action="STARTUP",
        )
        assert entry.user_id is None
        assert entry.details is None
        assert entry.ip_address is None

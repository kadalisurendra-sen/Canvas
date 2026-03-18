"""Tests for master data repository functions."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.repo.master_data_repository import (
    bulk_insert_values,
    create_value,
    delete_value,
    get_max_sort_order,
    list_categories,
    list_values,
    reorder_values,
    update_value,
    value_exists,
)


def _mock_session() -> AsyncMock:
    """Create a mock AsyncSession."""
    session = AsyncMock()
    return session


class TestListCategories:
    """Tests for list_categories."""

    @pytest.mark.asyncio
    async def test_returns_list_of_dicts(self) -> None:
        session = _mock_session()
        mock_row = MagicMock()
        mock_row._asdict.return_value = {
            "id": uuid.uuid4(),
            "name": "risk",
            "display_name": "Risk Categories",
            "icon": "warning",
            "sort_order": 1,
            "item_count": 5,
        }
        result_mock = MagicMock()
        result_mock.all.return_value = [mock_row]
        session.execute.return_value = result_mock
        result = await list_categories(session)
        assert len(result) == 1
        assert result[0]["name"] == "risk"

    @pytest.mark.asyncio
    async def test_returns_empty_list(self) -> None:
        session = _mock_session()
        result_mock = MagicMock()
        result_mock.all.return_value = []
        session.execute.return_value = result_mock
        result = await list_categories(session)
        assert result == []


class TestListValues:
    """Tests for list_values."""

    @pytest.mark.asyncio
    async def test_returns_items_and_total(self) -> None:
        session = _mock_session()
        cat_id = uuid.uuid4()
        mock_value = MagicMock()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = [mock_value]
        result_items = MagicMock()
        result_items.scalars.return_value = scalars_mock

        count_result = MagicMock()
        count_result.scalar.return_value = 1

        session.execute.side_effect = [count_result, result_items]
        items, total = await list_values(session, cat_id)
        assert total == 1
        assert len(items) == 1

    @pytest.mark.asyncio
    async def test_with_search_filter(self) -> None:
        session = _mock_session()
        cat_id = uuid.uuid4()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        result_items = MagicMock()
        result_items.scalars.return_value = scalars_mock
        count_result = MagicMock()
        count_result.scalar.return_value = 0
        session.execute.side_effect = [count_result, result_items]
        items, total = await list_values(session, cat_id, search="test")
        assert total == 0
        assert items == []

    @pytest.mark.asyncio
    async def test_pagination(self) -> None:
        session = _mock_session()
        cat_id = uuid.uuid4()
        scalars_mock = MagicMock()
        scalars_mock.all.return_value = []
        result_items = MagicMock()
        result_items.scalars.return_value = scalars_mock
        count_result = MagicMock()
        count_result.scalar.return_value = 25
        session.execute.side_effect = [count_result, result_items]
        items, total = await list_values(session, cat_id, page=3, page_size=5)
        assert total == 25


class TestGetMaxSortOrder:
    """Tests for get_max_sort_order."""

    @pytest.mark.asyncio
    async def test_returns_max_order(self) -> None:
        session = _mock_session()
        result_mock = MagicMock()
        result_mock.scalar.return_value = 5
        session.execute.return_value = result_mock
        result = await get_max_sort_order(session, uuid.uuid4())
        assert result == 5

    @pytest.mark.asyncio
    async def test_returns_zero_when_none(self) -> None:
        session = _mock_session()
        result_mock = MagicMock()
        result_mock.scalar.return_value = 0
        session.execute.return_value = result_mock
        result = await get_max_sort_order(session, uuid.uuid4())
        assert result == 0


class TestCreateValue:
    """Tests for create_value."""

    @pytest.mark.asyncio
    async def test_creates_and_returns_value(self) -> None:
        session = _mock_session()
        # Mock get_max_sort_order call
        result_mock = MagicMock()
        result_mock.scalar.return_value = 3
        session.execute.return_value = result_mock

        cat_id = uuid.uuid4()
        row = await create_value(
            session, cat_id, "val1", "Label 1", "high", "A description"
        )
        assert row.value == "val1"
        assert row.label == "Label 1"
        assert row.sort_order == 4
        session.add.assert_called_once()
        session.flush.assert_awaited()


class TestUpdateValue:
    """Tests for update_value."""

    @pytest.mark.asyncio
    async def test_updates_existing_value(self) -> None:
        session = _mock_session()
        mock_row = MagicMock()
        mock_row.label = "Old Label"
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_row
        session.execute.return_value = result_mock

        result = await update_value(session, uuid.uuid4(), {"label": "New Label"})
        assert result is not None
        assert result.label == "New Label"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self) -> None:
        session = _mock_session()
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        session.execute.return_value = result_mock

        result = await update_value(session, uuid.uuid4(), {"label": "X"})
        assert result is None

    @pytest.mark.asyncio
    async def test_skips_none_values(self) -> None:
        session = _mock_session()
        mock_row = MagicMock()
        mock_row.label = "Original"
        mock_row.severity = "high"
        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = mock_row
        session.execute.return_value = result_mock

        result = await update_value(
            session, uuid.uuid4(), {"label": None, "severity": "low"}
        )
        assert result is not None
        # label should not be changed (None values skipped)
        assert result.label == "Original"
        assert result.severity == "low"


class TestDeleteValue:
    """Tests for delete_value."""

    @pytest.mark.asyncio
    async def test_returns_true_when_deleted(self) -> None:
        session = _mock_session()
        result_mock = MagicMock()
        result_mock.rowcount = 1
        session.execute.return_value = result_mock
        assert await delete_value(session, uuid.uuid4()) is True

    @pytest.mark.asyncio
    async def test_returns_false_when_not_found(self) -> None:
        session = _mock_session()
        result_mock = MagicMock()
        result_mock.rowcount = 0
        session.execute.return_value = result_mock
        assert await delete_value(session, uuid.uuid4()) is False


class TestReorderValues:
    """Tests for reorder_values."""

    @pytest.mark.asyncio
    async def test_updates_sort_orders(self) -> None:
        session = _mock_session()
        cat_id = uuid.uuid4()
        ids = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]
        await reorder_values(session, cat_id, ids)
        assert session.execute.await_count == 3
        session.flush.assert_awaited()


class TestBulkInsertValues:
    """Tests for bulk_insert_values."""

    @pytest.mark.asyncio
    async def test_inserts_rows(self) -> None:
        session = _mock_session()
        cat_id = uuid.uuid4()
        rows = [
            {"value": "v1", "label": "L1", "severity": None, "description": None},
            {"value": "v2", "label": "L2", "severity": "high", "description": "desc"},
        ]
        count = await bulk_insert_values(session, cat_id, rows, 0)
        assert count == 2
        session.execute.assert_awaited()
        session.flush.assert_awaited()

    @pytest.mark.asyncio
    async def test_empty_rows_returns_zero(self) -> None:
        session = _mock_session()
        count = await bulk_insert_values(session, uuid.uuid4(), [], 0)
        assert count == 0
        session.execute.assert_not_awaited()


class TestValueExists:
    """Tests for value_exists."""

    @pytest.mark.asyncio
    async def test_returns_true_when_exists(self) -> None:
        session = _mock_session()
        result_mock = MagicMock()
        result_mock.scalar.return_value = 1
        session.execute.return_value = result_mock
        assert await value_exists(session, uuid.uuid4(), "test") is True

    @pytest.mark.asyncio
    async def test_returns_false_when_not_exists(self) -> None:
        session = _mock_session()
        result_mock = MagicMock()
        result_mock.scalar.return_value = 0
        session.execute.return_value = result_mock
        assert await value_exists(session, uuid.uuid4(), "test") is False

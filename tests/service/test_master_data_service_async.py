"""Tests for master data service async functions."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.service.master_data_service import (
    MAX_IMPORT_ROWS,
    create_value,
    delete_value,
    get_categories,
    get_values,
    import_csv,
    reorder_values,
    update_value,
)
from src.types.master_data import ValueCreate, ValueUpdate


def _mock_session() -> AsyncMock:
    return AsyncMock()


class TestGetCategories:
    """Tests for get_categories."""

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_returns_category_list(self, mock_repo: MagicMock) -> None:
        mock_repo.list_categories = AsyncMock(return_value=[
            {"id": uuid.uuid4(), "name": "risk", "display_name": "Risk",
             "icon": "warn", "sort_order": 1, "item_count": 3},
        ])
        result = await get_categories(_mock_session())
        assert len(result) == 1
        assert result[0].name == "risk"


class TestGetValues:
    """Tests for get_values."""

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_returns_paginated_values(self, mock_repo: MagicMock) -> None:
        mock_val = MagicMock()
        mock_val.id = uuid.uuid4()
        mock_val.value = "v1"
        mock_val.label = "L1"
        mock_val.severity = None
        mock_val.description = None
        mock_val.is_active = True
        mock_val.sort_order = 1
        mock_repo.list_values = AsyncMock(return_value=([mock_val], 1))
        result = await get_values(_mock_session(), uuid.uuid4())
        assert result.total == 1
        assert result.page == 1
        assert len(result.items) == 1


class TestCreateValue:
    """Tests for create_value."""

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_creates_value(self, mock_repo: MagicMock) -> None:
        mock_row = MagicMock()
        mock_row.id = uuid.uuid4()
        mock_row.value = "test"
        mock_row.label = "Test"
        mock_row.severity = None
        mock_row.description = None
        mock_row.is_active = True
        mock_row.sort_order = 1
        mock_repo.create_value = AsyncMock(return_value=mock_row)
        data = ValueCreate(value="test", label="Test")
        result = await create_value(_mock_session(), uuid.uuid4(), data)
        assert result.value == "test"


class TestUpdateValue:
    """Tests for update_value."""

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_returns_none_when_empty_update(self, mock_repo: MagicMock) -> None:
        data = ValueUpdate()  # all None
        result = await update_value(_mock_session(), uuid.uuid4(), data)
        assert result is None

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_returns_none_when_not_found(self, mock_repo: MagicMock) -> None:
        mock_repo.update_value = AsyncMock(return_value=None)
        data = ValueUpdate(label="New")
        result = await update_value(_mock_session(), uuid.uuid4(), data)
        assert result is None

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_returns_updated_value(self, mock_repo: MagicMock) -> None:
        mock_row = MagicMock()
        mock_row.id = uuid.uuid4()
        mock_row.value = "v1"
        mock_row.label = "Updated"
        mock_row.severity = None
        mock_row.description = None
        mock_row.is_active = True
        mock_row.sort_order = 1
        mock_repo.update_value = AsyncMock(return_value=mock_row)
        data = ValueUpdate(label="Updated")
        result = await update_value(_mock_session(), uuid.uuid4(), data)
        assert result is not None
        assert result.label == "Updated"


class TestDeleteValue:
    """Tests for delete_value."""

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_returns_true_on_success(self, mock_repo: MagicMock) -> None:
        mock_repo.delete_value = AsyncMock(return_value=True)
        assert await delete_value(_mock_session(), uuid.uuid4()) is True

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_returns_false_on_not_found(self, mock_repo: MagicMock) -> None:
        mock_repo.delete_value = AsyncMock(return_value=False)
        assert await delete_value(_mock_session(), uuid.uuid4()) is False


class TestReorderValues:
    """Tests for reorder_values."""

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_delegates_to_repo(self, mock_repo: MagicMock) -> None:
        mock_repo.reorder_values = AsyncMock()
        cat_id = uuid.uuid4()
        ids = [uuid.uuid4(), uuid.uuid4()]
        await reorder_values(_mock_session(), cat_id, ids)
        mock_repo.reorder_values.assert_awaited_once()


class TestImportCsv:
    """Tests for import_csv."""

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_imports_valid_csv(self, mock_repo: MagicMock) -> None:
        mock_repo.get_max_sort_order = AsyncMock(return_value=0)
        mock_repo.value_exists = AsyncMock(return_value=False)
        mock_repo.bulk_insert_values = AsyncMock(return_value=2)
        csv_content = b"value,label\nv1,Label 1\nv2,Label 2"
        result = await import_csv(_mock_session(), uuid.uuid4(), csv_content)
        assert result.imported == 2
        assert result.skipped == 0

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_skips_existing_values(self, mock_repo: MagicMock) -> None:
        mock_repo.get_max_sort_order = AsyncMock(return_value=0)
        mock_repo.value_exists = AsyncMock(side_effect=[True, False])
        mock_repo.bulk_insert_values = AsyncMock(return_value=1)
        csv_content = b"value,label\nexisting,Existing\nnew,New"
        result = await import_csv(_mock_session(), uuid.uuid4(), csv_content)
        assert result.imported == 1
        assert result.skipped == 1

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_rejects_too_many_rows(self, mock_repo: MagicMock) -> None:
        # Build a CSV with more than MAX_IMPORT_ROWS
        header = "value,label\n"
        rows = "\n".join(f"v{i},L{i}" for i in range(MAX_IMPORT_ROWS + 1))
        csv_content = (header + rows).encode()
        result = await import_csv(_mock_session(), uuid.uuid4(), csv_content)
        assert result.imported == 0
        assert len(result.errors) == 1
        assert "max" in result.errors[0]["message"].lower()

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_handles_empty_csv(self, mock_repo: MagicMock) -> None:
        mock_repo.get_max_sort_order = AsyncMock(return_value=0)
        mock_repo.value_exists = AsyncMock(return_value=False)
        mock_repo.bulk_insert_values = AsyncMock()
        csv_content = b""
        result = await import_csv(_mock_session(), uuid.uuid4(), csv_content)
        assert result.imported == 0
        assert len(result.errors) >= 1

    @pytest.mark.asyncio
    @patch("src.service.master_data_service.repo")
    async def test_no_valid_rows_no_bulk_insert(self, mock_repo: MagicMock) -> None:
        mock_repo.get_max_sort_order = AsyncMock(return_value=0)
        mock_repo.value_exists = AsyncMock(return_value=True)
        csv_content = b"value,label\nexisting,Existing"
        result = await import_csv(_mock_session(), uuid.uuid4(), csv_content)
        assert result.imported == 0
        assert result.skipped == 1
        mock_repo.bulk_insert_values.assert_not_called()

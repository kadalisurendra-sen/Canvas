"""Tests for template wizard service — scoring validation and publish."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.service.template_service import (
    TemplateNotFoundError,
    TemplateValidationError,
    _count_fields,
    get_template,
    get_templates,
    create_new_template,
    update_template,
    update_stages,
    remove_template,
)
from src.types.enums import FailAction, TemplateStatus
from src.types.template import (
    ScoringStageInput,
    ScoringUpdate,
    TemplateCreate,
    TemplateUpdate,
)


def _make_template_mock(
    name: str = "Test",
    status: str = "draft",
    version: int = 1,
    stages: list | None = None,
) -> MagicMock:
    t = MagicMock()
    t.id = uuid.uuid4()
    t.name = name
    t.category = "AI/ML"
    t.description = "desc"
    t.icon = "icon"
    t.theme_color = "#FFF"
    t.status = status
    t.version = version
    t.created_by = uuid.uuid4()
    t.created_at = "2026-01-01"
    t.updated_at = "2026-01-01"
    t.stages = stages or []
    t.tags = []
    return t


class TestGetTemplate:
    """Tests for get_template."""

    @pytest.mark.asyncio
    @patch("src.service.template_service.get_template_by_id", new_callable=AsyncMock)
    async def test_returns_template(self, mock_get: AsyncMock) -> None:
        tpl = _make_template_mock()
        mock_get.return_value = tpl
        result = await get_template(AsyncMock(), tpl.id)
        assert result is tpl

    @pytest.mark.asyncio
    @patch("src.service.template_service.get_template_by_id", new_callable=AsyncMock)
    async def test_raises_not_found(self, mock_get: AsyncMock) -> None:
        mock_get.return_value = None
        with pytest.raises(TemplateNotFoundError):
            await get_template(AsyncMock(), uuid.uuid4())


class TestGetTemplates:
    """Tests for get_templates."""

    @pytest.mark.asyncio
    @patch("src.service.template_service.list_templates", new_callable=AsyncMock)
    async def test_returns_list_response(self, mock_list: AsyncMock) -> None:
        tpl = _make_template_mock()
        mock_list.return_value = ([tpl], 1)
        result = await get_templates(AsyncMock())
        assert result.total == 1
        assert len(result.items) == 1

    @pytest.mark.asyncio
    @patch("src.service.template_service.list_templates", new_callable=AsyncMock)
    async def test_with_filters(self, mock_list: AsyncMock) -> None:
        mock_list.return_value = ([], 0)
        result = await get_templates(
            AsyncMock(), status="draft", category="AI/ML",
            search="test", page=2, page_size=5,
        )
        assert result.total == 0
        assert result.page == 2


class TestCreateNewTemplate:
    """Tests for create_new_template."""

    @pytest.mark.asyncio
    @patch("src.service.template_service.create_template", new_callable=AsyncMock)
    async def test_creates_template(self, mock_create: AsyncMock) -> None:
        tpl = _make_template_mock()
        mock_create.return_value = tpl
        data = TemplateCreate(name="Test", category="AI/ML")
        result = await create_new_template(AsyncMock(), data, uuid.uuid4())
        assert result is tpl
        mock_create.assert_awaited_once()


class TestUpdateTemplate:
    """Tests for update_template."""

    @pytest.mark.asyncio
    @patch("src.service.template_service.update_template_metadata", new_callable=AsyncMock)
    @patch("src.service.template_service.get_template_by_id", new_callable=AsyncMock)
    async def test_updates_template(
        self, mock_get: AsyncMock, mock_update: AsyncMock
    ) -> None:
        tpl = _make_template_mock()
        mock_get.return_value = tpl
        updated = _make_template_mock(name="Updated")
        mock_update.return_value = updated
        data = TemplateUpdate(name="Updated")
        result = await update_template(AsyncMock(), tpl.id, data)
        assert result.name == "Updated"


class TestUpdateStages:
    """Tests for update_stages."""

    @pytest.mark.asyncio
    @patch("src.service.template_service.replace_stages", new_callable=AsyncMock)
    @patch("src.service.template_service.get_template_by_id", new_callable=AsyncMock)
    async def test_replaces_stages(
        self, mock_get: AsyncMock, mock_replace: AsyncMock
    ) -> None:
        tpl = _make_template_mock()
        mock_get.return_value = tpl
        mock_replace.return_value = [MagicMock()]
        stages_data = [{"name": "Stage 1", "sort_order": 1}]
        result = await update_stages(AsyncMock(), tpl.id, stages_data)
        assert len(result) == 1


class TestRemoveTemplate:
    """Tests for remove_template."""

    @pytest.mark.asyncio
    @patch("src.service.template_service.delete_template", new_callable=AsyncMock)
    @patch("src.service.template_service.get_template_by_id", new_callable=AsyncMock)
    async def test_deletes_template(
        self, mock_get: AsyncMock, mock_delete: AsyncMock
    ) -> None:
        tpl = _make_template_mock()
        mock_get.return_value = tpl
        await remove_template(AsyncMock(), tpl.id)
        mock_delete.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("src.service.template_service.get_template_by_id", new_callable=AsyncMock)
    async def test_raises_when_not_found(self, mock_get: AsyncMock) -> None:
        mock_get.return_value = None
        with pytest.raises(TemplateNotFoundError):
            await remove_template(AsyncMock(), uuid.uuid4())


class TestCountFields:
    """Tests for _count_fields helper."""

    def test_counts_nested_fields(self) -> None:
        field1 = MagicMock()
        field2 = MagicMock()
        field3 = MagicMock()
        sec1 = MagicMock()
        sec1.fields = [field1, field2]
        sec2 = MagicMock()
        sec2.fields = [field3]
        stage = MagicMock()
        stage.sections = [sec1, sec2]
        tpl = _make_template_mock(stages=[stage])
        assert _count_fields(tpl) == 3

    def test_no_stages(self) -> None:
        tpl = _make_template_mock(stages=[])
        assert _count_fields(tpl) == 0

    def test_none_stages(self) -> None:
        tpl = _make_template_mock()
        tpl.stages = None
        assert _count_fields(tpl) == 0

    def test_stage_no_sections(self) -> None:
        stage = MagicMock()
        stage.sections = None
        tpl = _make_template_mock(stages=[stage])
        # hasattr will return True for MagicMock but sections is None
        assert _count_fields(tpl) == 0

    def test_section_no_fields(self) -> None:
        sec = MagicMock()
        sec.fields = None
        stage = MagicMock()
        stage.sections = [sec]
        tpl = _make_template_mock(stages=[stage])
        assert _count_fields(tpl) == 0

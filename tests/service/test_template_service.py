"""Tests for template service business logic."""
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.types.enums import FailAction, TemplateStatus
from src.types.template import (
    ScoringStageInput,
    ScoringUpdate,
    TemplateCreate,
    TemplateUpdate,
)
from src.service.template_service import (
    TemplateNotFoundError,
    TemplateValidationError,
    _to_list_item,
    _validate_publishable,
)


def _make_template(
    name: str = "Test",
    category: str = "AI/ML",
    status: str = "draft",
    stages: list | None = None,
    tags: list | None = None,
) -> MagicMock:
    """Create a mock Template object."""
    t = MagicMock()
    t.id = uuid.uuid4()
    t.name = name
    t.category = category
    t.description = "A test template"
    t.icon = "psychology"
    t.theme_color = "#5F2CFF"
    t.status = status
    t.version = 1
    t.created_by = uuid.uuid4()
    t.created_at = "2026-01-01T00:00:00"
    t.updated_at = "2026-01-01T00:00:00"
    t.stages = stages or []
    t.tags = tags or []
    return t


class TestToListItem:
    """Tests for _to_list_item helper."""

    def test_basic_conversion(self) -> None:
        """Converts template to list item."""
        template = _make_template()
        item = _to_list_item(template)
        assert item.name == "Test"
        assert item.category == "AI/ML"
        assert item.stage_count == 0
        assert item.field_count == 0

    def test_with_stages(self) -> None:
        """Counts stages correctly."""
        stage1 = MagicMock()
        stage1.sections = []
        stage2 = MagicMock()
        stage2.sections = []
        template = _make_template(stages=[stage1, stage2])
        item = _to_list_item(template)
        assert item.stage_count == 2

    def test_with_tags(self) -> None:
        """Extracts tag strings."""
        tag1 = MagicMock()
        tag1.tag = "ai"
        tag2 = MagicMock()
        tag2.tag = "ml"
        template = _make_template(tags=[tag1, tag2])
        item = _to_list_item(template)
        assert item.tags == ["ai", "ml"]

    def test_counts_fields(self) -> None:
        """Counts fields across sections."""
        field1 = MagicMock()
        field2 = MagicMock()
        section = MagicMock()
        section.fields = [field1, field2]
        stage = MagicMock()
        stage.sections = [section]
        template = _make_template(stages=[stage])
        item = _to_list_item(template)
        assert item.field_count == 2


class TestValidatePublishable:
    """Tests for _validate_publishable."""

    def test_no_stages_raises(self) -> None:
        """Template with no stages cannot publish."""
        template = _make_template(stages=[])
        with pytest.raises(TemplateValidationError, match="at least one stage"):
            _validate_publishable(template)

    def test_with_stages_passes(self) -> None:
        """Template with stages can publish."""
        stage = MagicMock()
        template = _make_template(stages=[stage])
        _validate_publishable(template)


class TestTemplateCreate:
    """Tests for TemplateCreate validation."""

    def test_valid_create_payload(self) -> None:
        """Valid payload works."""
        data = TemplateCreate(
            name="AI Eval",
            category="AI/ML Solutions",
            description="Test desc",
            tags=["ai"],
        )
        assert data.name == "AI Eval"

    def test_scoring_weight_validation(self) -> None:
        """Scoring weights must be 0-100."""
        sid = uuid.uuid4()
        data = ScoringUpdate(
            stages=[
                ScoringStageInput(
                    stage_id=sid,
                    weight_pct=100.0,
                    fail_action=FailAction.WARN,
                )
            ]
        )
        assert data.stages[0].weight_pct == 100.0

"""Tests for template Pydantic schemas."""
import uuid

import pytest
from pydantic import ValidationError

from src.types.enums import FailAction, FieldType, TemplateStatus
from src.types.template import (
    FieldOptionSchema,
    FieldsUpdate,
    FieldsUpdateStage,
    ScoringStageInput,
    ScoringUpdate,
    StageInput,
    StagesUpdate,
    TemplateCreate,
    TemplateFieldSchema,
    TemplateListItem,
    TemplateListResponse,
    TemplateResponse,
    TemplateSectionSchema,
    TemplateStageSchema,
    TemplateTagSchema,
    TemplateUpdate,
)


class TestTemplateCreate:
    """Tests for TemplateCreate schema."""

    def test_valid_create(self) -> None:
        """Valid creation payload passes validation."""
        data = TemplateCreate(
            name="AI/ML Eval",
            category="AI/ML Solutions",
            description="Test description",
            icon="psychology",
            theme_color="#02F576",
            tags=["ai", "ml"],
        )
        assert data.name == "AI/ML Eval"
        assert data.category == "AI/ML Solutions"
        assert data.tags == ["ai", "ml"]

    def test_name_required(self) -> None:
        """Name is required."""
        with pytest.raises(ValidationError):
            TemplateCreate(name="", category="AI/ML")

    def test_category_required(self) -> None:
        """Category is required."""
        with pytest.raises(ValidationError):
            TemplateCreate(name="Test", category="")

    def test_description_max_500(self) -> None:
        """Description max 500 chars."""
        with pytest.raises(ValidationError):
            TemplateCreate(
                name="Test",
                category="AI/ML",
                description="x" * 501,
            )

    def test_defaults(self) -> None:
        """Optional fields default correctly."""
        data = TemplateCreate(name="T", category="C")
        assert data.description is None
        assert data.icon is None
        assert data.tags == []


class TestTemplateUpdate:
    """Tests for TemplateUpdate schema."""

    def test_partial_update(self) -> None:
        """Can update only name."""
        data = TemplateUpdate(name="New Name")
        assert data.name == "New Name"
        assert data.category is None

    def test_all_none_allowed(self) -> None:
        """Empty update is allowed."""
        data = TemplateUpdate()
        assert data.name is None


class TestStagesUpdate:
    """Tests for StagesUpdate schema."""

    def test_valid_stages(self) -> None:
        """Valid stages pass."""
        data = StagesUpdate(
            stages=[
                StageInput(name="Desirable", sort_order=1),
                StageInput(name="Feasible", sort_order=2),
            ]
        )
        assert len(data.stages) == 2

    def test_stage_name_required(self) -> None:
        """Stage name is required."""
        with pytest.raises(ValidationError):
            StageInput(name="", sort_order=1)


class TestScoringUpdate:
    """Tests for ScoringUpdate schema."""

    def test_valid_scoring(self) -> None:
        """Valid scoring passes."""
        sid = uuid.uuid4()
        data = ScoringUpdate(
            stages=[
                ScoringStageInput(
                    stage_id=sid,
                    weight_pct=50.0,
                    min_pass_score=60.0,
                    fail_action=FailAction.BLOCK,
                )
            ]
        )
        assert data.stages[0].weight_pct == 50.0

    def test_weight_pct_bounds(self) -> None:
        """Weight must be 0-100."""
        with pytest.raises(ValidationError):
            ScoringStageInput(
                stage_id=uuid.uuid4(),
                weight_pct=101.0,
            )


class TestFieldSchemas:
    """Tests for field-related schemas."""

    def test_field_option(self) -> None:
        """FieldOptionSchema works."""
        opt = FieldOptionSchema(label="Healthcare", value="healthcare", score=10.0)
        assert opt.label == "Healthcare"

    def test_template_field(self) -> None:
        """TemplateFieldSchema with options."""
        field = TemplateFieldSchema(
            field_key="industry",
            label="Industry",
            field_type=FieldType.SINGLE_SELECT,
            is_mandatory=True,
            is_scoring=True,
            options=[
                FieldOptionSchema(label="HC", value="hc", score=10),
            ],
        )
        assert field.field_type == FieldType.SINGLE_SELECT
        assert len(field.options) == 1


class TestTemplateResponse:
    """Tests for TemplateResponse schema."""

    def test_full_response(self) -> None:
        """Full template response with stages."""
        resp = TemplateResponse(
            id=uuid.uuid4(),
            name="Test",
            category="AI/ML",
            status=TemplateStatus.DRAFT,
            version=1,
            created_by=uuid.uuid4(),
            tags=[TemplateTagSchema(tag="ai")],
            stages=[
                TemplateStageSchema(
                    name="Desirable",
                    sort_order=1,
                )
            ],
        )
        assert resp.status == TemplateStatus.DRAFT
        assert len(resp.stages) == 1


class TestTemplateListResponse:
    """Tests for TemplateListResponse."""

    def test_paginated_list(self) -> None:
        """Paginated response works."""
        resp = TemplateListResponse(
            items=[],
            total=0,
            page=1,
            page_size=10,
        )
        assert resp.total == 0

"""Pydantic schemas for template management."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.types.base import BaseSchema, IdentifiedModel, TimestampMixin
from src.types.enums import FailAction, FieldType, TemplateStatus


class FieldOptionSchema(BaseSchema):
    """Schema for a field option (select-type fields)."""

    id: uuid.UUID | None = None
    label: str
    value: str
    score: float = 0.0
    sort_order: int = 0


class TemplateFieldSchema(BaseSchema):
    """Schema for a template field."""

    id: uuid.UUID | None = None
    field_key: str
    label: str
    field_type: FieldType
    help_text: str | None = None
    is_mandatory: bool = False
    is_scoring: bool = False
    sort_order: int = 0
    options: list[FieldOptionSchema] = Field(default_factory=list)


class TemplateSectionSchema(BaseSchema):
    """Schema for a template section."""

    id: uuid.UUID | None = None
    name: str
    sort_order: int = 0
    fields: list[TemplateFieldSchema] = Field(default_factory=list)


class TemplateStageSchema(BaseSchema):
    """Schema for a template stage."""

    id: uuid.UUID | None = None
    name: str
    sort_order: int = 0
    weight_pct: float = 0.0
    min_pass_score: float | None = None
    fail_action: FailAction = FailAction.WARN
    sections: list[TemplateSectionSchema] = Field(default_factory=list)


class TemplateTagSchema(BaseSchema):
    """Schema for a template tag."""

    id: uuid.UUID | None = None
    tag: str


class TemplateCreate(BaseModel):
    """Payload for creating a template (Step 1)."""

    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    icon: str | None = Field(None, max_length=50)
    theme_color: str | None = Field(None, max_length=7)
    tags: list[str] = Field(default_factory=list)


class TemplateUpdate(BaseModel):
    """Payload for updating template metadata."""

    name: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    icon: str | None = Field(None, max_length=50)
    theme_color: str | None = Field(None, max_length=7)
    tags: list[str] | None = None


class StageInput(BaseModel):
    """Input for a single stage in Step 2."""

    name: str = Field(..., min_length=1, max_length=100)
    sort_order: int


class StagesUpdate(BaseModel):
    """Payload for updating stages (Step 2)."""

    stages: list[StageInput]


class FieldsUpdateStage(BaseModel):
    """Stage with sections/fields for Step 3 update."""

    stage_id: uuid.UUID
    sections: list[TemplateSectionSchema]


class FieldsUpdate(BaseModel):
    """Payload for bulk fields update (Step 3)."""

    stages: list[FieldsUpdateStage]


class ScoringStageInput(BaseModel):
    """Scoring config for a single stage (Step 4)."""

    stage_id: uuid.UUID
    weight_pct: float = Field(..., ge=0, le=100)
    min_pass_score: float | None = Field(None, ge=0, le=100)
    fail_action: FailAction = FailAction.WARN


class ScoringUpdate(BaseModel):
    """Payload for scoring update (Step 4)."""

    stages: list[ScoringStageInput]


class TemplateResponse(BaseSchema, TimestampMixin):
    """Template response with all nested data."""

    id: uuid.UUID
    name: str
    category: str
    description: str | None = None
    icon: str | None = None
    theme_color: str | None = None
    status: TemplateStatus
    version: int
    created_by: uuid.UUID
    tags: list[TemplateTagSchema] = Field(default_factory=list)
    stages: list[TemplateStageSchema] = Field(default_factory=list)


class TemplateListItem(BaseSchema):
    """Lightweight template for list views."""

    id: uuid.UUID
    name: str
    category: str
    description: str | None = None
    icon: str | None = None
    theme_color: str | None = None
    status: TemplateStatus
    version: int
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    stage_count: int = 0
    field_count: int = 0
    tags: list[str] = Field(default_factory=list)


class TemplateListResponse(BaseModel):
    """Paginated list of templates."""

    items: list[TemplateListItem]
    total: int
    page: int
    page_size: int

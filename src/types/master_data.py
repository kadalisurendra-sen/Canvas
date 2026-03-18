"""Pydantic schemas for master data categories and values."""
import uuid
from typing import Optional

from pydantic import Field

from src.types.base import BaseSchema


class CategoryOut(BaseSchema):
    """Category with item count for listing."""

    id: uuid.UUID
    name: str
    display_name: str
    icon: Optional[str] = None
    sort_order: int
    item_count: int = 0


class ValueOut(BaseSchema):
    """Master data value for API response."""

    id: uuid.UUID
    value: str
    label: str
    severity: Optional[str] = None
    description: Optional[str] = None
    is_active: bool = True
    sort_order: int


class ValueCreate(BaseSchema):
    """Schema for creating a master data value."""

    value: str = Field(..., min_length=1, max_length=200)
    label: str = Field(..., min_length=1, max_length=200)
    severity: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)


class ValueUpdate(BaseSchema):
    """Schema for updating a master data value."""

    value: Optional[str] = Field(default=None, max_length=200)
    label: Optional[str] = Field(default=None, max_length=200)
    severity: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class ReorderRequest(BaseSchema):
    """Schema for reorder request."""

    value_ids: list[uuid.UUID]


class PaginatedValues(BaseSchema):
    """Paginated response for master data values."""

    items: list[ValueOut]
    total: int
    page: int
    page_size: int


class ImportResult(BaseSchema):
    """CSV import result."""

    imported: int
    skipped: int
    errors: list[dict[str, str | int]]

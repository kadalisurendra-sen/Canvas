"""Tests for master data type schemas."""
import uuid

import pytest

from src.types.master_data import (
    CategoryOut,
    ImportResult,
    PaginatedValues,
    ReorderRequest,
    ValueCreate,
    ValueOut,
    ValueUpdate,
)


def test_category_out_from_dict() -> None:
    """CategoryOut should parse from a dict with item_count."""
    data = {
        "id": uuid.uuid4(),
        "name": "risk_categories",
        "display_name": "Risk Categories",
        "icon": "gpp_maybe",
        "sort_order": 1,
        "item_count": 14,
    }
    cat = CategoryOut(**data)
    assert cat.display_name == "Risk Categories"
    assert cat.item_count == 14


def test_value_create_requires_value_and_label() -> None:
    """ValueCreate must have value and label."""
    v = ValueCreate(value="test_val", label="Test Value")
    assert v.value == "test_val"
    assert v.severity is None


def test_value_create_rejects_empty_value() -> None:
    """ValueCreate should reject empty value string."""
    with pytest.raises(Exception):
        ValueCreate(value="", label="Test")


def test_value_update_allows_partial() -> None:
    """ValueUpdate should allow partial updates."""
    u = ValueUpdate(label="New Label")
    assert u.label == "New Label"
    assert u.value is None
    assert u.is_active is None


def test_reorder_request_accepts_uuid_list() -> None:
    """ReorderRequest should accept a list of UUIDs."""
    ids = [uuid.uuid4(), uuid.uuid4()]
    req = ReorderRequest(value_ids=ids)
    assert len(req.value_ids) == 2


def test_paginated_values_structure() -> None:
    """PaginatedValues should have items, total, page, page_size."""
    pv = PaginatedValues(items=[], total=0, page=1, page_size=10)
    assert pv.total == 0
    assert pv.items == []


def test_import_result_structure() -> None:
    """ImportResult should include imported, skipped, errors."""
    ir = ImportResult(imported=5, skipped=2, errors=[])
    assert ir.imported == 5
    assert ir.skipped == 2


def test_value_out_model_validates() -> None:
    """ValueOut should validate from ORM-like attributes."""
    data = {
        "id": uuid.uuid4(),
        "value": "data_privacy",
        "label": "Data Privacy",
        "severity": "high",
        "description": "GDPR compliance",
        "is_active": True,
        "sort_order": 1,
    }
    v = ValueOut(**data)
    assert v.severity == "high"

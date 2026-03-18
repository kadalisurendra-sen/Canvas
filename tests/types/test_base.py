"""Tests for base Pydantic models."""
import uuid

from src.types.base import BaseSchema, IdentifiedModel, TimestampMixin


class TestBaseSchema:
    """Tests for BaseSchema."""

    def test_from_attributes_enabled(self) -> None:
        assert BaseSchema.model_config.get("from_attributes") is True


class TestIdentifiedModel:
    """Tests for IdentifiedModel."""

    def test_default_uuid_generated(self) -> None:
        model = IdentifiedModel()
        assert isinstance(model.id, uuid.UUID)

    def test_two_instances_have_different_ids(self) -> None:
        a = IdentifiedModel()
        b = IdentifiedModel()
        assert a.id != b.id


class TestTimestampMixin:
    """Tests for TimestampMixin."""

    def test_timestamps_are_set(self) -> None:
        model = TimestampMixin()
        assert model.created_at is not None
        assert model.updated_at is not None

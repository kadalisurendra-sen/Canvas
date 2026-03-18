"""Base Pydantic models shared across the application."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseModel):
    """Mixin for created_at / updated_at timestamps."""

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IdentifiedModel(BaseSchema):
    """Base model with a UUID primary key."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)

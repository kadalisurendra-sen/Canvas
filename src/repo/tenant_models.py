"""SQLAlchemy models for tenant databases."""
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.repo.database import Base


class Template(Base):
    """Evaluation template model."""

    __tablename__ = "templates"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    theme_color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="draft"
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1"
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default="now()"
    )

    stages: Mapped[list["TemplateStage"]] = relationship(
        back_populates="template", cascade="all, delete-orphan"
    )
    tags: Mapped[list["TemplateTag"]] = relationship(
        back_populates="template", cascade="all, delete-orphan"
    )

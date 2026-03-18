"""Extended tenant models — stages, sections, fields, options."""
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
from src.repo.tenant_models import Template


class TemplateTag(Base):
    """Search tag for a template."""

    __tablename__ = "template_tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag: Mapped[str] = mapped_column(String(50), nullable=False)

    template: Mapped["Template"] = relationship(back_populates="tags")


class TemplateStage(Base):
    """Evaluation stage within a template."""

    __tablename__ = "template_stages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    weight_pct: Mapped[float | None] = mapped_column(
        Numeric(5, 2), server_default="0"
    )
    min_pass_score: Mapped[float | None] = mapped_column(
        Numeric(5, 2), nullable=True
    )
    fail_action: Mapped[str | None] = mapped_column(
        String(10), server_default="warn"
    )

    template: Mapped["Template"] = relationship(back_populates="stages")
    sections: Mapped[list["TemplateSection"]] = relationship(
        back_populates="stage", cascade="all, delete-orphan"
    )


class TemplateSection(Base):
    """Section within a template stage."""

    __tablename__ = "template_sections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("template_stages.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    stage: Mapped["TemplateStage"] = relationship(back_populates="sections")
    fields: Mapped[list["TemplateField"]] = relationship(
        back_populates="section", cascade="all, delete-orphan"
    )


class TemplateField(Base):
    """Field within a template section."""

    __tablename__ = "template_fields"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    section_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("template_sections.id", ondelete="CASCADE"),
        nullable=False,
    )
    field_key: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    field_type: Mapped[str] = mapped_column(String(30), nullable=False)
    help_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    is_scoring: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    section: Mapped["TemplateSection"] = relationship(back_populates="fields")
    options: Mapped[list["FieldOption"]] = relationship(
        back_populates="field", cascade="all, delete-orphan"
    )


class FieldOption(Base):
    """Option for a select-type template field."""

    __tablename__ = "field_options"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    field_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("template_fields.id", ondelete="CASCADE"),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[str] = mapped_column(String(200), nullable=False)
    score: Mapped[float | None] = mapped_column(
        Numeric(5, 2), server_default="0"
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)

    field: Mapped["TemplateField"] = relationship(back_populates="options")

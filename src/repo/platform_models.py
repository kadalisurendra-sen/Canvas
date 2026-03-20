"""SQLAlchemy models for the platform database (tenants, tenant_plans)."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.repo.database import Base


class Tenant(Base):
    """Tenant record in the platform database."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    schema_name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    keycloak_realm: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True
    )
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(
        String(50), nullable=False, server_default="UTC"
    )
    default_language: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="en"
    )
    primary_color: Mapped[str | None] = mapped_column(
        String(7), server_default="#5F2CFF"
    )
    favicon_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    font_family: Mapped[str | None] = mapped_column(
        String(50), server_default="Montserrat"
    )
    email_signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_currency: Mapped[str] = mapped_column(
        String(10), nullable=False, server_default="USD"
    )
    standard_roi_period: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="3 Years"
    )
    min_feasibility_threshold: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="65"
    )
    required_ethics_level: Mapped[str] = mapped_column(
        String(50), nullable=False,
        server_default="Level 3 - Enterprise Standard",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default="now()"
    )

    plans: Mapped[list["TenantPlan"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )


class TenantPlan(Base):
    """Tenant subscription plan record."""

    __tablename__ = "tenant_plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False
    )
    plan_name: Mapped[str] = mapped_column(String(50), nullable=False)
    max_users: Mapped[int] = mapped_column(Integer, nullable=False)
    max_templates: Mapped[int] = mapped_column(Integer, nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="plans")

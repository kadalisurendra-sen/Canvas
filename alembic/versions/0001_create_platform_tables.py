"""Create platform tables (tenants and tenant_plans).

Revision ID: 0001
Revises: None
Create Date: 2026-03-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column(
            "keycloak_realm", sa.String(100), nullable=False, unique=True
        ),
        sa.Column("db_name", sa.String(100), nullable=False, unique=True),
        sa.Column(
            "db_host",
            sa.String(255),
            nullable=False,
            server_default="localhost",
        ),
        sa.Column(
            "db_port", sa.Integer, nullable=False, server_default="5432"
        ),
        sa.Column("logo_url", sa.Text, nullable=True),
        sa.Column(
            "timezone", sa.String(50), nullable=False, server_default="UTC"
        ),
        sa.Column(
            "default_language",
            sa.String(10),
            nullable=False,
            server_default="en",
        ),
        sa.Column(
            "primary_color", sa.String(7), server_default="#5F2CFF"
        ),
        sa.Column("favicon_url", sa.Text, nullable=True),
        sa.Column(
            "font_family", sa.String(50), server_default="Montserrat"
        ),
        sa.Column("email_signature", sa.Text, nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default="true",
        ),
        sa.Column(
            "created_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "tenant_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id"),
            nullable=False,
        ),
        sa.Column("plan_name", sa.String(50), nullable=False),
        sa.Column("max_users", sa.Integer, nullable=False),
        sa.Column("max_templates", sa.Integer, nullable=False),
        sa.Column("valid_from", sa.DateTime, nullable=False),
        sa.Column("valid_to", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("tenant_plans")
    op.drop_table("tenants")

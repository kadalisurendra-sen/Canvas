"""Migrate to schema-per-tenant architecture.

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-18

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add schema_name column to tenants
    op.add_column("tenants", sa.Column("schema_name", sa.String(100), nullable=True))

    # Remove old db connection columns
    op.drop_column("tenants", "db_name")
    op.drop_column("tenants", "db_host")
    op.drop_column("tenants", "db_port")

    # Set schema_name from slug for existing rows
    op.execute("UPDATE tenants SET schema_name = 'tenant_' || slug WHERE schema_name IS NULL")

    # Make schema_name NOT NULL and UNIQUE
    op.alter_column("tenants", "schema_name", nullable=False)
    op.create_unique_constraint("uq_tenants_schema_name", "tenants", ["schema_name"])


def downgrade() -> None:
    op.drop_constraint("uq_tenants_schema_name", "tenants", type_="unique")
    op.drop_column("tenants", "schema_name")
    op.add_column("tenants", sa.Column("db_name", sa.String(100), nullable=True))
    op.add_column("tenants", sa.Column("db_host", sa.String(255), server_default="localhost"))
    op.add_column("tenants", sa.Column("db_port", sa.Integer, server_default="5432"))

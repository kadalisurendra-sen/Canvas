"""Tests for platform database SQLAlchemy models."""
from src.repo.platform_models import Tenant, TenantPlan


class TestTenantModel:
    """Tests for the Tenant SQLAlchemy model."""

    def test_tenant_tablename(self) -> None:
        assert Tenant.__tablename__ == "tenants"

    def test_tenant_has_required_columns(self) -> None:
        columns = {c.name for c in Tenant.__table__.columns}
        expected = {
            "id", "name", "slug", "keycloak_realm", "db_name",
            "db_host", "db_port", "logo_url", "timezone",
            "default_language", "primary_color", "favicon_url",
            "font_family", "email_signature", "is_active",
            "created_at", "updated_at",
        }
        assert expected.issubset(columns)

    def test_tenant_name_is_unique(self) -> None:
        name_col = Tenant.__table__.c.name
        assert name_col.unique is True

    def test_tenant_slug_is_unique(self) -> None:
        slug_col = Tenant.__table__.c.slug
        assert slug_col.unique is True


class TestTenantPlanModel:
    """Tests for the TenantPlan SQLAlchemy model."""

    def test_tenant_plan_tablename(self) -> None:
        assert TenantPlan.__tablename__ == "tenant_plans"

    def test_tenant_plan_has_required_columns(self) -> None:
        columns = {c.name for c in TenantPlan.__table__.columns}
        expected = {
            "id", "tenant_id", "plan_name", "max_users",
            "max_templates", "valid_from", "valid_to",
        }
        assert expected.issubset(columns)

    def test_tenant_plan_has_foreign_key(self) -> None:
        fks = TenantPlan.__table__.c.tenant_id.foreign_keys
        assert len(fks) == 1
        fk = next(iter(fks))
        assert str(fk.column) == "tenants.id"

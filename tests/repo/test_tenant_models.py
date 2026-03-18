"""Tests for tenant database SQLAlchemy models."""
from src.repo.tenant_models import Template
from src.repo.tenant_models_ext import (
    FieldOption,
    TemplateField,
    TemplateSection,
    TemplateStage,
    TemplateTag,
)
from src.repo.master_data_models import (
    AuditLog,
    MasterDataCategory,
    MasterDataValue,
)


class TestTemplateModel:
    """Tests for the Template model."""

    def test_tablename(self) -> None:
        assert Template.__tablename__ == "templates"

    def test_has_required_columns(self) -> None:
        columns = {c.name for c in Template.__table__.columns}
        expected = {
            "id", "name", "category", "description", "icon",
            "theme_color", "status", "version", "created_by",
            "created_at", "updated_at",
        }
        assert expected.issubset(columns)


class TestTemplateStageModel:
    """Tests for the TemplateStage model."""

    def test_tablename(self) -> None:
        assert TemplateStage.__tablename__ == "template_stages"

    def test_has_weight_and_scoring_columns(self) -> None:
        columns = {c.name for c in TemplateStage.__table__.columns}
        assert "weight_pct" in columns
        assert "min_pass_score" in columns
        assert "fail_action" in columns


class TestTemplateSectionModel:
    """Tests for the TemplateSection model."""

    def test_tablename(self) -> None:
        assert TemplateSection.__tablename__ == "template_sections"


class TestTemplateFieldModel:
    """Tests for the TemplateField model."""

    def test_tablename(self) -> None:
        assert TemplateField.__tablename__ == "template_fields"

    def test_has_field_type_column(self) -> None:
        columns = {c.name for c in TemplateField.__table__.columns}
        assert "field_type" in columns
        assert "is_mandatory" in columns
        assert "is_scoring" in columns


class TestFieldOptionModel:
    """Tests for the FieldOption model."""

    def test_tablename(self) -> None:
        assert FieldOption.__tablename__ == "field_options"

    def test_has_score_column(self) -> None:
        columns = {c.name for c in FieldOption.__table__.columns}
        assert "score" in columns


class TestTemplateTagModel:
    """Tests for the TemplateTag model."""

    def test_tablename(self) -> None:
        assert TemplateTag.__tablename__ == "template_tags"


class TestMasterDataCategoryModel:
    """Tests for the MasterDataCategory model."""

    def test_tablename(self) -> None:
        assert MasterDataCategory.__tablename__ == "master_data_categories"


class TestMasterDataValueModel:
    """Tests for the MasterDataValue model."""

    def test_tablename(self) -> None:
        assert MasterDataValue.__tablename__ == "master_data_values"

    def test_has_severity_column(self) -> None:
        columns = {c.name for c in MasterDataValue.__table__.columns}
        assert "severity" in columns


class TestAuditLogModel:
    """Tests for the AuditLog model."""

    def test_tablename(self) -> None:
        assert AuditLog.__tablename__ == "audit_logs"

    def test_has_event_type_column(self) -> None:
        columns = {c.name for c in AuditLog.__table__.columns}
        assert "event_type" in columns
        assert "action" in columns
        assert "ip_address" in columns

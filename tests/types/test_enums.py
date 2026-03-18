"""Tests for domain enumerations."""
from src.types.enums import (
    EventType,
    FailAction,
    FieldType,
    Severity,
    TemplateStatus,
    UserRole,
)


class TestUserRole:
    """Tests for the UserRole enum."""

    def test_all_roles_exist(self) -> None:
        assert UserRole.SYSTEM_ADMIN == "system_admin"
        assert UserRole.ADMIN == "admin"
        assert UserRole.CONTRIBUTOR == "contributor"
        assert UserRole.VIEWER == "viewer"

    def test_role_count(self) -> None:
        assert len(UserRole) == 4

    def test_role_is_string(self) -> None:
        assert isinstance(UserRole.ADMIN, str)


class TestTemplateStatus:
    """Tests for the TemplateStatus enum."""

    def test_all_statuses_exist(self) -> None:
        assert TemplateStatus.DRAFT == "draft"
        assert TemplateStatus.PUBLISHED == "published"
        assert TemplateStatus.ARCHIVED == "archived"

    def test_status_count(self) -> None:
        assert len(TemplateStatus) == 3


class TestFieldType:
    """Tests for the FieldType enum."""

    def test_all_types_exist(self) -> None:
        assert FieldType.TEXT_SHORT == "text_short"
        assert FieldType.TEXT_LONG == "text_long"
        assert FieldType.SINGLE_SELECT == "single_select"
        assert FieldType.MULTI_SELECT == "multi_select"
        assert FieldType.NUMBER == "number"
        assert FieldType.DATE == "date"

    def test_type_count(self) -> None:
        assert len(FieldType) == 6


class TestEventType:
    """Tests for the EventType enum."""

    def test_all_event_types_exist(self) -> None:
        assert EventType.MANAGEMENT == "MANAGEMENT"
        assert EventType.SYSTEM == "SYSTEM"
        assert EventType.SECURITY == "SECURITY"


class TestFailAction:
    """Tests for the FailAction enum."""

    def test_all_actions_exist(self) -> None:
        assert FailAction.WARN == "warn"
        assert FailAction.BLOCK == "block"
        assert FailAction.ALLOW == "allow"


class TestSeverity:
    """Tests for the Severity enum."""

    def test_all_severities_exist(self) -> None:
        assert Severity.HIGH == "high"
        assert Severity.MEDIUM == "medium"
        assert Severity.LOW == "low"

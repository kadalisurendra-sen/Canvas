"""Domain enumerations for Helio Canvas."""
import enum


class UserRole(str, enum.Enum):
    """User roles for RBAC."""

    SYSTEM_ADMIN = "system_admin"
    ADMIN = "admin"
    CONTRIBUTOR = "contributor"
    VIEWER = "viewer"


class UserStatus(str, enum.Enum):
    """User account statuses."""

    ACTIVE = "active"
    INVITED = "invited"
    DEACTIVATED = "deactivated"


class TemplateStatus(str, enum.Enum):
    """Template lifecycle statuses."""

    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class FieldType(str, enum.Enum):
    """Supported field types for template fields."""

    TEXT_SHORT = "text_short"
    TEXT_LONG = "text_long"
    SINGLE_SELECT = "single_select"
    MULTI_SELECT = "multi_select"
    NUMBER = "number"
    DATE = "date"


class EventType(str, enum.Enum):
    """Audit log event categories."""

    MANAGEMENT = "MANAGEMENT"
    SYSTEM = "SYSTEM"
    SECURITY = "SECURITY"


class FailAction(str, enum.Enum):
    """Action taken when a stage qualification threshold is not met."""

    WARN = "warn"
    BLOCK = "block"
    ALLOW = "allow"


class Severity(str, enum.Enum):
    """Severity levels for master data values."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

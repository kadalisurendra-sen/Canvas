"""Tests for authentication types."""
import uuid

from src.types.auth import TokenPayload, UserContext
from src.types.enums import UserRole


class TestTokenPayload:
    """Tests for TokenPayload model."""

    def test_minimal_payload(self) -> None:
        payload = TokenPayload(sub="abc-123")
        assert payload.sub == "abc-123"
        assert payload.email == ""
        assert payload.roles == []

    def test_full_payload(self) -> None:
        payload = TokenPayload(
            sub="user-1",
            email="test@example.com",
            name="Test User",
            roles=[UserRole.ADMIN],
            tenant_id="tenant-1",
            exp=9999999999,
        )
        assert payload.name == "Test User"
        assert payload.roles == [UserRole.ADMIN]


class TestUserContext:
    """Tests for UserContext model."""

    def test_user_context_creation(self) -> None:
        uid = uuid.uuid4()
        tid = uuid.uuid4()
        ctx = UserContext(
            user_id=uid,
            email="admin@test.com",
            name="Admin",
            roles=[UserRole.SYSTEM_ADMIN],
            tenant_id=tid,
        )
        assert ctx.user_id == uid
        assert ctx.tenant_id == tid
        assert ctx.roles == [UserRole.SYSTEM_ADMIN]

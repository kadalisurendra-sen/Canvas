"""Tests for user service helper functions — edge cases."""
import pytest

from src.service.user_service import (
    _apply_filters,
    _calc_pages,
    _extract_name,
    _extract_role,
    _extract_status,
    _resolve_enabled,
    map_kc_user,
)
from src.types.enums import UserRole, UserStatus


class TestExtractRole:
    """Tests for _extract_role."""

    def test_valid_role(self) -> None:
        assert _extract_role({"role": ["admin"]}) == UserRole.ADMIN

    def test_empty_list_defaults_to_viewer(self) -> None:
        assert _extract_role({"role": []}) == UserRole.VIEWER

    def test_missing_role_defaults_to_viewer(self) -> None:
        assert _extract_role({}) == UserRole.VIEWER

    def test_non_list_defaults_to_viewer(self) -> None:
        assert _extract_role({"role": "admin"}) == UserRole.VIEWER

    def test_invalid_role_value(self) -> None:
        assert _extract_role({"role": ["nonexistent"]}) == UserRole.VIEWER


class TestExtractStatus:
    """Tests for _extract_status."""

    def test_disabled_returns_deactivated(self) -> None:
        assert _extract_status({"status": ["active"]}, False) == UserStatus.DEACTIVATED

    def test_active_from_attributes(self) -> None:
        assert _extract_status({"status": ["active"]}, True) == UserStatus.ACTIVE

    def test_invited_from_attributes(self) -> None:
        assert _extract_status({"status": ["invited"]}, True) == UserStatus.INVITED

    def test_empty_status_defaults_to_active(self) -> None:
        assert _extract_status({}, True) == UserStatus.ACTIVE

    def test_non_list_status_defaults(self) -> None:
        assert _extract_status({"status": "active"}, True) == UserStatus.ACTIVE

    def test_invalid_status_defaults_to_active(self) -> None:
        assert _extract_status({"status": ["unknown"]}, True) == UserStatus.ACTIVE


class TestExtractName:
    """Tests for _extract_name."""

    def test_full_name(self) -> None:
        assert _extract_name({"firstName": "Jane", "lastName": "Doe"}) == "Jane Doe"

    def test_first_only(self) -> None:
        assert _extract_name({"firstName": "Jane"}) == "Jane"

    def test_last_only(self) -> None:
        assert _extract_name({"lastName": "Doe"}) == "Doe"

    def test_fallback_to_username(self) -> None:
        assert _extract_name({"username": "jane@test.com"}) == "jane@test.com"

    def test_empty_fields(self) -> None:
        result = _extract_name({"firstName": "", "lastName": "", "username": "u1"})
        assert result == "u1"


class TestResolveEnabled:
    """Tests for _resolve_enabled."""

    def test_deactivated_returns_false(self) -> None:
        assert _resolve_enabled(UserStatus.DEACTIVATED) is False

    def test_active_returns_true(self) -> None:
        assert _resolve_enabled(UserStatus.ACTIVE) is True

    def test_invited_returns_none(self) -> None:
        assert _resolve_enabled(UserStatus.INVITED) is None

    def test_none_returns_none(self) -> None:
        assert _resolve_enabled(None) is None


class TestApplyFilters:
    """Tests for _apply_filters."""

    def _make_user(self, role: str, status: str) -> object:
        from src.types.user import UserResponse
        return UserResponse(
            id="u1", name="Test", email="t@t.com",
            role=UserRole(role), status=UserStatus(status),
        )

    def test_filter_by_role(self) -> None:
        users = [self._make_user("admin", "active"), self._make_user("viewer", "active")]
        result = _apply_filters(users, "admin", "")
        assert len(result) == 1

    def test_filter_by_status(self) -> None:
        users = [self._make_user("admin", "active"), self._make_user("admin", "invited")]
        result = _apply_filters(users, "", "invited")
        assert len(result) == 1

    def test_both_filters(self) -> None:
        users = [
            self._make_user("admin", "active"),
            self._make_user("admin", "invited"),
            self._make_user("viewer", "active"),
        ]
        result = _apply_filters(users, "admin", "active")
        assert len(result) == 1

    def test_no_filters(self) -> None:
        users = [self._make_user("admin", "active")]
        result = _apply_filters(users, "", "")
        assert len(result) == 1


class TestCalcPages:
    """Tests for _calc_pages."""

    def test_exact_division(self) -> None:
        assert _calc_pages(30, 10) == 3

    def test_remainder(self) -> None:
        assert _calc_pages(31, 10) == 4

    def test_zero_total(self) -> None:
        assert _calc_pages(0, 10) == 1

    def test_single_page(self) -> None:
        assert _calc_pages(5, 10) == 1


class TestMapKcUserEdgeCases:
    """Edge case tests for map_kc_user."""

    def test_none_attributes(self) -> None:
        kc_user = {
            "id": "u1", "email": "a@b.com", "username": "a@b.com",
            "enabled": True, "attributes": None,
        }
        user = map_kc_user(kc_user)
        assert user.role == UserRole.VIEWER
        assert user.status == UserStatus.ACTIVE

    def test_non_dict_attributes(self) -> None:
        kc_user = {
            "id": "u1", "email": "a@b.com", "username": "a@b.com",
            "enabled": True, "attributes": "invalid",
        }
        user = map_kc_user(kc_user)
        assert user.role == UserRole.VIEWER

    def test_with_last_login(self) -> None:
        kc_user = {
            "id": "u1", "email": "a@b.com", "username": "a@b.com",
            "enabled": True, "attributes": {"role": ["admin"], "status": ["active"]},
            "lastLogin": 1234567890,
        }
        user = map_kc_user(kc_user)
        assert user.last_login == "1234567890"

    def test_missing_attributes_key(self) -> None:
        kc_user = {"id": "u1", "email": "a@b.com", "username": "a@b.com", "enabled": True}
        user = map_kc_user(kc_user)
        assert user.role == UserRole.VIEWER

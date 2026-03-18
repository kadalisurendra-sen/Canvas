"""Tests for UserRepository Keycloak API client."""
import pytest

from src.repo.user_repository import (
    UserAlreadyExistsError,
    UserRepository,
    UserRepositoryError,
    build_admin_url,
    build_token_url,
    make_create_payload,
    make_deactivate_payload,
    make_update_payload,
)


class TestUserRepositoryInit:
    """Tests for repository initialization."""

    def test_init_sets_realm(self) -> None:
        repo = UserRepository(realm="test-realm")
        assert repo._realm == "test-realm"

    def test_admin_base_url(self) -> None:
        repo = UserRepository(realm="test-realm")
        assert "/admin/realms/test-realm" in repo._admin_base


class TestUserRepositoryErrors:
    """Tests for error classes."""

    def test_already_exists_is_repo_error(self) -> None:
        err = UserAlreadyExistsError("dup")
        assert isinstance(err, UserRepositoryError)

    def test_error_message(self) -> None:
        err = UserAlreadyExistsError("User exists")
        assert str(err) == "User exists"


class TestHelperFunctions:
    """Tests for module-level helper functions."""

    def test_build_admin_url(self) -> None:
        url = build_admin_url("http://kc:8080", "myrealm")
        assert url == "http://kc:8080/admin/realms/myrealm"

    def test_build_token_url(self) -> None:
        url = build_token_url("http://kc:8080", "myrealm")
        assert "openid-connect/token" in url

    def test_make_create_payload(self) -> None:
        payload = make_create_payload("a@b.com", "admin")
        assert payload["email"] == "a@b.com"
        assert payload["enabled"] is True

    def test_make_deactivate_payload(self) -> None:
        payload = make_deactivate_payload()
        assert payload["enabled"] is False

    def test_make_update_payload_role(self) -> None:
        payload = make_update_payload("admin", None)
        assert payload["attributes"] == {"role": ["admin"]}
        assert "enabled" not in payload

    def test_make_update_payload_enabled(self) -> None:
        payload = make_update_payload(None, False)
        assert payload["enabled"] is False
        assert "attributes" not in payload

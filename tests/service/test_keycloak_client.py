"""Tests for KeycloakClient URL construction."""
from src.service.keycloak_client import KeycloakClient


class TestKeycloakClientUrls:
    """Tests for Keycloak endpoint URL generation."""

    def test_issuer_url(self) -> None:
        kc = KeycloakClient()
        assert "/realms/" in kc.issuer_url

    def test_auth_url(self) -> None:
        kc = KeycloakClient()
        assert kc.auth_url.endswith("/protocol/openid-connect/auth")

    def test_token_url(self) -> None:
        kc = KeycloakClient()
        assert kc.token_url.endswith("/protocol/openid-connect/token")

    def test_jwks_url(self) -> None:
        kc = KeycloakClient()
        assert kc.jwks_url.endswith("/protocol/openid-connect/certs")

    def test_logout_url(self) -> None:
        kc = KeycloakClient()
        assert kc.logout_url.endswith("/protocol/openid-connect/logout")

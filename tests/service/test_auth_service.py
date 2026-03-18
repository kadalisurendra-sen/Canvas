"""Tests for JWT validation and auth service."""
import time
import uuid

import pytest
from jose import jwt

from src.service.auth_service import (
    AuthService,
    InvalidTokenError,
    TokenExpiredError,
)
from src.types.enums import UserRole

# RSA test key pair (for test purposes only, not a real secret)
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def _generate_test_keys() -> tuple[dict[str, str], str]:
    """Generate RSA key pair for testing JWT signing."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    public_key = private_key.public_key()
    public_numbers = public_key.public_numbers()

    import base64

    def _int_to_base64url(val: int) -> str:
        byte_length = (val.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(
            val.to_bytes(byte_length, byteorder="big")
        ).rstrip(b"=").decode("ascii")

    jwk = {
        "kty": "RSA",
        "kid": "test-key-1",
        "use": "sig",
        "alg": "RS256",
        "n": _int_to_base64url(public_numbers.n),
        "e": _int_to_base64url(public_numbers.e),
    }
    return jwk, private_pem


JWK, PRIVATE_PEM = _generate_test_keys()
JWKS = {"keys": [JWK]}

TEST_USER_ID = str(uuid.uuid4())
TEST_TENANT_ID = str(uuid.uuid4())


def _make_token(
    expired: bool = False,
    wrong_audience: bool = False,
    kid: str = "test-key-1",
) -> str:
    """Create a signed JWT for testing."""
    now = int(time.time())
    payload = {
        "sub": TEST_USER_ID,
        "email": "user@test.com",
        "name": "Test User",
        "realm_access": {"roles": ["admin"]},
        "tenant_id": TEST_TENANT_ID,
        "aud": "wrong-aud" if wrong_audience else "test-client",
        "iss": "http://localhost:8080/realms/test-realm",
        "iat": now - 60,
        "exp": now - 10 if expired else now + 3600,
    }
    return jwt.encode(
        payload, PRIVATE_PEM, algorithm="RS256", headers={"kid": kid}
    )


@pytest.fixture()
def auth_service() -> AuthService:
    """Create an AuthService with test JWKS."""
    svc = AuthService()
    svc.set_jwks(JWKS)
    return svc


class TestAuthServiceValidToken:
    """Tests for successful JWT validation."""

    def test_decode_valid_token(self, auth_service: AuthService) -> None:
        token = _make_token()
        payload = auth_service.decode_token(token)
        assert payload.sub == TEST_USER_ID
        assert payload.email == "user@test.com"
        assert UserRole.ADMIN in payload.roles

    def test_get_user_context(self, auth_service: AuthService) -> None:
        token = _make_token()
        payload = auth_service.decode_token(token)
        ctx = auth_service.get_user_context(payload)
        assert ctx.user_id == uuid.UUID(TEST_USER_ID)
        assert ctx.tenant_id == uuid.UUID(TEST_TENANT_ID)


class TestAuthServiceExpiredToken:
    """Tests for expired token rejection."""

    def test_expired_token_raises(self, auth_service: AuthService) -> None:
        token = _make_token(expired=True)
        with pytest.raises(TokenExpiredError):
            auth_service.decode_token(token)


class TestAuthServiceWrongAudience:
    """Tests for wrong audience rejection."""

    def test_wrong_audience_raises(self, auth_service: AuthService) -> None:
        token = _make_token(wrong_audience=True)
        with pytest.raises(InvalidTokenError):
            auth_service.decode_token(token)


class TestAuthServiceInvalidToken:
    """Tests for malformed token rejection."""

    def test_garbage_token_raises(self, auth_service: AuthService) -> None:
        with pytest.raises(InvalidTokenError):
            auth_service.decode_token("not.a.jwt")

    def test_missing_kid_raises(self, auth_service: AuthService) -> None:
        token = _make_token(kid="unknown-kid")
        with pytest.raises(InvalidTokenError):
            auth_service.decode_token(token)

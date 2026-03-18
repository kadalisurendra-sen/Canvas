"""Authentication and authorization types."""
import uuid

from pydantic import BaseModel, Field

from src.types.enums import UserRole


class TokenPayload(BaseModel):
    """Decoded JWT token payload."""

    sub: str
    email: str = ""
    name: str = ""
    roles: list[UserRole] = Field(default_factory=list)
    tenant_id: str = ""
    exp: int = 0


class UserContext(BaseModel):
    """Current user context extracted from JWT."""

    user_id: uuid.UUID
    email: str
    name: str
    roles: list[UserRole]
    tenant_id: uuid.UUID

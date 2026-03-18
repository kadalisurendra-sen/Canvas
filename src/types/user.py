"""User management Pydantic schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from src.types.base import BaseSchema
from src.types.enums import UserRole, UserStatus


class UserResponse(BaseSchema):
    """User data returned from API."""

    id: str
    name: str
    email: str
    role: UserRole
    status: UserStatus
    last_login: str | None = None


class UserListResponse(BaseSchema):
    """Paginated user list response."""

    users: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class InviteUserRequest(BaseModel):
    """Request body for inviting a user."""

    email: EmailStr = Field(..., min_length=3, max_length=255)
    role: UserRole = UserRole.VIEWER


class UpdateUserRequest(BaseModel):
    """Request body for updating a user."""

    role: UserRole | None = None
    status: UserStatus | None = None


class InviteUserResponse(BaseSchema):
    """Response after inviting a user."""

    id: str
    email: str
    role: UserRole
    status: UserStatus
    message: str = "Invitation sent successfully"

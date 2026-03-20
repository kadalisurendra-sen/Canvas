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
    active_count: int = 0
    deactivated_count: int = 0


class InviteUserRequest(BaseModel):
    """Request body for inviting a user."""

    email: str = Field(..., min_length=3, max_length=255)
    role: UserRole = UserRole.VIEWER
    username: str = Field("", min_length=0, max_length=100)
    password: str = Field("", min_length=0, max_length=100)
    first_name: str = Field("", min_length=0, max_length=100)
    last_name: str = Field("", min_length=0, max_length=100)


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

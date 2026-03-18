"""User management business logic."""
import logging
import math

from src.repo.user_repo_ops import (
    count_users as repo_count,
    create_user as repo_create,
    deactivate_user as repo_deactivate,
    list_users as repo_list,
    update_user as repo_update,
)
from src.repo.user_repository import (
    UserAlreadyExistsError,
    UserRepository,
    UserRepositoryError,
)
from src.types.enums import UserRole, UserStatus
from src.types.user import (
    InviteUserResponse,
    UserListResponse,
    UserResponse,
)

logger = logging.getLogger(__name__)


class UserServiceError(Exception):
    """Raised when a user service operation fails."""


class UserConflictError(UserServiceError):
    """Raised when a user already exists."""


def _extract_role(attrs: dict[str, object]) -> UserRole:
    """Extract user role from Keycloak attributes."""
    role_list = attrs.get("role", ["viewer"])
    role_str = role_list[0] if isinstance(role_list, list) and role_list else "viewer"
    try:
        return UserRole(role_str)
    except ValueError:
        return UserRole.VIEWER


def _extract_status(attrs: dict[str, object], enabled: bool) -> UserStatus:
    """Extract user status from Keycloak attributes."""
    if not enabled:
        return UserStatus.DEACTIVATED
    status_list = attrs.get("status", ["active"])
    status_str = status_list[0] if isinstance(status_list, list) and status_list else "active"
    try:
        return UserStatus(status_str)
    except ValueError:
        return UserStatus.ACTIVE


def _extract_name(kc_user: dict[str, object]) -> str:
    """Extract display name from Keycloak user data."""
    first = str(kc_user.get("firstName", ""))
    last = str(kc_user.get("lastName", ""))
    name = f"{first} {last}".strip()
    return name or str(kc_user.get("username", ""))


def map_kc_user(kc_user: dict[str, object]) -> UserResponse:
    """Map a Keycloak user representation to UserResponse."""
    attrs = kc_user.get("attributes", {}) or {}
    if not isinstance(attrs, dict):
        attrs = {}
    enabled = bool(kc_user.get("enabled", True))
    role = _extract_role(attrs)
    status = _extract_status(attrs, enabled)
    name = _extract_name(kc_user)
    last_login_ts = kc_user.get("lastLogin")
    last_login = str(last_login_ts) if last_login_ts else None
    return UserResponse(
        id=str(kc_user.get("id", "")), name=name,
        email=str(kc_user.get("email", "")),
        role=role, status=status, last_login=last_login,
    )


def _resolve_enabled(status: UserStatus | None) -> bool | None:
    """Resolve enabled flag from user status."""
    if status == UserStatus.DEACTIVATED:
        return False
    if status == UserStatus.ACTIVE:
        return True
    return None


def _apply_filters(
    users: list[UserResponse], role: str, status: str,
) -> list[UserResponse]:
    """Filter user list by role and status."""
    if role:
        users = [u for u in users if u.role.value == role]
    if status:
        users = [u for u in users if u.status.value == status]
    return users


def _calc_pages(total: int, page_size: int) -> int:
    """Calculate total number of pages."""
    return max(1, math.ceil(total / page_size))


class UserService:
    """Service for user management operations."""

    def __init__(self, repo: UserRepository) -> None:
        """Initialize with a user repository."""
        self._repo = repo

    async def list_users(
        self, search: str = "", role: str = "",
        status: str = "", page: int = 1, page_size: int = 10,
    ) -> UserListResponse:
        """List users with optional filters and pagination."""
        total = await repo_count(self._repo, search=search)
        first = (page - 1) * page_size
        raw = await repo_list(self._repo, search=search, first=first, max_results=page_size)
        users = _apply_filters([map_kc_user(u) for u in raw], role, status)
        return UserListResponse(
            users=users, total=total, page=page,
            page_size=page_size, total_pages=_calc_pages(total, page_size),
        )

    async def invite_user(self, email: str, role: UserRole) -> InviteUserResponse:
        """Invite a new user via Keycloak."""
        try:
            result = await repo_create(self._repo, email, role.value)
        except UserAlreadyExistsError as exc:
            raise UserConflictError(str(exc)) from exc
        except UserRepositoryError as exc:
            raise UserServiceError(str(exc)) from exc
        return InviteUserResponse(
            id=str(result["id"]), email=email, role=role, status=UserStatus.INVITED,
        )

    async def update_user(
        self, user_id: str, role: UserRole | None = None, status: UserStatus | None = None,
    ) -> dict[str, str]:
        """Update user role or status."""
        enabled = _resolve_enabled(status)
        role_val = role.value if role else None
        await repo_update(self._repo, user_id, role_val, enabled)
        return {"message": "User updated successfully"}

    async def deactivate_user(self, user_id: str) -> dict[str, str]:
        """Deactivate a user account."""
        await repo_deactivate(self._repo, user_id)
        return {"message": "User deactivated successfully"}

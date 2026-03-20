"""User management business logic."""
import logging
import math
import time

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


def _extract_role(
    attrs: dict[str, object],
    realm_roles: list[str] | None = None,
) -> UserRole:
    """Extract user role from realm roles or Keycloak attributes."""
    # Priority order: system_admin > admin > contributor > viewer
    priority = ["system_admin", "admin", "contributor", "viewer"]
    if realm_roles:
        for role in priority:
            if role in realm_roles:
                try:
                    return UserRole(role)
                except ValueError:
                    pass

    # Fallback to attributes
    role_list = attrs.get("role", ["viewer"])
    role_str = role_list[0] if isinstance(role_list, list) and role_list else "viewer"
    try:
        return UserRole(role_str)
    except ValueError:
        return UserRole.VIEWER


def _extract_status(
    attrs: dict[str, object],
    enabled: bool,
    kc_user: dict[str, object] | None = None,
) -> UserStatus:
    """Extract user status from Keycloak user data.

    Logic:
    - disabled → deactivated
    - enabled → active (regardless of session count)
    """
    if not enabled:
        return UserStatus.DEACTIVATED
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
    realm_roles = kc_user.get("_realm_roles")
    role = _extract_role(attrs, realm_roles if isinstance(realm_roles, list) else None)
    status = _extract_status(attrs, enabled, kc_user)
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


# Short-lived cache for Keycloak user list (avoids repeated 2s+ calls)
_user_list_cache: dict[str, tuple[list, float]] = {}
_USER_CACHE_TTL = 5  # seconds


def _invalidate_user_cache() -> None:
    """Clear user list cache after mutations."""
    _user_list_cache.clear()


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
        # Use short-lived cache for Keycloak data
        cache_key = f"{self._repo._realm}:{search}"
        cached = _user_list_cache.get(cache_key)
        if cached and cached[1] > time.monotonic():
            raw = cached[0]
        else:
            raw = await repo_list(self._repo, search=search, first=0, max_results=100)
            _user_list_cache[cache_key] = (raw, time.monotonic() + _USER_CACHE_TTL)
        mapped = [map_kc_user(u) for u in raw]

        # Overall counts (before status filter, after role filter)
        role_filtered = _apply_filters(mapped, role, "")
        active_count = sum(1 for u in role_filtered if u.status == UserStatus.ACTIVE)
        deactivated_count = sum(1 for u in role_filtered if u.status == UserStatus.DEACTIVATED)

        # Apply all filters
        all_users = _apply_filters(mapped, role, status)
        total = len(all_users)
        # Paginate after filtering
        first = (page - 1) * page_size
        users = all_users[first:first + page_size]
        return UserListResponse(
            users=users, total=total, page=page,
            page_size=page_size, total_pages=_calc_pages(total, page_size),
            active_count=active_count, deactivated_count=deactivated_count,
        )

    async def invite_user(
        self, email: str, role: UserRole,
        username: str = "", password: str = "",
        first_name: str = "", last_name: str = "",
    ) -> InviteUserResponse:
        """Invite a new user via Keycloak."""
        try:
            result = await repo_create(
                self._repo, email, role.value, username=username, password=password,
                first_name=first_name, last_name=last_name,
            )
        except UserAlreadyExistsError as exc:
            raise UserConflictError(str(exc)) from exc
        except UserRepositoryError as exc:
            raise UserServiceError(str(exc)) from exc
        _invalidate_user_cache()
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
        _invalidate_user_cache()
        return {"message": "User updated successfully"}

    async def deactivate_user(self, user_id: str) -> dict[str, str]:
        """Deactivate a user account."""
        await repo_deactivate(self._repo, user_id)
        _invalidate_user_cache()
        return {"message": "User deactivated successfully"}

    async def delete_user(self, user_id: str) -> dict[str, str]:
        """Permanently delete a user from Keycloak."""
        from src.repo.user_repo_ops import delete_user as repo_delete
        await repo_delete(self._repo, user_id)
        _invalidate_user_cache()
        return {"message": "User deleted successfully"}

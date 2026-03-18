"""User management API routes."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from src.runtime.dependencies.auth import get_current_user, require_role
from src.service.user_service import UserConflictError, UserService, UserServiceError
from src.repo.user_repository import UserRepository
from src.types.auth import UserContext
from src.types.enums import UserRole
from src.types.user import (
    InviteUserRequest,
    InviteUserResponse,
    UpdateUserRequest,
    UserListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def _get_user_service(realm: str = "helio") -> UserService:
    """Build a UserService with the given realm."""
    repo = UserRepository(realm=realm)
    return UserService(repo=repo)


def _check_self_deactivation(user_id: str, current_user: UserContext) -> None:
    """Raise 400 if user tries to deactivate themselves."""
    if user_id == str(current_user.user_id):
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")


def _raise_conflict(exc: UserConflictError) -> None:
    """Raise 409 for user conflict errors."""
    raise HTTPException(status_code=409, detail=str(exc))


def _raise_server_error(exc: UserServiceError) -> None:
    """Raise 500 for generic service errors."""
    raise HTTPException(status_code=500, detail=str(exc))


def _admin_dep():  # type: ignore[no-untyped-def]
    """Dependency that requires admin or system admin role."""
    return require_role(UserRole.SYSTEM_ADMIN, UserRole.ADMIN)


@router.get("", response_model=UserListResponse)
async def list_users(
    search: str = Query(default=""),
    role: str = Query(default=""),
    status: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user: UserContext = Depends(get_current_user),
) -> UserListResponse:
    """List users with search, filter, and pagination."""
    svc = _get_user_service()
    return await svc.list_users(
        search=search, role=role, status=status,
        page=page, page_size=page_size,
    )


def _handle_invite_error(exc: Exception) -> None:
    """Handle errors from invite operation."""
    if isinstance(exc, UserConflictError):
        _raise_conflict(exc)
    if isinstance(exc, UserServiceError):
        _raise_server_error(exc)


@router.post("/invite", response_model=InviteUserResponse)
async def invite_user(
    body: InviteUserRequest,
    user: UserContext = Depends(_admin_dep()),
) -> InviteUserResponse:
    """Invite a new user via email."""
    svc = _get_user_service()
    try:
        return await svc.invite_user(body.email, body.role)
    except UserConflictError as exc:
        _raise_conflict(exc)
    except UserServiceError as exc:
        _raise_server_error(exc)


@router.put("/{user_id}")
async def update_user(
    user_id: str, body: UpdateUserRequest,
    user: UserContext = Depends(_admin_dep()),
) -> dict[str, str]:
    """Update a user's role or status."""
    svc = _get_user_service()
    try:
        return await svc.update_user(user_id, role=body.role, status=body.status)
    except UserServiceError as exc:
        _raise_server_error(exc)


@router.delete("/{user_id}")
async def deactivate_user_route(
    user_id: str,
    user: UserContext = Depends(_admin_dep()),
) -> dict[str, str]:
    """Deactivate a user account."""
    _check_self_deactivation(user_id, user)
    svc = _get_user_service()
    try:
        return await svc.deactivate_user(user_id)
    except UserServiceError as exc:
        _raise_server_error(exc)

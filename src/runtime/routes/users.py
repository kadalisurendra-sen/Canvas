"""User management API routes."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from src.runtime.dependencies.auth import get_current_user, require_role
from src.runtime.dependencies.db import get_tenant_session
from src.repo.analytics_repository import create_audit_log
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


def _get_user_service_from_request(request: Request) -> UserService:
    """Build a UserService using the tenant's Keycloak realm."""
    realm = getattr(request.state, "tenant_realm", "helio")
    logger.info("UserService using realm: %s", realm)
    return _get_user_service(realm=realm)


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
    request: Request,
    search: str = Query(default=""),
    role: str = Query(default=""),
    status: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user: UserContext = Depends(get_current_user),
) -> UserListResponse:
    """List users with search, filter, and pagination."""
    svc = _get_user_service_from_request(request)
    return await svc.list_users(
        search=search, role=role, status=status,
        page=page, page_size=page_size,
    )


@router.post("/invite", response_model=InviteUserResponse)
async def invite_user(
    request: Request,
    body: InviteUserRequest,
    user: UserContext = Depends(_admin_dep()),
) -> InviteUserResponse:
    """Invite a new user via email."""
    svc = _get_user_service_from_request(request)
    try:
        result = await svc.invite_user(
            body.email, body.role, username=body.username, password=body.password,
            first_name=body.first_name, last_name=body.last_name,
        )

        # Audit log
        ip = request.client.host if request.client else None
        async with get_tenant_session(request) as session:
            await create_audit_log(
                session, user.user_id, user.name,
                "MANAGEMENT", "user_invited",
                details=f"Invited {body.email} as {body.role.value}",
                ip_address=ip,
            )

        return result
    except UserConflictError as exc:
        _raise_conflict(exc)
    except UserServiceError as exc:
        _raise_server_error(exc)


@router.put("/{user_id}")
async def update_user(
    request: Request,
    user_id: str, body: UpdateUserRequest,
    user: UserContext = Depends(_admin_dep()),
) -> dict[str, str]:
    """Update a user's role or status."""
    svc = _get_user_service_from_request(request)
    try:
        result = await svc.update_user(user_id, role=body.role, status=body.status)

        # Audit log
        changes = []
        if body.role:
            changes.append(f"role={body.role.value}")
        if body.status:
            changes.append(f"status={body.status.value}")
        ip = request.client.host if request.client else None
        async with get_tenant_session(request) as session:
            await create_audit_log(
                session, user.user_id, user.name,
                "MANAGEMENT", "user_updated",
                details=f"Updated user {user_id}: {', '.join(changes)}",
                ip_address=ip,
            )

        return result
    except UserServiceError as exc:
        _raise_server_error(exc)


@router.delete("/{user_id}/permanent")
async def delete_user_permanently(
    request: Request,
    user_id: str,
    user: UserContext = Depends(_admin_dep()),
) -> dict[str, str]:
    """Permanently delete a deactivated user from Keycloak."""
    _check_self_deactivation(user_id, user)
    svc = _get_user_service_from_request(request)
    try:
        result = await svc.delete_user(user_id)

        # Audit log
        ip = request.client.host if request.client else None
        async with get_tenant_session(request) as session:
            await create_audit_log(
                session, user.user_id, user.name,
                "MANAGEMENT", "user_deleted",
                details=f"Permanently deleted user {user_id}",
                ip_address=ip,
            )

        return result
    except UserServiceError as exc:
        _raise_server_error(exc)


@router.delete("/{user_id}")
async def deactivate_user_route(
    request: Request,
    user_id: str,
    user: UserContext = Depends(_admin_dep()),
) -> dict[str, str]:
    """Deactivate a user account."""
    _check_self_deactivation(user_id, user)
    svc = _get_user_service_from_request(request)
    try:
        result = await svc.deactivate_user(user_id)

        # Audit log
        ip = request.client.host if request.client else None
        async with get_tenant_session(request) as session:
            await create_audit_log(
                session, user.user_id, user.name,
                "MANAGEMENT", "user_deactivated",
                details=f"Deactivated user {user_id}",
                ip_address=ip,
            )

        return result
    except UserServiceError as exc:
        _raise_server_error(exc)

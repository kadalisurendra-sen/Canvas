"""Template management API routes — list, create, get, update, delete."""
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from src.runtime.dependencies.auth import get_current_user
from src.runtime.dependencies.db import get_tenant_session
from src.repo.analytics_repository import create_audit_log
from src.service.template_service import (
    TemplateNotFoundError,
    TemplateServiceError,
    create_new_template,
    get_template,
    get_templates,
    remove_template,
    update_template,
)
from src.types.auth import UserContext
from src.types.template import (
    TemplateCreate,
    TemplateListResponse,
    TemplateUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


@router.get("", response_model=TemplateListResponse)
async def list_templates_route(
    request: Request,
    status: str | None = Query(None),
    category: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user_context: UserContext = Depends(get_current_user),
) -> TemplateListResponse:
    """GET /api/v1/templates — list with filters."""
    try:
        async with get_tenant_session(request) as session:
            return await get_templates(
                session, status, category, search, page, page_size
            )
    except TemplateServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("", status_code=201)
async def create_template_route(
    request: Request,
    data: TemplateCreate,
    user_context: UserContext = Depends(get_current_user),
) -> dict[str, str]:
    """POST /api/v1/templates — create draft."""
    try:
        async with get_tenant_session(request) as session:
            tpl = await create_new_template(
                session, data, user_context.user_id,
            )
            tpl_id = str(tpl.id)
            # Audit log in same session before commit
            ip = request.client.host if request.client else None
            await create_audit_log(
                session, user_context.user_id, user_context.name,
                "TEMPLATE", "template_created",
                details=f"Created template '{data.name}'",
                ip_address=ip,
            )
        return {"id": tpl_id, "status": "draft"}
    except TemplateServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{template_id}")
async def get_template_route(
    request: Request,
    template_id: uuid.UUID,
    user_context: UserContext = Depends(get_current_user),
) -> dict:  # type: ignore[type-arg]
    """GET /api/v1/templates/{id}."""
    try:
        async with get_tenant_session(request) as session:
            tpl = await get_template(session, template_id)
            return _template_to_dict(tpl)
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


def _template_to_dict(tpl: "Template") -> dict:  # type: ignore[type-arg]
    """Serialize a Template ORM object to a full dict."""
    stages = []
    if tpl.stages:
        for stage in tpl.stages:
            sections = []
            if hasattr(stage, "sections") and stage.sections:
                for sec in stage.sections:
                    fields = []
                    if hasattr(sec, "fields") and sec.fields:
                        for f in sec.fields:
                            options = []
                            if hasattr(f, "options") and f.options:
                                for o in f.options:
                                    options.append({
                                        "id": str(o.id),
                                        "label": o.label,
                                        "value": o.value,
                                        "score": o.score,
                                        "sort_order": o.sort_order,
                                    })
                            fields.append({
                                "id": str(f.id),
                                "field_key": f.field_key,
                                "label": f.label,
                                "field_type": f.field_type,
                                "help_text": f.help_text,
                                "is_mandatory": f.is_mandatory,
                                "is_scoring": f.is_scoring,
                                "sort_order": f.sort_order,
                                "options": options,
                            })
                    sections.append({
                        "id": str(sec.id),
                        "name": sec.name,
                        "sort_order": sec.sort_order,
                        "fields": fields,
                    })
            stages.append({
                "id": str(stage.id),
                "name": stage.name,
                "sort_order": stage.sort_order,
                "weight_pct": stage.weight_pct,
                "min_pass_score": stage.min_pass_score,
                "fail_action": stage.fail_action,
                "sections": sections,
            })
    tags = []
    if hasattr(tpl, "tags") and tpl.tags:
        tags = [{"id": str(t.id), "tag": t.tag} for t in tpl.tags]
    return {
        "id": str(tpl.id),
        "name": tpl.name,
        "category": tpl.category,
        "description": tpl.description,
        "icon": tpl.icon,
        "theme_color": tpl.theme_color,
        "status": tpl.status,
        "version": tpl.version,
        "created_by": str(tpl.created_by),
        "created_at": tpl.created_at.isoformat() if tpl.created_at else None,
        "updated_at": tpl.updated_at.isoformat() if tpl.updated_at else None,
        "tags": tags,
        "stages": stages,
    }


@router.put("/{template_id}")
async def update_template_route(
    request: Request,
    template_id: uuid.UUID,
    data: TemplateUpdate,
    user_context: UserContext = Depends(get_current_user),
) -> dict[str, str]:
    """PUT /api/v1/templates/{id} — update metadata."""
    try:
        async with get_tenant_session(request) as session:
            tpl = await update_template(session, template_id, data)
            ip = request.client.host if request.client else None
            await create_audit_log(
                session, user_context.user_id, user_context.name,
                "TEMPLATE", "template_updated",
                details=f"Updated template {template_id}",
                ip_address=ip,
            )
            return {"id": str(tpl.id), "status": tpl.status}
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{template_id}", status_code=204)
async def delete_template_route(
    request: Request,
    template_id: uuid.UUID,
    user_context: UserContext = Depends(get_current_user),
) -> None:
    """DELETE /api/v1/templates/{id}."""
    try:
        async with get_tenant_session(request) as session:
            await remove_template(session, template_id)
            ip = request.client.host if request.client else None
            await create_audit_log(
                session, user_context.user_id, user_context.name,
                "TEMPLATE", "template_deleted",
                details=f"Deleted template {template_id}",
                ip_address=ip,
            )
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{template_id}/clone", status_code=201)
async def clone_template_route(
    request: Request,
    template_id: uuid.UUID,
    user_context: UserContext = Depends(get_current_user),
) -> dict[str, str]:
    """POST /api/v1/templates/{id}/clone — clone a template."""
    try:
        async with get_tenant_session(request) as session:
            source = await get_template(session, template_id)
            clone_data = TemplateCreate(
                name=f"{source.name} (Copy)",
                category=source.category,
                description=source.description,
                icon=source.icon,
                theme_color=source.theme_color,
                tags=[t.tag for t in source.tags] if source.tags else [],
            )
            tpl = await create_new_template(
                session, clone_data, user_context.user_id,
            )
            ip = request.client.host if request.client else None
            await create_audit_log(
                session, user_context.user_id, user_context.name,
                "TEMPLATE", "template_cloned",
                details=f"Cloned template {template_id} as '{clone_data.name}'",
                ip_address=ip,
            )
            return {"id": str(tpl.id), "status": "draft"}
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TemplateServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

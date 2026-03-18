"""Template wizard API routes — stages, fields, scoring, publish."""
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request

from src.runtime.dependencies.auth import get_current_user
from src.runtime.dependencies.db import get_tenant_session
from src.service.template_service import (
    TemplateNotFoundError,
    TemplateValidationError,
    update_stages,
)
from src.service.template_wizard_service import (
    publish_template,
    update_fields,
    update_scoring,
)
from src.types.auth import UserContext
from src.types.template import (
    FieldsUpdate,
    ScoringUpdate,
    StagesUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/templates", tags=["template-wizard"])


@router.put("/{template_id}/stages")
async def update_stages_route(
    request: Request,
    template_id: uuid.UUID,
    data: StagesUpdate,
    user_context: UserContext = Depends(get_current_user),
) -> dict[str, str]:
    """PUT /api/v1/templates/{id}/stages."""
    try:
        async with get_tenant_session(request) as session:
            stages = await update_stages(
                session, template_id,
                [s.model_dump() for s in data.stages],
            )
            return {
                "template_id": str(template_id),
                "stage_count": str(len(stages)),
            }
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{template_id}/fields")
async def update_fields_route(
    request: Request,
    template_id: uuid.UUID,
    data: FieldsUpdate,
    user_context: UserContext = Depends(get_current_user),
) -> dict[str, str]:
    """PUT /api/v1/templates/{id}/fields."""
    try:
        async with get_tenant_session(request) as session:
            tpl = await update_fields(session, template_id, data)
            return {"id": str(tpl.id), "status": tpl.status}
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.put("/{template_id}/scoring")
async def update_scoring_route(
    request: Request,
    template_id: uuid.UUID,
    data: ScoringUpdate,
    user_context: UserContext = Depends(get_current_user),
) -> dict[str, str]:
    """PUT /api/v1/templates/{id}/scoring."""
    try:
        async with get_tenant_session(request) as session:
            tpl = await update_scoring(session, template_id, data)
            return {"id": str(tpl.id), "status": tpl.status}
    except TemplateValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{template_id}/publish")
async def publish_template_route(
    request: Request,
    template_id: uuid.UUID,
    user_context: UserContext = Depends(get_current_user),
) -> dict[str, str]:
    """POST /api/v1/templates/{id}/publish."""
    try:
        async with get_tenant_session(request) as session:
            tpl = await publish_template(session, template_id)
            return {
                "id": str(tpl.id),
                "status": "published",
                "version": str(tpl.version),
            }
    except TemplateValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

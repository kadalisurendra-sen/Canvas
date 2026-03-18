"""Template business logic — CRUD operations."""
import logging
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from src.repo.template_repository import (
    create_template,
    delete_template,
    get_template_by_id,
    list_templates,
    replace_stages,
    update_template_metadata,
)
from src.repo.tenant_models import Template
from src.repo.tenant_models_ext import TemplateStage
from src.types.template import (
    TemplateCreate,
    TemplateListItem,
    TemplateListResponse,
    TemplateUpdate,
)

logger = logging.getLogger(__name__)


class TemplateServiceError(Exception):
    """Base exception for template service errors."""


class TemplateNotFoundError(TemplateServiceError):
    """Raised when a template is not found."""


class TemplateValidationError(TemplateServiceError):
    """Raised when template data fails validation."""


async def get_templates(
    session: AsyncSession,
    status: str | None = None,
    category: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> TemplateListResponse:
    """Fetch paginated template list."""
    templates, total = await list_templates(
        session, status, category, search, page, page_size
    )
    items = [_to_list_item(t) for t in templates]
    return TemplateListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


async def get_template(
    session: AsyncSession,
    template_id: uuid.UUID,
) -> Template:
    """Get a template by ID or raise not found."""
    template = await get_template_by_id(session, template_id)
    if not template:
        raise TemplateNotFoundError(f"Template {template_id} not found")
    return template


async def create_new_template(
    session: AsyncSession,
    data: TemplateCreate,
    created_by: uuid.UUID,
) -> Template:
    """Create a new draft template."""
    return await create_template(
        session, name=data.name, category=data.category,
        created_by=created_by, description=data.description,
        icon=data.icon, theme_color=data.theme_color, tags=data.tags,
    )


async def update_template(
    session: AsyncSession,
    template_id: uuid.UUID,
    data: TemplateUpdate,
) -> Template:
    """Update template metadata."""
    template = await get_template(session, template_id)
    return await update_template_metadata(
        session, template, name=data.name, category=data.category,
        description=data.description, icon=data.icon,
        theme_color=data.theme_color, tags=data.tags,
    )


async def update_stages(
    session: AsyncSession,
    template_id: uuid.UUID,
    stages_data: list[dict[str, str | int]],
) -> list[TemplateStage]:
    """Replace stages for a template."""
    await get_template(session, template_id)
    return await replace_stages(session, template_id, stages_data)


async def remove_template(
    session: AsyncSession,
    template_id: uuid.UUID,
) -> None:
    """Delete a template."""
    template = await get_template(session, template_id)
    await delete_template(session, template)


def _to_list_item(template: Template) -> TemplateListItem:
    """Convert ORM Template to list item schema."""
    stage_count = len(template.stages) if template.stages else 0
    field_count = _count_fields(template)
    tags = [t.tag for t in template.tags] if template.tags else []
    return TemplateListItem(
        id=template.id, name=template.name,
        category=template.category, description=template.description,
        icon=template.icon, theme_color=template.theme_color,
        status=template.status, version=template.version,
        created_by=template.created_by,
        created_at=template.created_at, updated_at=template.updated_at,
        stage_count=stage_count, field_count=field_count, tags=tags,
    )


def _count_fields(template: Template) -> int:
    """Count total fields across all stages/sections."""
    count = 0
    if not template.stages:
        return 0
    for stage in template.stages:
        if hasattr(stage, "sections") and stage.sections:
            for section in stage.sections:
                if hasattr(section, "fields") and section.fields:
                    count += len(section.fields)
    return count


def _validate_publishable(template: Template) -> None:
    """Validate that a template is ready to publish."""
    if not template.name or not template.name.strip():
        raise TemplateValidationError("Template must have a name")

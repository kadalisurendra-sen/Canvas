"""Repository for template CRUD operations."""
import logging
import uuid
from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.repo.tenant_models import Template
from src.repo.tenant_models_ext import (
    FieldOption,
    TemplateField,
    TemplateSection,
    TemplateStage,
    TemplateTag,
)

logger = logging.getLogger(__name__)


async def list_templates(
    session: AsyncSession,
    status: str | None = None,
    category: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Template], int]:
    """List templates with optional filters and pagination."""
    query = select(Template).options(
        selectinload(Template.tags),
        selectinload(Template.stages)
        .selectinload(TemplateStage.sections)
        .selectinload(TemplateSection.fields),
    )
    count_query = select(func.count(Template.id))

    if status:
        query = query.where(Template.status == status)
        count_query = count_query.where(Template.status == status)
    if category:
        query = query.where(Template.category == category)
        count_query = count_query.where(Template.category == category)
    if search:
        pattern = f"%{search}%"
        query = query.where(Template.name.ilike(pattern))
        count_query = count_query.where(Template.name.ilike(pattern))

    query = query.order_by(Template.updated_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await session.execute(query)
    templates = list(result.scalars().unique().all())

    count_result = await session.execute(count_query)
    total = count_result.scalar() or 0

    return templates, total


async def get_template_by_id(
    session: AsyncSession,
    template_id: uuid.UUID,
) -> Template | None:
    """Get a single template with all nested data."""
    query = (
        select(Template)
        .where(Template.id == template_id)
        .options(
            selectinload(Template.tags),
            selectinload(Template.stages)
            .selectinload(TemplateStage.sections)
            .selectinload(TemplateSection.fields)
            .selectinload(TemplateField.options),
        )
    )
    result = await session.execute(query)
    return result.scalars().unique().first()


async def create_template(
    session: AsyncSession,
    name: str,
    category: str,
    created_by: uuid.UUID,
    description: str | None = None,
    icon: str | None = None,
    theme_color: str | None = None,
    tags: list[str] | None = None,
) -> Template:
    """Create a new template with tags."""
    template = Template(
        name=name,
        category=category,
        description=description,
        icon=icon,
        theme_color=theme_color,
        created_by=created_by,
        status="draft",
        version=1,
    )
    session.add(template)
    await session.flush()

    if tags:
        for tag_str in tags:
            tag = TemplateTag(template_id=template.id, tag=tag_str)
            session.add(tag)

    await session.commit()
    await session.refresh(template)
    return template


async def update_template_metadata(
    session: AsyncSession,
    template: Template,
    name: str | None = None,
    category: str | None = None,
    description: str | None = None,
    icon: str | None = None,
    theme_color: str | None = None,
    tags: list[str] | None = None,
) -> Template:
    """Update template metadata and optionally tags."""
    if name is not None:
        template.name = name
    if category is not None:
        template.category = category
    if description is not None:
        template.description = description
    if icon is not None:
        template.icon = icon
    if theme_color is not None:
        template.theme_color = theme_color
    template.updated_at = datetime.utcnow()

    if tags is not None:
        await session.execute(
            delete(TemplateTag).where(
                TemplateTag.template_id == template.id
            )
        )
        for tag_str in tags:
            tag = TemplateTag(template_id=template.id, tag=tag_str)
            session.add(tag)

    await session.commit()
    await session.refresh(template)
    return template


async def replace_stages(
    session: AsyncSession,
    template_id: uuid.UUID,
    stages_data: list[dict[str, str | int]],
) -> list[TemplateStage]:
    """Replace all stages for a template."""
    await session.execute(
        delete(TemplateStage).where(
            TemplateStage.template_id == template_id
        )
    )
    new_stages: list[TemplateStage] = []
    for stage_d in stages_data:
        stage = TemplateStage(
            template_id=template_id,
            name=str(stage_d["name"]),
            sort_order=int(stage_d["sort_order"]),
        )
        session.add(stage)
        new_stages.append(stage)

    await session.commit()
    for stage in new_stages:
        await session.refresh(stage)
    return new_stages


async def delete_template(
    session: AsyncSession,
    template: Template,
) -> None:
    """Delete a template (cascades to children)."""
    await session.delete(template)
    await session.commit()

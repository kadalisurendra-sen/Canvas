"""Template wizard business logic — fields, scoring, publish."""
import logging
import uuid
from datetime import datetime

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.repo.tenant_models import Template
from src.repo.tenant_models_ext import (
    FieldOption,
    TemplateField,
    TemplateSection,
    TemplateStage,
)
from src.service.template_service import (
    TemplateNotFoundError,
    TemplateValidationError,
    _validate_publishable,
    get_template,
)
from src.types.template import FieldsUpdate, ScoringUpdate

logger = logging.getLogger(__name__)


async def update_fields(
    session: AsyncSession,
    template_id: uuid.UUID,
    data: FieldsUpdate,
) -> Template:
    """Replace sections/fields/options for a template."""
    template = await get_template(session, template_id)
    for stage_data in data.stages:
        stage = await _find_stage(session, stage_data.stage_id)
        await _replace_sections(session, stage, stage_data.sections)
    await session.flush()
    return template


async def update_scoring(
    session: AsyncSession,
    template_id: uuid.UUID,
    data: ScoringUpdate,
) -> Template:
    """Update scoring config for stages."""
    await get_template(session, template_id)
    total_weight = sum(s.weight_pct for s in data.stages)
    if abs(total_weight - 100.0) > 0.01:
        raise TemplateValidationError(
            f"Stage weights must sum to 100%, got {total_weight}%"
        )
    for scoring in data.stages:
        stage = await _find_stage(session, scoring.stage_id)
        stage.weight_pct = scoring.weight_pct
        stage.min_pass_score = scoring.min_pass_score
        stage.fail_action = scoring.fail_action.value
    await session.flush()
    return template


async def publish_template(
    session: AsyncSession,
    template_id: uuid.UUID,
) -> Template:
    """Publish a template after validation."""
    template = await get_template(session, template_id)
    _validate_publishable(template)
    template.status = "published"
    template.version = template.version + 1
    template.updated_at = datetime.utcnow()
    await session.flush()
    return template


async def _find_stage(
    session: AsyncSession,
    stage_id: uuid.UUID,
) -> TemplateStage:
    """Find a stage by ID."""
    stage = await session.get(TemplateStage, stage_id)
    if not stage:
        raise TemplateNotFoundError(f"Stage {stage_id} not found")
    return stage


async def _replace_sections(
    session: AsyncSession,
    stage: TemplateStage,
    sections_data: list,  # type: ignore[type-arg]
) -> None:
    """Replace all sections/fields for a stage."""
    await session.execute(
        delete(TemplateSection).where(
            TemplateSection.stage_id == stage.id
        )
    )
    for sec_data in sections_data:
        section = TemplateSection(
            stage_id=stage.id, name=sec_data.name,
            sort_order=sec_data.sort_order,
        )
        session.add(section)
        await session.flush()
        await _create_fields(session, section, sec_data.fields)


async def _create_fields(
    session: AsyncSession,
    section: TemplateSection,
    fields_data: list,  # type: ignore[type-arg]
) -> None:
    """Create fields and options for a section."""
    for field_data in fields_data:
        field = TemplateField(
            section_id=section.id,
            field_key=field_data.field_key,
            label=field_data.label,
            field_type=field_data.field_type.value,
            help_text=field_data.help_text,
            is_mandatory=field_data.is_mandatory,
            is_scoring=field_data.is_scoring,
            sort_order=field_data.sort_order,
        )
        session.add(field)
        await session.flush()
        for opt_data in field_data.options:
            option = FieldOption(
                field_id=field.id, label=opt_data.label,
                value=opt_data.value, score=opt_data.score,
                sort_order=opt_data.sort_order,
            )
            session.add(option)

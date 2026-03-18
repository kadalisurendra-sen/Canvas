"""Business logic for master data management."""
import csv
import io
import logging
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.repo import master_data_repository as repo
from src.types.master_data import (
    CategoryOut,
    ImportResult,
    PaginatedValues,
    ValueCreate,
    ValueOut,
    ValueUpdate,
)

logger = logging.getLogger(__name__)

VALID_SEVERITIES = {"high", "medium", "low", ""}
MAX_IMPORT_ROWS = 1000


async def get_categories(
    session: AsyncSession,
) -> list[CategoryOut]:
    """Return all master data categories with counts."""
    rows = await repo.list_categories(session)
    return [CategoryOut(**r) for r in rows]


async def get_values(
    session: AsyncSession,
    category_id: uuid.UUID,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> PaginatedValues:
    """Return paginated values for a category."""
    items, total = await repo.list_values(
        session, category_id, search, page, page_size
    )
    return PaginatedValues(
        items=[ValueOut.model_validate(v) for v in items],
        total=total,
        page=page,
        page_size=page_size,
    )


async def create_value(
    session: AsyncSession,
    category_id: uuid.UUID,
    data: ValueCreate,
) -> ValueOut:
    """Create a new master data value."""
    row = await repo.create_value(
        session,
        category_id,
        value=data.value,
        label=data.label,
        severity=data.severity,
        description=data.description,
    )
    return ValueOut.model_validate(row)


async def update_value(
    session: AsyncSession,
    value_id: uuid.UUID,
    data: ValueUpdate,
) -> Optional[ValueOut]:
    """Update an existing master data value."""
    update_dict = data.model_dump(exclude_none=True)
    if not update_dict:
        return None
    row = await repo.update_value(session, value_id, update_dict)
    if not row:
        return None
    return ValueOut.model_validate(row)


async def delete_value(
    session: AsyncSession, value_id: uuid.UUID
) -> bool:
    """Delete a master data value."""
    return await repo.delete_value(session, value_id)


async def reorder_values(
    session: AsyncSession,
    category_id: uuid.UUID,
    value_ids: list[uuid.UUID],
) -> None:
    """Reorder values in a category."""
    await repo.reorder_values(session, category_id, value_ids)


async def import_csv(
    session: AsyncSession,
    category_id: uuid.UUID,
    file_content: bytes,
) -> ImportResult:
    """Parse and import CSV file content."""
    text = _decode_csv(file_content)
    rows, errors = _parse_csv(text)

    if len(rows) > MAX_IMPORT_ROWS:
        return ImportResult(
            imported=0,
            skipped=0,
            errors=[{"row": 0, "message": f"Exceeds max {MAX_IMPORT_ROWS} rows"}],
        )

    imported = 0
    skipped = 0
    max_order = await repo.get_max_sort_order(session, category_id)

    valid_rows = []
    for row_data in rows:
        exists = await repo.value_exists(
            session, category_id, row_data["value"]
        )
        if exists:
            skipped += 1
            continue
        valid_rows.append(row_data)

    if valid_rows:
        imported = await repo.bulk_insert_values(
            session, category_id, valid_rows, max_order
        )

    return ImportResult(imported=imported, skipped=skipped, errors=errors)


def _decode_csv(content: bytes) -> str:
    """Decode CSV bytes, handling BOM."""
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="replace")


def _parse_csv(
    text: str,
) -> tuple[list[dict], list[dict[str, str | int]]]:
    """Parse CSV text into rows and validation errors."""
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        return [], [{"row": 0, "message": "Empty or invalid CSV"}]

    header_map = {h.strip().lower(): h for h in reader.fieldnames}
    rows: list[dict] = []
    errors: list[dict[str, str | int]] = []

    for i, raw in enumerate(reader, start=2):
        mapped = {k.strip().lower(): v.strip() for k, v in raw.items() if v}
        val = mapped.get("value", "")
        lab = mapped.get("label", "")
        if not val or not lab:
            errors.append({"row": i, "message": "value and label required"})
            continue
        sev = mapped.get("severity", "")
        if sev and sev.lower() not in VALID_SEVERITIES:
            errors.append({"row": i, "message": f"Invalid severity: {sev}"})
            continue
        rows.append({
            "value": val,
            "label": lab,
            "severity": sev.lower() if sev else None,
            "description": mapped.get("description"),
        })

    return rows, errors

"""Repository for master data categories and values CRUD."""
import logging
import uuid
from typing import Optional

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.repo.master_data_models import (
    AuditLog,
    MasterDataCategory,
    MasterDataValue,
)

logger = logging.getLogger(__name__)


async def list_categories(
    session: AsyncSession,
) -> list[dict]:
    """Return all categories with active item counts."""
    subq = (
        select(
            MasterDataValue.category_id,
            func.count(MasterDataValue.id).label("item_count"),
        )
        .where(MasterDataValue.is_active.is_(True))
        .group_by(MasterDataValue.category_id)
        .subquery()
    )
    stmt = (
        select(
            MasterDataCategory.id,
            MasterDataCategory.name,
            MasterDataCategory.display_name,
            MasterDataCategory.icon,
            MasterDataCategory.sort_order,
            func.coalesce(subq.c.item_count, 0).label("item_count"),
        )
        .outerjoin(subq, MasterDataCategory.id == subq.c.category_id)
        .order_by(MasterDataCategory.sort_order)
    )
    result = await session.execute(stmt)
    rows = result.all()
    return [row._asdict() for row in rows]


async def list_values(
    session: AsyncSession,
    category_id: uuid.UUID,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[MasterDataValue], int]:
    """Return paginated values for a category."""
    base = select(MasterDataValue).where(
        MasterDataValue.category_id == category_id
    )
    count_q = select(func.count(MasterDataValue.id)).where(
        MasterDataValue.category_id == category_id
    )
    if search:
        pattern = f"%{search}%"
        base = base.where(
            MasterDataValue.label.ilike(pattern)
            | MasterDataValue.value.ilike(pattern)
        )
        count_q = count_q.where(
            MasterDataValue.label.ilike(pattern)
            | MasterDataValue.value.ilike(pattern)
        )
    total = (await session.execute(count_q)).scalar() or 0
    offset = (page - 1) * page_size
    stmt = base.order_by(MasterDataValue.sort_order).offset(offset).limit(page_size)
    result = await session.execute(stmt)
    return list(result.scalars().all()), total


async def get_max_sort_order(
    session: AsyncSession, category_id: uuid.UUID
) -> int:
    """Get the current max sort_order for a category."""
    stmt = select(func.coalesce(func.max(MasterDataValue.sort_order), 0)).where(
        MasterDataValue.category_id == category_id
    )
    result = await session.execute(stmt)
    return result.scalar() or 0


async def create_value(
    session: AsyncSession,
    category_id: uuid.UUID,
    value: str,
    label: str,
    severity: Optional[str],
    description: Optional[str],
) -> MasterDataValue:
    """Insert a new master data value."""
    max_order = await get_max_sort_order(session, category_id)
    row = MasterDataValue(
        id=uuid.uuid4(),
        category_id=category_id,
        value=value,
        label=label,
        severity=severity,
        description=description,
        is_active=True,
        sort_order=max_order + 1,
    )
    session.add(row)
    await session.flush()
    return row


async def update_value(
    session: AsyncSession,
    value_id: uuid.UUID,
    data: dict,
) -> Optional[MasterDataValue]:
    """Update a master data value by ID."""
    stmt = select(MasterDataValue).where(MasterDataValue.id == value_id)
    result = await session.execute(stmt)
    row = result.scalar_one_or_none()
    if not row:
        return None
    for key, val in data.items():
        if val is not None:
            setattr(row, key, val)
    await session.flush()
    return row


async def delete_value(
    session: AsyncSession, value_id: uuid.UUID
) -> bool:
    """Delete a master data value. Returns True if deleted."""
    stmt = delete(MasterDataValue).where(MasterDataValue.id == value_id)
    result = await session.execute(stmt)
    return (result.rowcount or 0) > 0


async def reorder_values(
    session: AsyncSession,
    category_id: uuid.UUID,
    value_ids: list[uuid.UUID],
) -> None:
    """Bulk update sort_order for values in a category."""
    for idx, vid in enumerate(value_ids):
        await session.execute(
            update(MasterDataValue)
            .where(
                MasterDataValue.id == vid,
                MasterDataValue.category_id == category_id,
            )
            .values(sort_order=idx + 1)
        )
    await session.flush()


async def bulk_insert_values(
    session: AsyncSession,
    category_id: uuid.UUID,
    rows: list[dict],
    start_order: int,
) -> int:
    """Bulk insert parsed CSV rows. Returns count inserted."""
    if not rows:
        return 0
    values_list = []
    for i, row in enumerate(rows):
        values_list.append({
            "id": uuid.uuid4(),
            "category_id": category_id,
            "value": row["value"],
            "label": row["label"],
            "severity": row.get("severity"),
            "description": row.get("description"),
            "is_active": True,
            "sort_order": start_order + i + 1,
        })
    stmt = insert(MasterDataValue).values(values_list)
    await session.execute(stmt)
    await session.flush()
    return len(values_list)


async def value_exists(
    session: AsyncSession,
    category_id: uuid.UUID,
    value: str,
) -> bool:
    """Check if a value key already exists in a category."""
    stmt = select(func.count(MasterDataValue.id)).where(
        MasterDataValue.category_id == category_id,
        MasterDataValue.value == value,
    )
    result = await session.execute(stmt)
    return (result.scalar() or 0) > 0

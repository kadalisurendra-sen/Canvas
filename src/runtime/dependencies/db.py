"""Database session dependency for tenant-scoped routes."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.repo.session_manager import TenantSessionManager

logger = logging.getLogger(__name__)

_tenant_manager = TenantSessionManager()


@asynccontextmanager
async def get_tenant_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a tenant-scoped async session using schema search_path."""
    schema_name: str = getattr(request.state, "tenant_schema", "tenant_acme")
    session = await _tenant_manager.get_tenant_session(schema_name)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

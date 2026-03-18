"""Database session dependency for tenant-scoped routes."""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.repo.session_manager import TenantSessionManager

logger = logging.getLogger(__name__)

_tenant_manager = TenantSessionManager()

# For local dev: hardcode to the seeded tenant database
# In production, this would look up tenant.db_name from the platform DB
_DEFAULT_TENANT_DB = "db_tenant_acme"


@asynccontextmanager
async def get_tenant_session(
    request: Request | None = None,
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a tenant-scoped async session."""
    # TODO: In production, look up tenant db_name from platform DB
    # using request.state.tenant_id. For now, always use acme tenant.
    db_name = _DEFAULT_TENANT_DB

    factory = _tenant_manager.get_session_factory(
        "localhost", 5432, db_name,
    )
    async with factory() as session:
        yield session

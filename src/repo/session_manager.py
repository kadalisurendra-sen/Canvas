"""Tenant session manager — schema-per-tenant using search_path."""
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class TenantSessionManager:
    """Manages tenant-scoped sessions via PostgreSQL schema search_path."""

    def __init__(self) -> None:
        """Initialize with a single shared engine."""
        self._engine = None
        self._base_factory: async_sessionmaker[AsyncSession] | None = None

    def _get_engine(self):
        """Get or create the shared async engine."""
        if self._engine is None:
            settings = get_settings()
            self._engine = create_async_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_size=20,
                max_overflow=30,
            )
            self._base_factory = async_sessionmaker(
                self._engine, class_=AsyncSession, expire_on_commit=False
            )
        return self._engine

    def get_session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get the base session factory (caller sets search_path)."""
        self._get_engine()
        return self._base_factory

    async def get_tenant_session(self, schema_name: str) -> AsyncSession:
        """Create a session scoped to the given tenant schema."""
        factory = self.get_session_factory()
        session = factory()
        await session.execute(text(f"SET search_path TO {schema_name}, public"))
        return session

    async def close_all(self) -> None:
        """Dispose of the shared engine."""
        if self._engine:
            logger.info("Disposing shared engine")
            await self._engine.dispose()
            self._engine = None
            self._base_factory = None

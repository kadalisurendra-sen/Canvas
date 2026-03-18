"""Tenant session manager — dynamic async session factory per tenant DB."""
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class TenantSessionManager:
    """Manages per-tenant database connections with connection pooling."""

    def __init__(self) -> None:
        """Initialize the session manager with empty caches."""
        self._engines: dict[str, "create_async_engine"] = {}
        self._session_factories: dict[
            str, async_sessionmaker[AsyncSession]
        ] = {}

    def _build_dsn(
        self, db_host: str, db_port: int, db_name: str
    ) -> str:
        """Build an async PostgreSQL connection string."""
        settings = get_settings()
        return (
            f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{db_host}:{db_port}/{db_name}"
        )

    def get_session_factory(
        self, db_host: str, db_port: int, db_name: str
    ) -> async_sessionmaker[AsyncSession]:
        """Get or create a session factory for the given tenant DB."""
        dsn = self._build_dsn(db_host, db_port, db_name)
        if dsn not in self._session_factories:
            logger.info("Creating engine for tenant DB: %s", db_name)
            engine = create_async_engine(
                dsn, pool_pre_ping=True, pool_size=5, max_overflow=10
            )
            factory = async_sessionmaker(
                engine, class_=AsyncSession, expire_on_commit=False
            )
            self._engines[dsn] = engine
            self._session_factories[dsn] = factory
        return self._session_factories[dsn]

    async def close_all(self) -> None:
        """Dispose of all cached engines."""
        for dsn, engine in self._engines.items():
            logger.info("Disposing engine: %s", dsn[:50])
            await engine.dispose()
        self._engines.clear()
        self._session_factories.clear()

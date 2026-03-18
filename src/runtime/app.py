"""FastAPI application factory and health endpoint."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import get_settings
from src.runtime.middleware.tenant_resolver import TenantResolverMiddleware
from src.runtime.routes.health import router as health_router
from src.runtime.routes.auth import router as auth_router
from src.runtime.routes.users import router as users_router
from src.runtime.routes.tenants import router as tenants_router
from src.runtime.routes.templates import router as templates_router
from src.runtime.routes.template_wizard import router as template_wizard_router
from src.runtime.routes.master_data import router as master_data_router
from src.runtime.routes.analytics import router as analytics_router
from src.service.auth_service import AuthService

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    application.add_middleware(
        TenantResolverMiddleware,
        auth_service=AuthService(),
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(users_router)
    application.include_router(tenants_router)
    application.include_router(templates_router)
    application.include_router(template_wizard_router)
    application.include_router(master_data_router)
    application.include_router(analytics_router)

    return application


app = create_app()

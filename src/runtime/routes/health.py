"""Health check endpoint."""
import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return application health status."""
    return {"status": "ok"}

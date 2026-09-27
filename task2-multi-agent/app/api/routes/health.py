"""Liveness endpoint - lets a load balancer or monitor check the app is up."""

from fastapi import APIRouter

from app.config import get_settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse, summary="Service liveness check")
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
    )

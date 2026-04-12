from fastapi import APIRouter, Depends, Response, status

from pdf_accessibility.core.settings import Settings, get_settings
from pdf_accessibility.services.runtime_checks import build_runtime_status

router = APIRouter(tags=["system"])


@router.get("/")
def root(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "service": settings.app_name,
        "environment": settings.environment,
        "docs_url": "/docs",
        "health_url": "/healthz",
        "readiness_url": "/readyz",
    }


@router.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@router.get("/readyz")
def readyz(
    response: Response,
    settings: Settings = Depends(get_settings),
) -> dict:
    payload = build_runtime_status(settings)
    response.status_code = (
        status.HTTP_200_OK if payload["ready"] else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return payload

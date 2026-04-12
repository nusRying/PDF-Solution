from __future__ import annotations

from fastapi import APIRouter, Depends

from pdf_accessibility.core.settings import Settings, get_settings
from pdf_accessibility.services.file_store import FileStore
from pdf_accessibility.services.telemetry import build_empty_lane_telemetry_artifact

router = APIRouter(tags=["metrics"])


@router.get("/metrics/lanes")
def get_lane_metrics(
    settings: Settings = Depends(get_settings),
):
    store = FileStore(settings)
    artifact = store.get_lane_telemetry_artifact()
    return artifact or build_empty_lane_telemetry_artifact()

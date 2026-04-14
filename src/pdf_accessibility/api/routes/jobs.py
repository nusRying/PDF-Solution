from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from pdf_accessibility.core.settings import Settings, get_settings
from pdf_accessibility.models.documents import utc_now
from pdf_accessibility.models.jobs import JobRecord
from pdf_accessibility.services.file_store import get_file_store
from pdf_accessibility.services.telemetry import record_job_telemetry

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{job_id}", response_model=JobRecord)
def get_job_status(
    job_id: str,
    settings: Settings = Depends(get_settings),
):
    store = get_file_store(settings)
    record = store.get_job_record(job_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return record


@router.get("/jobs/{job_id}/metrics")
def get_job_metrics(
    job_id: str,
    settings: Settings = Depends(get_settings),
):
    store = get_file_store(settings)
    record = store.get_job_record(job_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return record.summary

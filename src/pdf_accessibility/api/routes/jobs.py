from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from pdf_accessibility.core.settings import Settings, get_settings
from pdf_accessibility.models.documents import utc_now
from pdf_accessibility.models.jobs import JobStage, JobStageEvent, JobStatus, JobSummary
from pdf_accessibility.services.file_store import FileStore
from pdf_accessibility.services.job_queue import JobQueueService

router = APIRouter(tags=["jobs"])


@router.get("/jobs/{job_id}")
def get_job(
    job_id: str,
    settings: Settings = Depends(get_settings),
):
    store = FileStore(settings)
    record = store.get_job_record(job_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    return record


@router.get("/jobs/{job_id}/metrics")
def get_job_metrics(
    job_id: str,
    settings: Settings = Depends(get_settings),
):
    store = FileStore(settings)
    record = store.get_job_record(job_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    summary = record.summary
    return {
        "job_id": record.job_id,
        "document_id": record.document_id,
        "status": record.status,
        "current_stage": record.current_stage,
        "processing_lane": summary.processing_lane,
        "lane_policy": summary.lane_policy,
        "page_count": summary.page_count,
        "ocr_mode": summary.ocr_mode,
        "ocr_attempted_page_count": summary.ocr_attempted_page_count,
        "ocr_completed_page_count": summary.ocr_completed_page_count,
        "manual_review_required": summary.manual_review_required,
        "processing_duration_seconds": summary.processing_duration_seconds,
        "throughput_pages_per_second": summary.throughput_pages_per_second,
    }


@router.post("/jobs/{job_id}/retry", status_code=status.HTTP_202_ACCEPTED)
def retry_job(
    job_id: str,
    request: Request,
    settings: Settings = Depends(get_settings),
):
    store = FileStore(settings)
    record = store.get_job_record(job_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    if record.status == JobStatus.processing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job is currently processing.",
        )

    original_artifact = record.artifacts.get("original")
    record.status = JobStatus.pending
    record.error = None
    record.summary = JobSummary()
    record.current_stage = JobStage.uploaded
    record.stage_events.append(
        JobStageEvent(
            stage=JobStage.uploaded,
            note="Job requeued for processing.",
        )
    )
    record.artifacts = {"original": original_artifact} if original_artifact else {}
    record.updated_at = utc_now()
    store.save_job_record(record)

    job_queue = getattr(request.app.state, "job_queue", None)
    if not isinstance(job_queue, JobQueueService):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ingestion queue is unavailable.",
        )

    job_queue.enqueue(record.job_id)
    return record

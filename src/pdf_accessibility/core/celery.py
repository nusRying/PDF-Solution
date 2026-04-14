from __future__ import annotations

from celery import Celery
from pdf_accessibility.core.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "pdf_accessibility",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

@celery_app.task(name="process_pdf_job")
def process_pdf_job(job_id: str):
    from pdf_accessibility.services.ingestion import process_ingest_job
    from pdf_accessibility.core.settings import get_settings
    
    settings = get_settings()
    process_ingest_job(job_id, settings)

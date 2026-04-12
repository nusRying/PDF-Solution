from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from pdf_accessibility.models.documents import utc_now
from pdf_accessibility.models.jobs import JobStatus
from pdf_accessibility.models.preflight import ProcessingLane


class LaneTelemetryTotals(BaseModel):
    total_attempt_count: int = 0
    classified_attempt_count: int = 0
    succeeded_count: int = 0
    failed_count: int = 0
    unclassified_failure_count: int = 0
    total_page_count: int = 0
    total_processing_duration_seconds: float = 0.0


class LaneTelemetryRecord(BaseModel):
    lane: ProcessingLane
    total_attempt_count: int = 0
    succeeded_count: int = 0
    failed_count: int = 0
    manual_review_attempt_count: int = 0
    total_page_count: int = 0
    total_ocr_attempted_page_count: int = 0
    total_ocr_completed_page_count: int = 0
    total_processing_duration_seconds: float = 0.0
    total_throughput_pages_per_second: float = 0.0
    average_processing_duration_seconds: float | None = None
    average_throughput_pages_per_second: float | None = None
    success_rate: float | None = None
    last_job_id: str | None = None
    last_status: JobStatus | None = None
    updated_at: datetime = Field(default_factory=utc_now)


class LaneTelemetryArtifact(BaseModel):
    generated_at: datetime = Field(default_factory=utc_now)
    totals: LaneTelemetryTotals = Field(default_factory=LaneTelemetryTotals)
    lanes: list[LaneTelemetryRecord] = Field(default_factory=list)

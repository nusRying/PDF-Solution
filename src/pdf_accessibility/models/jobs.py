from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from pdf_accessibility.models.compliance import ComplianceProfile
from pdf_accessibility.models.documents import DocumentRecord, DocumentSourceType, utc_now
from pdf_accessibility.models.preflight import PreflightClass, ProcessingLane
from pdf_accessibility.models.validation import ValidationStatus


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    succeeded = "succeeded"
    failed = "failed"


class JobStage(str, Enum):
    uploaded = "uploaded"
    parsed = "parsed"
    preflight_classified = "preflight-classified"
    ocr_enriched = "ocr-enriched"
    canonicalized = "canonicalized"
    remediated = "remediated"
    validated = "validated"
    completed = "completed"
    failed = "failed"


class JobStageEvent(BaseModel):
    stage: JobStage
    timestamp: datetime = Field(default_factory=utc_now)
    note: str | None = None


class JobSummary(BaseModel):
    page_count: int | None = None
    source_type: DocumentSourceType | None = None
    processing_lane: ProcessingLane | None = None
    compliance_profile: ComplianceProfile | None = None
    lane_policy: str | None = None
    ocr_mode: str | None = None
    ocr_attempted_page_count: int | None = None
    ocr_completed_page_count: int | None = None
    manual_review_required: bool | None = None
    processing_duration_seconds: float | None = None
    throughput_pages_per_second: float | None = None
    preflight_classes: list[PreflightClass] = Field(default_factory=list)
    preflight_form_field_count: int | None = None
    preflight_table_page_count: int | None = None
    preflight_multi_column_page_count: int | None = None
    preflight_rtl_detected: bool | None = None
    text_page_count: int | None = None
    image_page_count: int | None = None
    ocr_page_count: int | None = None
    canonical_block_count: int | None = None
    remediation_action_count: int | None = None
    remediation_changed_count: int | None = None
    remediation_review_pages: int | None = None
    validation_status: ValidationStatus | None = None
    validation_finding_count: int | None = None


class JobRecord(BaseModel):
    job_id: str
    document_id: str
    status: JobStatus
    compliance_profile: ComplianceProfile = ComplianceProfile.profile_b
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    error: str | None = None
    artifacts: dict[str, str] = Field(default_factory=dict)
    summary: JobSummary = Field(default_factory=JobSummary)
    current_stage: JobStage = JobStage.uploaded
    stage_events: list[JobStageEvent] = Field(default_factory=list)


class DocumentIngestResponse(BaseModel):
    document: DocumentRecord
    job: JobRecord

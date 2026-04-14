from __future__ import annotations

import hashlib
import time
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.compliance import ComplianceProfile
from pdf_accessibility.models.documents import DocumentRecord, utc_now
from pdf_accessibility.models.jobs import JobRecord, JobStage, JobStageEvent, JobStatus, JobSummary
from pdf_accessibility.models.ocr import OCRArtifact
from pdf_accessibility.services.canonicalize import build_canonical_document
from pdf_accessibility.services.file_store import get_file_store, BaseFileStore
from pdf_accessibility.services.lane_policy import OCRMode, resolve_lane_execution_policy
from pdf_accessibility.services.ocr import run_tesseract_ocr
from pdf_accessibility.services.pdf_parser import parse_pdf
from pdf_accessibility.services.pdf_writer import PdfWriterService
from pdf_accessibility.services.preflight import classify_preflight
from pdf_accessibility.services.remediation import run_remediation_pipeline
from pdf_accessibility.services.telemetry import record_job_telemetry
from pdf_accessibility.services.validation import run_validation_pipeline


async def _save_upload_to_path(upload: UploadFile, destination: Path) -> tuple[int, str]:
    hasher = hashlib.sha256()
    size = 0

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as handle:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
            hasher.update(chunk)
            size += len(chunk)

    await upload.close()
    return size, hasher.hexdigest()


def _normalize_filename(filename: str | None) -> str:
    if not filename:
        return "uploaded.pdf"
    return Path(filename).name or "uploaded.pdf"


def _advance_job_stage(
    job: JobRecord,
    store: BaseFileStore,
    stage: JobStage,
    note: str | None = None,
) -> None:
    job.current_stage = stage
    job.stage_events.append(JobStageEvent(stage=stage, note=note))
    job.updated_at = utc_now()
    store.save_job_record(job)


async def create_ingest_job(
    upload: UploadFile,
    settings: Settings,
    profile: ComplianceProfile = ComplianceProfile.profile_b,
) -> tuple[DocumentRecord, JobRecord]:
    store = get_file_store(settings)
    document_id = uuid4().hex
    job_id = uuid4().hex

    original_filename = _normalize_filename(upload.filename)
    suffix = Path(original_filename).suffix.lower() or ".pdf"
    content = await upload.read()
    stored_pdf_path = store.save_original_pdf(document_id, content, suffix=suffix)

    file_size_bytes = len(content)
    sha256 = hashlib.sha256(content).hexdigest()

    document = DocumentRecord(
        document_id=document_id,
        original_filename=original_filename,
        stored_filename=stored_pdf_path.name,
        content_type=upload.content_type,
        file_size_bytes=file_size_bytes,
        sha256=sha256,
        original_path=store.relative_path(stored_pdf_path),
    )
    store.save_document_record(document)

    job = JobRecord(
        job_id=job_id,
        document_id=document_id,
        status=JobStatus.pending,
        compliance_profile=profile,
        artifacts={"original": store.relative_path(stored_pdf_path)},
        current_stage=JobStage.uploaded,
        stage_events=[JobStageEvent(stage=JobStage.uploaded, note=f"PDF file stored with {profile.value} profile.")],
    )
    store.save_job_record(job)

    return document, job


def _fail_job(job: JobRecord, store: FileStore, message: str) -> JobRecord:
    job.status = JobStatus.failed
    job.current_stage = JobStage.failed
    job.stage_events.append(JobStageEvent(stage=JobStage.failed, note=message))
    job.error = message
    job.updated_at = utc_now()
    store.save_job_record(job)
    return job


def process_ingest_job(
    job_id: str,
    settings: Settings,
) -> JobRecord:
    store = get_file_store(settings)
    job = store.get_job_record(job_id)
    if job is None:
        raise FileNotFoundError(f"Job {job_id} not found.")

    if job.status == JobStatus.succeeded:
        return job

    document = store.get_document_record(job.document_id)
    if document is None:
        failed_job = _fail_job(job, store, f"Document record {job.document_id} not found.")
        record_job_telemetry(store=store, job=failed_job)
        return failed_job
    document_id = job.document_id

    stored_pdf_path = store.original_pdf_path(document_id, suffix=Path(document.original_filename).suffix)
    if not stored_pdf_path.exists():
        failed_job = _fail_job(job, store, f"Original PDF not found at {stored_pdf_path}.")
        record_job_telemetry(store=store, job=failed_job)
        return failed_job

    job.status = JobStatus.processing
    job.error = None
    job.updated_at = utc_now()
    store.save_job_record(job)
    processing_started = time.perf_counter()
    preflight_artifact = None
    lane_policy = None

    try:
        parser_artifact = parse_pdf(document_id=document_id, pdf_path=stored_pdf_path)
        job.summary.page_count = parser_artifact.page_count
        job.summary.source_type = parser_artifact.source_type
        _advance_job_stage(
            job,
            store,
            JobStage.parsed,
            note=f"Parsed {parser_artifact.page_count} pages.",
        )

        preflight_artifact = classify_preflight(
            document_id=document_id,
            pdf_path=stored_pdf_path,
            parser_artifact=parser_artifact,
        )
        _advance_job_stage(
            job,
            store,
            JobStage.preflight_classified,
            note=f"Routed to {preflight_artifact.lane.value} lane.",
        )

        lane_policy = resolve_lane_execution_policy(preflight_artifact)
        job.summary.processing_lane = preflight_artifact.lane
        job.summary.compliance_profile = job.compliance_profile
        job.summary.preflight_classes = preflight_artifact.classes
        job.summary.preflight_form_field_count = preflight_artifact.signals.form_field_count
        job.summary.preflight_table_page_count = preflight_artifact.signals.estimated_table_page_count
        job.summary.preflight_multi_column_page_count = preflight_artifact.signals.multi_column_page_count
        job.summary.preflight_rtl_detected = preflight_artifact.signals.rtl_detected
        job.summary.lane_policy = lane_policy.name
        job.summary.ocr_mode = lane_policy.ocr_mode.value
        job.summary.manual_review_required = lane_policy.manual_review_required
        if lane_policy.ocr_mode == OCRMode.skip:
            ocr_artifact = OCRArtifact(
                document_id=document_id,
                engine="tesseract",
                engine_version=None,
                language=settings.default_ocr_language,
                attempted_page_count=0,
                completed_page_count=0,
                pages=[],
                errors=[],
            )
        else:
            ocr_artifact = run_tesseract_ocr(
                document_id=document_id,
                pdf_path=stored_pdf_path,
                parser_artifact=parser_artifact,
                settings=settings,
            )
        job.summary.ocr_attempted_page_count = ocr_artifact.attempted_page_count
        job.summary.ocr_completed_page_count = ocr_artifact.completed_page_count
        _advance_job_stage(
            job,
            store,
            JobStage.ocr_enriched,
            note=(
                f"OCR mode={lane_policy.ocr_mode.value}; "
                f"attempted {ocr_artifact.attempted_page_count} pages."
            ),
        )

        canonical_artifact = build_canonical_document(
            parser_artifact=parser_artifact,
            ocr_artifact=ocr_artifact,
        )
        _advance_job_stage(
            job,
            store,
            JobStage.canonicalized,
            note=f"Canonicalized into {canonical_artifact.total_block_count} blocks.",
        )

        remediated_canonical_artifact, remediation_artifact = run_remediation_pipeline(
            document=canonical_artifact,
            settings=settings,
            profile=job.compliance_profile,
        )
        if lane_policy.manual_review_required:
            for page in remediated_canonical_artifact.pages:
                page.needs_review = True
            remediation_artifact.review_flagged_page_count = sum(
                1 for page in remediated_canonical_artifact.pages if page.needs_review
            )

        _advance_job_stage(
            job,
            store,
            JobStage.remediated,
            note=f"Applied {remediation_artifact.action_count} remediation actions.",
        )

        # Write remediated PDF
        writer = PdfWriterService(settings)
        output_pdf_path = store.output_pdf_path(document_id)
        writer.write_remediated_pdf(
            original_pdf_path=stored_pdf_path,
            output_pdf_path=output_pdf_path,
            remediated_doc=remediated_canonical_artifact,
        )
        # Upload output PDF if using S3 (or ensure it's in the store)
        store.save_output_pdf(document_id, output_pdf_path.read_bytes())
        job.artifacts["output_pdf"] = store.relative_path(output_pdf_path)

        validation_artifact = run_validation_pipeline(
            document=remediated_canonical_artifact,
            settings=settings,
            profile=job.compliance_profile,
            preflight_artifact=preflight_artifact,
            manual_review_required=lane_policy.manual_review_required,
        )
        _advance_job_stage(
            job,
            store,
            JobStage.validated,
            note=f"Validation status: {validation_artifact.status.value}.",
        )
    except Exception as exc:
        processing_duration_seconds = max(0.0, time.perf_counter() - processing_started)
        job.summary.processing_duration_seconds = round(processing_duration_seconds, 4)
        job.summary.throughput_pages_per_second = (
            round(job.summary.page_count / processing_duration_seconds, 3)
            if job.summary.page_count and processing_duration_seconds > 0
            else None
        )
        failed_job = _fail_job(job, store, str(exc))
        record_job_telemetry(store=store, job=failed_job)
        return failed_job

    store.save_parser_artifact(parser_artifact)
    store.save_preflight_artifact(preflight_artifact)
    store.save_ocr_artifact(ocr_artifact)
    store.save_canonical_artifact(canonical_artifact)
    store.save_remediated_canonical_artifact(remediated_canonical_artifact)
    store.save_remediation_artifact(remediation_artifact)
    store.save_validation_artifact(validation_artifact)

    document.source_type = parser_artifact.source_type
    document.page_count = parser_artifact.page_count
    document.updated_at = utc_now()
    store.save_document_record(document)
    processing_duration_seconds = max(0.0, time.perf_counter() - processing_started)
    throughput_pages_per_second = (
        round(parser_artifact.page_count / processing_duration_seconds, 3)
        if processing_duration_seconds > 0
        else None
    )

    job.summary = JobSummary(
        page_count=parser_artifact.page_count,
        source_type=parser_artifact.source_type,
        processing_lane=preflight_artifact.lane,
        compliance_profile=job.compliance_profile,
        lane_policy=lane_policy.name,
        ocr_mode=lane_policy.ocr_mode.value,
        ocr_attempted_page_count=ocr_artifact.attempted_page_count,
        ocr_completed_page_count=ocr_artifact.completed_page_count,
        manual_review_required=lane_policy.manual_review_required,
        processing_duration_seconds=round(processing_duration_seconds, 4),
        throughput_pages_per_second=throughput_pages_per_second,
        preflight_classes=preflight_artifact.classes,
        preflight_form_field_count=preflight_artifact.signals.form_field_count,
        preflight_table_page_count=preflight_artifact.signals.estimated_table_page_count,
        preflight_multi_column_page_count=preflight_artifact.signals.multi_column_page_count,
        preflight_rtl_detected=preflight_artifact.signals.rtl_detected,
        text_page_count=parser_artifact.text_page_count,
        image_page_count=parser_artifact.image_page_count,
        ocr_page_count=remediated_canonical_artifact.ocr_page_count,
        canonical_block_count=remediated_canonical_artifact.total_block_count,
        remediation_action_count=remediation_artifact.action_count,
        remediation_changed_count=remediation_artifact.changed_action_count,
        remediation_review_pages=remediation_artifact.review_flagged_page_count,
        validation_status=validation_artifact.status,
        validation_finding_count=validation_artifact.finding_count,
    )
    job.artifacts["parser"] = store.relative_path(store.parser_artifact_path(document_id))
    job.artifacts["preflight"] = store.relative_path(store.preflight_artifact_path(document_id))
    job.artifacts["ocr"] = store.relative_path(store.ocr_artifact_path(document_id))
    job.artifacts["canonical"] = store.relative_path(store.canonical_artifact_path(document_id))
    job.artifacts["remediated_canonical"] = store.relative_path(
        store.remediated_canonical_artifact_path(document_id)
    )
    job.artifacts["remediation"] = store.relative_path(store.remediation_artifact_path(document_id))
    job.artifacts["validation"] = store.relative_path(store.validation_artifact_path(document_id))
    job.current_stage = JobStage.completed
    job.stage_events.append(JobStageEvent(stage=JobStage.completed, note="Pipeline finished."))
    job.updated_at = utc_now()
    job.status = JobStatus.succeeded
    store.save_job_record(job)
    record_job_telemetry(store=store, job=job)

    return job

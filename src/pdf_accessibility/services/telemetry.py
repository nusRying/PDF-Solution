from __future__ import annotations

from threading import Lock

from pdf_accessibility.models.documents import utc_now
from pdf_accessibility.models.jobs import JobRecord, JobStatus
from pdf_accessibility.models.preflight import ProcessingLane
from pdf_accessibility.models.telemetry import (
    LaneTelemetryArtifact,
    LaneTelemetryRecord,
)
from pdf_accessibility.services.file_store import FileStore

_TELEMETRY_LOCK = Lock()


def _default_lane_records() -> list[LaneTelemetryRecord]:
    return [
        LaneTelemetryRecord(lane=ProcessingLane.fast),
        LaneTelemetryRecord(lane=ProcessingLane.standard),
        LaneTelemetryRecord(lane=ProcessingLane.heavy),
        LaneTelemetryRecord(lane=ProcessingLane.manual),
    ]


def build_empty_lane_telemetry_artifact() -> LaneTelemetryArtifact:
    return LaneTelemetryArtifact(lanes=_default_lane_records())


def _get_or_create_lane_record(
    artifact: LaneTelemetryArtifact,
    lane: ProcessingLane,
) -> LaneTelemetryRecord:
    for record in artifact.lanes:
        if record.lane == lane:
            return record

    record = LaneTelemetryRecord(lane=lane)
    artifact.lanes.append(record)
    return record


def record_job_telemetry(
    store: FileStore,
    job: JobRecord,
) -> LaneTelemetryArtifact:
    with _TELEMETRY_LOCK:
        artifact = store.get_lane_telemetry_artifact() or build_empty_lane_telemetry_artifact()
        summary = job.summary
        totals = artifact.totals

        totals.total_attempt_count += 1
        if job.status == JobStatus.succeeded:
            totals.succeeded_count += 1
        elif job.status == JobStatus.failed:
            totals.failed_count += 1

        if summary.page_count:
            totals.total_page_count += summary.page_count
        if summary.processing_duration_seconds:
            totals.total_processing_duration_seconds = round(
                totals.total_processing_duration_seconds + summary.processing_duration_seconds,
                4,
            )

        lane = summary.processing_lane
        if lane is None:
            if job.status == JobStatus.failed:
                totals.unclassified_failure_count += 1
            artifact.generated_at = utc_now()
            store.save_lane_telemetry_artifact(artifact)
            return artifact

        totals.classified_attempt_count += 1
        record = _get_or_create_lane_record(artifact, lane)
        record.total_attempt_count += 1
        if job.status == JobStatus.succeeded:
            record.succeeded_count += 1
        elif job.status == JobStatus.failed:
            record.failed_count += 1

        if summary.manual_review_required:
            record.manual_review_attempt_count += 1
        if summary.page_count:
            record.total_page_count += summary.page_count
        if summary.ocr_attempted_page_count:
            record.total_ocr_attempted_page_count += summary.ocr_attempted_page_count
        if summary.ocr_completed_page_count:
            record.total_ocr_completed_page_count += summary.ocr_completed_page_count
        if summary.processing_duration_seconds:
            record.total_processing_duration_seconds = round(
                record.total_processing_duration_seconds + summary.processing_duration_seconds,
                4,
            )
        if summary.throughput_pages_per_second:
            record.total_throughput_pages_per_second = round(
                record.total_throughput_pages_per_second + summary.throughput_pages_per_second,
                4,
            )

        record.average_processing_duration_seconds = round(
            record.total_processing_duration_seconds / record.total_attempt_count,
            4,
        )
        successful_attempts = max(record.succeeded_count, 0)
        record.average_throughput_pages_per_second = (
            round(record.total_throughput_pages_per_second / successful_attempts, 4)
            if successful_attempts
            else None
        )
        record.success_rate = round(record.succeeded_count / record.total_attempt_count, 4)
        record.last_job_id = job.job_id
        record.last_status = job.status
        record.updated_at = utc_now()

        artifact.generated_at = utc_now()
        store.save_lane_telemetry_artifact(artifact)
        return artifact

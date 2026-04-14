from __future__ import annotations

from threading import Lock

from pdf_accessibility.models.documents import utc_now
from pdf_accessibility.models.jobs import JobRecord, JobStatus
from pdf_accessibility.models.preflight import ProcessingLane
from pdf_accessibility.models.telemetry import (
    LaneTelemetryArtifact,
    LaneTelemetryRecord,
    LaneTelemetryTotals,
)
from pdf_accessibility.services.file_store import BaseFileStore

_telemetry_lock = Lock()


def build_empty_lane_telemetry_artifact() -> LaneTelemetryArtifact:
    return LaneTelemetryArtifact(
        totals=LaneTelemetryTotals(),
        lanes=[
            LaneTelemetryRecord(lane=ProcessingLane.fast),
            LaneTelemetryRecord(lane=ProcessingLane.standard),
            LaneTelemetryRecord(lane=ProcessingLane.heavy),
            LaneTelemetryRecord(lane=ProcessingLane.manual),
        ],
    )


def record_job_telemetry(
    store: BaseFileStore,
    job: JobRecord,
) -> LaneTelemetryArtifact:
    with _telemetry_lock:
        artifact = store.get_lane_telemetry_artifact()
        if artifact is None:
            artifact = build_empty_lane_telemetry_artifact()

        # Update totals
        artifact.totals.total_attempt_count += 1
        if job.status == JobStatus.succeeded:
            artifact.totals.succeeded_count += 1
        elif job.status == JobStatus.failed:
            artifact.totals.failed_count += 1

        if job.summary.processing_lane:
            artifact.totals.classified_attempt_count += 1

        # Update lane-specific metrics
        lane_name = job.summary.processing_lane or ProcessingLane.standard
        record = next((r for r in artifact.lanes if r.lane == lane_name), None)
        if record is None:
            record = LaneTelemetryRecord(lane=lane_name)
            artifact.lanes.append(record)

        record.total_attempt_count += 1
        if job.status == JobStatus.succeeded:
            record.succeeded_count += 1
        elif job.status == JobStatus.failed:
            record.failed_count += 1

        if job.summary.page_count:
            record.total_page_count += job.summary.page_count

        if job.summary.ocr_attempted_page_count:
            record.total_ocr_attempted_page_count += job.summary.ocr_attempted_page_count

        if job.summary.ocr_completed_page_count:
            record.total_ocr_completed_page_count += job.summary.ocr_completed_page_count

        if job.summary.processing_duration_seconds:
            record.total_processing_duration_seconds += job.summary.processing_duration_seconds
            if job.summary.throughput_pages_per_second:
                record.average_throughput_pages_per_second = (
                    record.total_page_count / record.total_processing_duration_seconds
                )

        record.last_job_id = job.job_id
        record.last_status = job.status
        record.updated_at = utc_now()

        artifact.generated_at = utc_now()
        store.save_lane_telemetry_artifact(artifact)
        return artifact

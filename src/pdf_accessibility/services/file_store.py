from __future__ import annotations

import json
import time
from pathlib import Path
from uuid import uuid4

from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.documents import DocumentRecord, ParserArtifact
from pdf_accessibility.models.jobs import JobRecord
from pdf_accessibility.models.ocr import OCRArtifact
from pdf_accessibility.models.preflight import PreflightArtifact
from pdf_accessibility.models.remediation import RemediationArtifact
from pdf_accessibility.models.telemetry import LaneTelemetryArtifact
from pdf_accessibility.models.validation import ValidationArtifact


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.{uuid4().hex}.tmp")
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    for attempt in range(6):
        try:
            temp_path.replace(path)
            return
        except PermissionError:
            if attempt == 5:
                raise
            time.sleep(0.02 * (attempt + 1))


class FileStore:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def relative_path(self, path: Path) -> str:
        return str(path.relative_to(self.settings.data_root))

    def document_record_path(self, document_id: str) -> Path:
        return self.settings.document_records_dir / f"{document_id}.json"

    def job_record_path(self, job_id: str) -> Path:
        return self.settings.job_records_dir / f"{job_id}.json"

    def parser_artifact_path(self, document_id: str) -> Path:
        return self.settings.parser_artifacts_dir / f"{document_id}.json"

    def preflight_artifact_path(self, document_id: str) -> Path:
        return self.settings.preflight_artifacts_dir / f"{document_id}.json"

    def ocr_artifact_path(self, document_id: str) -> Path:
        return self.settings.ocr_artifacts_dir / f"{document_id}.json"

    def canonical_artifact_path(self, document_id: str) -> Path:
        return self.settings.canonical_artifacts_dir / f"{document_id}.json"

    def remediated_canonical_artifact_path(self, document_id: str) -> Path:
        return self.settings.remediated_canonical_artifacts_dir / f"{document_id}.json"

    def validation_artifact_path(self, document_id: str) -> Path:
        return self.settings.validation_reports_dir / f"{document_id}.json"

    def remediation_artifact_path(self, document_id: str) -> Path:
        return self.settings.remediation_reports_dir / f"{document_id}.json"

    def lane_telemetry_path(self) -> Path:
        return self.settings.telemetry_dir / "lane-rollup.json"

    def original_pdf_path(self, document_id: str, suffix: str = ".pdf") -> Path:
        return self.settings.originals_dir / f"{document_id}{suffix}"

    def save_document_record(self, record: DocumentRecord) -> None:
        _write_json(
            self.document_record_path(record.document_id),
            record.model_dump(mode="json"),
        )

    def save_job_record(self, record: JobRecord) -> None:
        _write_json(
            self.job_record_path(record.job_id),
            record.model_dump(mode="json"),
        )

    def save_parser_artifact(self, artifact: ParserArtifact) -> None:
        _write_json(
            self.parser_artifact_path(artifact.document_id),
            artifact.model_dump(mode="json"),
        )

    def save_preflight_artifact(self, artifact: PreflightArtifact) -> None:
        _write_json(
            self.preflight_artifact_path(artifact.document_id),
            artifact.model_dump(mode="json"),
        )

    def save_ocr_artifact(self, artifact: OCRArtifact) -> None:
        _write_json(
            self.ocr_artifact_path(artifact.document_id),
            artifact.model_dump(mode="json"),
        )

    def save_canonical_artifact(self, artifact: CanonicalDocument) -> None:
        _write_json(
            self.canonical_artifact_path(artifact.document_id),
            artifact.model_dump(mode="json"),
        )

    def save_remediated_canonical_artifact(self, artifact: CanonicalDocument) -> None:
        _write_json(
            self.remediated_canonical_artifact_path(artifact.document_id),
            artifact.model_dump(mode="json"),
        )

    def save_validation_artifact(self, artifact: ValidationArtifact) -> None:
        _write_json(
            self.validation_artifact_path(artifact.document_id),
            artifact.model_dump(mode="json"),
        )

    def save_remediation_artifact(self, artifact: RemediationArtifact) -> None:
        _write_json(
            self.remediation_artifact_path(artifact.document_id),
            artifact.model_dump(mode="json"),
        )

    def save_lane_telemetry_artifact(self, artifact: LaneTelemetryArtifact) -> None:
        _write_json(
            self.lane_telemetry_path(),
            artifact.model_dump(mode="json"),
        )

    def get_job_record(self, job_id: str) -> JobRecord | None:
        path = self.job_record_path(job_id)
        if not path.exists():
            return None
        return JobRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def get_document_record(self, document_id: str) -> DocumentRecord | None:
        path = self.document_record_path(document_id)
        if not path.exists():
            return None
        return DocumentRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def get_parser_artifact(self, document_id: str) -> ParserArtifact | None:
        path = self.parser_artifact_path(document_id)
        if not path.exists():
            return None
        return ParserArtifact.model_validate_json(path.read_text(encoding="utf-8"))

    def get_preflight_artifact(self, document_id: str) -> PreflightArtifact | None:
        path = self.preflight_artifact_path(document_id)
        if not path.exists():
            return None
        return PreflightArtifact.model_validate_json(path.read_text(encoding="utf-8"))

    def get_ocr_artifact(self, document_id: str) -> OCRArtifact | None:
        path = self.ocr_artifact_path(document_id)
        if not path.exists():
            return None
        return OCRArtifact.model_validate_json(path.read_text(encoding="utf-8"))

    def get_canonical_artifact(self, document_id: str) -> CanonicalDocument | None:
        path = self.canonical_artifact_path(document_id)
        if not path.exists():
            return None
        return CanonicalDocument.model_validate_json(path.read_text(encoding="utf-8"))

    def get_remediated_canonical_artifact(self, document_id: str) -> CanonicalDocument | None:
        path = self.remediated_canonical_artifact_path(document_id)
        if not path.exists():
            return None
        return CanonicalDocument.model_validate_json(path.read_text(encoding="utf-8"))

    def get_validation_artifact(self, document_id: str) -> ValidationArtifact | None:
        path = self.validation_artifact_path(document_id)
        if not path.exists():
            return None
        return ValidationArtifact.model_validate_json(path.read_text(encoding="utf-8"))

    def get_remediation_artifact(self, document_id: str) -> RemediationArtifact | None:
        path = self.remediation_artifact_path(document_id)
        if not path.exists():
            return None
        return RemediationArtifact.model_validate_json(path.read_text(encoding="utf-8"))

    def get_lane_telemetry_artifact(self) -> LaneTelemetryArtifact | None:
        path = self.lane_telemetry_path()
        if not path.exists():
            return None
        return LaneTelemetryArtifact.model_validate_json(path.read_text(encoding="utf-8"))

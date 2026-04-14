from __future__ import annotations

import json
import logging
from pathlib import Path
from tempfile import gettempdir

import boto3
from botocore.exceptions import ClientError

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.documents import DocumentRecord, ParserArtifact
from pdf_accessibility.models.jobs import JobRecord
from pdf_accessibility.models.ocr import OCRArtifact
from pdf_accessibility.models.preflight import PreflightArtifact
from pdf_accessibility.models.remediation import RemediationArtifact
from pdf_accessibility.models.review import ReviewArtifact
from pdf_accessibility.models.telemetry import LaneTelemetryArtifact
from pdf_accessibility.models.validation import ValidationArtifact
from pdf_accessibility.services.file_store import BaseFileStore

logger = logging.getLogger(__name__)


class S3FileStore(BaseFileStore):
    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self.s3 = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region_name,
        )
        self.bucket = settings.s3_bucket
        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except ClientError:
            try:
                self.s3.create_bucket(Bucket=self.bucket)
                logger.info(f"Created S3 bucket: {self.bucket}")
            except Exception as e:
                logger.error(f"Failed to create S3 bucket {self.bucket}: {e}")

    def _get_key(self, folder: str, document_id: str, suffix: str = ".json") -> str:
        return f"{folder}/{document_id}{suffix}"

    def _save_json(self, key: str, payload: dict) -> None:
        self.s3.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=json.dumps(payload, indent=2),
            ContentType="application/json",
        )

    def _get_json(self, key: str) -> dict | None:
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response["Body"].read().decode("utf-8"))
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return None
            raise

    # JSON Artifacts
    def save_document_record(self, record: DocumentRecord) -> None:
        self._save_json(self._get_key("manifests/documents", record.document_id), record.model_dump(mode="json"))

    def save_job_record(self, record: JobRecord) -> None:
        self._save_json(self._get_key("manifests/jobs", record.job_id), record.model_dump(mode="json"))

    def save_parser_artifact(self, artifact: ParserArtifact) -> None:
        self._save_json(self._get_key("intermediate/parser", artifact.document_id), artifact.model_dump(mode="json"))

    def save_preflight_artifact(self, artifact: PreflightArtifact) -> None:
        self._save_json(self._get_key("intermediate/preflight", artifact.document_id), artifact.model_dump(mode="json"))

    def save_ocr_artifact(self, artifact: OCRArtifact) -> None:
        self._save_json(self._get_key("intermediate/ocr", artifact.document_id), artifact.model_dump(mode="json"))

    def save_canonical_artifact(self, artifact: CanonicalDocument) -> None:
        self._save_json(self._get_key("intermediate/canonical", artifact.document_id), artifact.model_dump(mode="json"))

    def save_remediated_canonical_artifact(self, artifact: CanonicalDocument) -> None:
        self._save_json(self._get_key("intermediate/remediated-canonical", artifact.document_id), artifact.model_dump(mode="json"))

    def save_validation_artifact(self, artifact: ValidationArtifact) -> None:
        self._save_json(self._get_key("reports/validation", artifact.document_id), artifact.model_dump(mode="json"))

    def save_remediation_artifact(self, artifact: RemediationArtifact) -> None:
        self._save_json(self._get_key("reports/remediation", artifact.document_id), artifact.model_dump(mode="json"))

    def save_review_artifact(self, artifact: ReviewArtifact) -> None:
        self._save_json(self._get_key("review", artifact.document_id), artifact.model_dump(mode="json"))

    def save_lane_telemetry_artifact(self, artifact: LaneTelemetryArtifact) -> None:
        self._save_json("telemetry/lane-rollup.json", artifact.model_dump(mode="json"))

    def get_job_record(self, job_id: str) -> JobRecord | None:
        data = self._get_json(self._get_key("manifests/jobs", job_id))
        return JobRecord.model_validate(data) if data else None

    def get_document_record(self, document_id: str) -> DocumentRecord | None:
        data = self._get_json(self._get_key("manifests/documents", document_id))
        return DocumentRecord.model_validate(data) if data else None

    def get_parser_artifact(self, document_id: str) -> ParserArtifact | None:
        data = self._get_json(self._get_key("intermediate/parser", document_id))
        return ParserArtifact.model_validate(data) if data else None

    def get_preflight_artifact(self, document_id: str) -> PreflightArtifact | None:
        data = self._get_json(self._get_key("intermediate/preflight", document_id))
        return PreflightArtifact.model_validate(data) if data else None

    def get_ocr_artifact(self, document_id: str) -> OCRArtifact | None:
        data = self._get_json(self._get_key("intermediate/ocr", document_id))
        return OCRArtifact.model_validate(data) if data else None

    def get_canonical_artifact(self, document_id: str) -> CanonicalDocument | None:
        data = self._get_json(self._get_key("intermediate/canonical", document_id))
        return CanonicalDocument.model_validate(data) if data else None

    def get_remediated_canonical_artifact(self, document_id: str) -> CanonicalDocument | None:
        data = self._get_json(self._get_key("intermediate/remediated-canonical", document_id))
        return CanonicalDocument.model_validate(data) if data else None

    def get_validation_artifact(self, document_id: str) -> ValidationArtifact | None:
        data = self._get_json(self._get_key("reports/validation", document_id))
        return ValidationArtifact.model_validate(data) if data else None

    def get_remediation_artifact(self, document_id: str) -> RemediationArtifact | None:
        data = self._get_json(self._get_key("reports/remediation", document_id))
        return RemediationArtifact.model_validate(data) if data else None

    def get_review_artifact(self, document_id: str) -> ReviewArtifact | None:
        data = self._get_json(self._get_key("review", document_id))
        return ReviewArtifact.model_validate(data) if data else None

    def get_lane_telemetry_artifact(self) -> LaneTelemetryArtifact | None:
        data = self._get_json("telemetry/lane-rollup.json")
        return LaneTelemetryArtifact.model_validate(data) if data else None

    # Binary Artifacts
    def original_pdf_path(self, document_id: str, suffix: str = ".pdf") -> Path:
        # For S3, we download to a temporary file if a local path is required
        local_path = Path(gettempdir()) / f"s3_cache_{document_id}{suffix}"
        if not local_path.exists():
            try:
                self.s3.download_file(self.bucket, self._get_key("originals", document_id, suffix), str(local_path))
            except ClientError:
                # If not found in S3, we return the path anyway, it might be about to be saved
                pass
        return local_path

    def output_pdf_path(self, document_id: str, suffix: str = ".pdf") -> Path:
        local_path = Path(gettempdir()) / f"s3_cache_out_{document_id}{suffix}"
        return local_path

    def save_original_pdf(self, document_id: str, content: bytes, suffix: str = ".pdf") -> Path:
        key = self._get_key("originals", document_id, suffix)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType="application/pdf")
        # Also cache locally
        local_path = self.original_pdf_path(document_id, suffix)
        local_path.write_bytes(content)
        return local_path

    def save_output_pdf(self, document_id: str, content: bytes, suffix: str = ".pdf") -> Path:
        key = self._get_key("output", document_id, suffix)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType="application/pdf")
        # Also cache locally
        local_path = self.output_pdf_path(document_id, suffix)
        local_path.write_bytes(content)
        return local_path

    def get_original_pdf_content(self, document_id: str, suffix: str = ".pdf") -> bytes:
        response = self.s3.get_object(Bucket=self.bucket, Key=self._get_key("originals", document_id, suffix))
        return response["Body"].read()

    def get_output_pdf_content(self, document_id: str, suffix: str = ".pdf") -> bytes:
        response = self.s3.get_object(Bucket=self.bucket, Key=self._get_key("output", document_id, suffix))
        return response["Body"].read()

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "PDF Accessibility Remediation Platform"
    environment: str = "development"
    log_level: str = "INFO"
    host: str = "127.0.0.1"
    port: int = 8000
    api_prefix: str = "/api/v1"
    data_root: Path = PROJECT_ROOT / "data"
    qpdf_exe: str = "qpdf"
    tesseract_exe: str = str(Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"))
    tessdata_prefix: Path = Path(r"C:\Program Files\Tesseract-OCR\tessdata")
    default_ocr_language: str = "eng"
    ocr_low_confidence_threshold: float = 70.0
    ingest_worker_count: int = Field(default=1, ge=1)
    ingest_queue_poll_seconds: float = Field(default=0.5, ge=0.1, le=5.0)
    redis_url: str = "redis://localhost:6379/0"
    queue_backend: str = "threaded"  # "threaded" or "celery"

    # AI Settings
    ai_provider: str = "mock"  # "mock", "openai", "anthropic"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-3-5-sonnet-20240620"

    # Storage Settings
    storage_backend: str = "local"  # "local" or "s3"
    s3_bucket: str = "pdf-accessibility"
    s3_endpoint_url: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_region_name: str = "us-east-1"

    @field_validator("data_root", "tessdata_prefix", mode="before")
    @classmethod
    def normalize_paths(cls, value: str | Path) -> Path:
        return Path(value).expanduser()

    @computed_field
    @property
    def originals_dir(self) -> Path:
        return self.data_root / "originals"

    @computed_field
    @property
    def intermediate_dir(self) -> Path:
        return self.data_root / "intermediate"

    @computed_field
    @property
    def output_dir(self) -> Path:
        return self.data_root / "output"

    @computed_field
    @property
    def reports_dir(self) -> Path:
        return self.data_root / "reports"

    @computed_field
    @property
    def validation_reports_dir(self) -> Path:
        return self.reports_dir / "validation"

    @computed_field
    @property
    def review_dir(self) -> Path:
        return self.data_root / "review"

    @computed_field
    @property
    def review_artifacts_dir(self) -> Path:
        return self.review_dir

    @computed_field
    @property
    def manifests_dir(self) -> Path:
        return self.data_root / "manifests"

    @computed_field
    @property
    def telemetry_dir(self) -> Path:
        return self.data_root / "telemetry"

    @computed_field
    @property
    def document_records_dir(self) -> Path:
        return self.manifests_dir / "documents"

    @computed_field
    @property
    def job_records_dir(self) -> Path:
        return self.manifests_dir / "jobs"

    @computed_field
    @property
    def parser_artifacts_dir(self) -> Path:
        return self.intermediate_dir / "parser"

    @computed_field
    @property
    def preflight_artifacts_dir(self) -> Path:
        return self.intermediate_dir / "preflight"

    @computed_field
    @property
    def ocr_artifacts_dir(self) -> Path:
        return self.intermediate_dir / "ocr"

    @computed_field
    @property
    def canonical_artifacts_dir(self) -> Path:
        return self.intermediate_dir / "canonical"

    @computed_field
    @property
    def remediated_canonical_artifacts_dir(self) -> Path:
        return self.intermediate_dir / "remediated-canonical"

    @computed_field
    @property
    def remediation_reports_dir(self) -> Path:
        return self.reports_dir / "remediation"

    def ensure_directories(self) -> None:
        for directory in (
            self.data_root,
            self.originals_dir,
            self.intermediate_dir,
            self.output_dir,
            self.reports_dir,
            self.validation_reports_dir,
            self.review_dir,
            self.telemetry_dir,
            self.manifests_dir,
            self.document_records_dir,
            self.job_records_dir,
            self.parser_artifacts_dir,
            self.preflight_artifacts_dir,
            self.ocr_artifacts_dir,
            self.canonical_artifacts_dir,
            self.remediated_canonical_artifacts_dir,
            self.remediation_reports_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()

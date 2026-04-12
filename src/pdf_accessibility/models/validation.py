from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from pdf_accessibility.models.compliance import ComplianceProfile, ComplianceStandard
from pdf_accessibility.models.documents import BoundingBox, utc_now


class ValidationSeverity(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"


class ValidationStatus(str, Enum):
    passed = "passed"
    needs_review = "needs-review"
    failed = "failed"


class StandardMapping(BaseModel):
    standard: ComplianceStandard
    rule_id: str
    criterion: str | None = None


class ValidationFinding(BaseModel):
    rule_id: str
    severity: ValidationSeverity
    message: str
    page_number: int | None = None
    block_id: str | None = None
    bbox: BoundingBox | None = None
    source: str
    standards: list[StandardMapping] = Field(default_factory=list)


class ValidationArtifact(BaseModel):
    document_id: str
    profile: ComplianceProfile = ComplianceProfile.profile_b
    generated_at: datetime = Field(default_factory=utc_now)
    rule_catalog_version: str = "0.1.0"
    status: ValidationStatus
    finding_count: int
    error_count: int
    warning_count: int
    findings: list[ValidationFinding] = Field(default_factory=list)

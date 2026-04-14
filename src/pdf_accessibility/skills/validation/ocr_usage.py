from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.compliance import ComplianceStandard
from pdf_accessibility.models.validation import ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import SkillCategory, ValidationSkill


class OCRUsageValidationSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-OCR-002"

    @property
    def name(self) -> str:
        return "OCR Usage Check"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return "Flags pages where content was derived from OCR, indicating a need for human review."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.ocr

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        for page in canonical_doc.pages:
            if page.used_ocr:
                findings.append(
                    ValidationFinding(
                        rule_id=self.skill_id,
                        severity=ValidationSeverity.warning,
                        message="Page content was derived from OCR and should be reviewed.",
                        page_number=page.page_number,
                        source="ocr",
                    )
                )
        return findings

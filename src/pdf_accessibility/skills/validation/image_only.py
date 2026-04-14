from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.compliance import ComplianceStandard
from pdf_accessibility.models.documents import DocumentSourceType
from pdf_accessibility.models.validation import StandardMapping, ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import SkillCategory, ValidationSkill


class ImageOnlyValidationSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-DOC-001"

    @property
    def name(self) -> str:
        return "Image-only Document Check"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return "Checks if the document is scanned or image-only and depends on OCR."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.ocr

    @property
    def standards(self) -> list[ComplianceStandard]:
        return [ComplianceStandard.pdf_ua_1]

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        if canonical_doc.source_type in {DocumentSourceType.scanned, DocumentSourceType.image_only}:
            findings.append(
                ValidationFinding(
                    rule_id=self.skill_id,
                    severity=ValidationSeverity.info,
                    message="Document is image-based and depends on OCR-derived text.",
                    source="classifier",
                    standards=[
                        StandardMapping(
                            standard=ComplianceStandard.pdf_ua_1,
                            rule_id="Matterhorn 01",
                            criterion="Real content must be tagged.",
                        )
                    ],
                )
            )
        return findings

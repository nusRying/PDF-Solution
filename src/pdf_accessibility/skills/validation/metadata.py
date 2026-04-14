from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.compliance import ComplianceStandard
from pdf_accessibility.models.validation import StandardMapping, ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import SkillCategory, ValidationSkill


class DocumentTitleValidationSkill(ValidationSkill):
    """
    Checks if the document has a non-empty title in metadata.
    """

    @property
    def skill_id(self) -> str:
        return "VALID-META-001"

    @property
    def name(self) -> str:
        return "Document Title Presence"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return "Checks if the document has a non-empty title in metadata."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.metadata

    @property
    def standards(self) -> list[ComplianceStandard]:
        return [ComplianceStandard.wcag_2_1_aa]

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        
        if not canonical_doc.metadata.title or not canonical_doc.metadata.title.strip():
            findings.append(
                ValidationFinding(
                    rule_id=self.skill_id,
                    severity=ValidationSeverity.error,
                    message="Document title is missing in metadata.",
                    source="validation",
                    standards=[
                        StandardMapping(
                            standard=ComplianceStandard.wcag_2_1_aa,
                            rule_id="2.4.2",
                            criterion="Page Titled",
                        )
                    ],
                )
            )
            
        return findings

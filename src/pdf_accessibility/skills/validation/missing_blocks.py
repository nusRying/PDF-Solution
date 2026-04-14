from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.compliance import ComplianceStandard
from pdf_accessibility.models.validation import StandardMapping, ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import SkillCategory, ValidationSkill


class MissingBlocksValidationSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-CANON-001"

    @property
    def name(self) -> str:
        return "Missing Canonical Blocks Check"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return "Validates that each page in the canonical document has at least one text block."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.structural_fix

    @property
    def standards(self) -> list[ComplianceStandard]:
        return [ComplianceStandard.wcag_2_1_aa]

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        for page in canonical_doc.pages:
            if page.block_count == 0:
                findings.append(
                    ValidationFinding(
                        rule_id=self.skill_id,
                        severity=ValidationSeverity.error,
                        message="Page has no canonical text blocks.",
                        page_number=page.page_number,
                        source="canonical",
                        standards=[
                            StandardMapping(
                                standard=ComplianceStandard.wcag_2_1_aa,
                                rule_id="1.1.1",
                                criterion="Non-text Content",
                            )
                        ],
                    )
                )
        return findings

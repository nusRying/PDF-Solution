from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalRole
from pdf_accessibility.models.compliance import ComplianceStandard
from pdf_accessibility.models.validation import StandardMapping, ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import SkillCategory, ValidationSkill


class FigureAltTextValidationSkill(ValidationSkill):
    """
    Validates that all figures have descriptive alternative text.
    """

    @property
    def skill_id(self) -> str:
        return "VALID-FIG-001"

    @property
    def name(self) -> str:
        return "Figure Alt-Text Check"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return "Validates that all figures have descriptive alternative text."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.figures

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
            for block in page.blocks:
                if block.role == CanonicalRole.figure:
                    if not block.alt_text or not block.alt_text.strip():
                        findings.append(
                            ValidationFinding(
                                rule_id=self.skill_id,
                                severity=ValidationSeverity.error,
                                message=f"Figure missing alternative text on page {page.page_number}.",
                                page_number=page.page_number,
                                block_id=block.block_id,
                                bbox=block.bbox,
                                source="validation",
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

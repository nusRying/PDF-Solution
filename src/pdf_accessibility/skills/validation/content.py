from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalRole
from pdf_accessibility.models.validation import ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import SkillCategory, ValidationSkill


class FigureAltSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        # We use a combined skill ID or handle multiple in one. 
        # The plan mentions VALID-MH-14-001 and VALID-MH-14-003.
        return "VALID-MH-14-001"

    @property
    def name(self) -> str:
        return "Figure Alternate Text"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Check for presence and non-emptiness of alt_text on Figure blocks."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.figures

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings = []
        for page in canonical_doc.pages:
            for block in page.blocks:
                if block.role == CanonicalRole.figure:
                    if block.alt_text is None:
                        findings.append(
                            ValidationFinding(
                                rule_id="VALID-MH-14-001",
                                severity=ValidationSeverity.error,
                                message="Figure missing alternate text",
                                page_number=page.page_number,
                                block_id=block.block_id,
                                bbox=block.bbox,
                                source=self.name,
                            )
                        )
                    elif not block.alt_text.strip():
                        findings.append(
                            ValidationFinding(
                                rule_id="VALID-MH-14-003",
                                severity=ValidationSeverity.error,
                                message="Figure alternate text is empty or whitespace only",
                                page_number=page.page_number,
                                block_id=block.block_id,
                                bbox=block.bbox,
                                source=self.name,
                            )
                        )
        return findings

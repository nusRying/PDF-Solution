from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalRole
from pdf_accessibility.models.compliance import ComplianceStandard
from pdf_accessibility.models.validation import StandardMapping, ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import SkillCategory, ValidationSkill


class HeadingHierarchyValidationSkill(ValidationSkill):
    """
    Checks for logical heading level continuity (e.g. no H1 -> H3 skips).
    """

    @property
    def skill_id(self) -> str:
        return "VALID-HEAD-001"

    @property
    def name(self) -> str:
        return "Heading Level Continuity"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return "Ensures heading levels follow a logical hierarchy (e.g., no H1 to H3 jump)."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.headings

    @property
    def standards(self) -> list[ComplianceStandard]:
        return [ComplianceStandard.wcag_2_1_aa]

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        
        role_to_level = {
            CanonicalRole.heading1: 1,
            CanonicalRole.heading2: 2,
            CanonicalRole.heading3: 3,
            CanonicalRole.heading4: 4,
            CanonicalRole.heading5: 5,
            CanonicalRole.heading6: 6,
        }
        
        last_level = 0
        
        for page in canonical_doc.pages:
            for block in page.blocks:
                if block.role in role_to_level:
                    current_level = role_to_level[block.role]
                    
                    if last_level > 0 and current_level > last_level + 1:
                        findings.append(
                            ValidationFinding(
                                rule_id=self.skill_id,
                                severity=ValidationSeverity.error,
                                message=(
                                    f"Illogical heading jump from H{last_level} to H{current_level} "
                                    f"on page {page.page_number}."
                                ),
                                page_number=page.page_number,
                                block_id=block.block_id,
                                bbox=block.bbox,
                                source="validation",
                                standards=[
                                    StandardMapping(
                                        standard=ComplianceStandard.wcag_2_1_aa,
                                        rule_id="1.3.1",
                                        criterion="Info and Relationships",
                                    )
                                ],
                            )
                        )
                    last_level = current_level
                    
        return findings

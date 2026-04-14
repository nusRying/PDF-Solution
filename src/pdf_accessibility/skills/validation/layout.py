from __future__ import annotations

import math

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalRole
from pdf_accessibility.models.compliance import ComplianceStandard
from pdf_accessibility.models.validation import StandardMapping, ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import SkillCategory, ValidationSkill


class ReadingOrderJumpSkill(ValidationSkill):
    """
    Detects significant vertical or horizontal jumps in reading order
    that might indicate an incorrect layout reconstruction.
    """

    @property
    def skill_id(self) -> str:
        return "VALID-LAYOUT-001"

    @property
    def name(self) -> str:
        return "Reading Order Jump Check"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return "Detects illogical reading order jumps across the page."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.reading_order

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings: list[ValidationFinding] = []
        for page in canonical_doc.pages:
            if len(page.blocks) < 2:
                continue

            for i in range(len(page.blocks) - 1):
                curr = page.blocks[i]
                nxt = page.blocks[i + 1]

                # If the next block is significantly ABOVE the current one
                # AND it's not a common layout pattern (like top of a new column), flag it.
                if (curr.bbox.y0 - nxt.bbox.y1) > 200:
                    findings.append(
                        ValidationFinding(
                            rule_id=self.skill_id,
                            severity=ValidationSeverity.warning,
                            message=(
                                f"Possible illogical reading order jump on page {page.page_number}. "
                                f"Block '{nxt.text[:20]}...' is significantly above "
                                f"block '{curr.text[:20]}...'."
                            ),
                            page_number=page.page_number,
                            source="layout",
                        )
                    )
        return findings


class HeadingStructureSkill(ValidationSkill):
    """
    Validates the presence of document structure (headings).
    """

    @property
    def skill_id(self) -> str:
        return "VALID-LAYOUT-002"

    @property
    def name(self) -> str:
        return "Heading Structure Check"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return "Checks if the document has at least one heading."

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
        heading_roles = {
            CanonicalRole.heading1,
            CanonicalRole.heading2,
            CanonicalRole.heading3,
            CanonicalRole.heading4,
            CanonicalRole.heading5,
            CanonicalRole.heading6,
        }

        has_heading = any(
            block.role in heading_roles
            for page in canonical_doc.pages
            for block in page.blocks
        )

        if not has_heading and canonical_doc.total_text_char_count > 500:
            findings.append(
                ValidationFinding(
                    rule_id=self.skill_id,
                    severity=ValidationSeverity.warning,
                    message="Document has no detected headings. Structure might be missing.",
                    source="layout",
                    standards=[
                        StandardMapping(
                            standard=ComplianceStandard.wcag_2_1_aa,
                            rule_id="1.3.1",
                            criterion="Info and Relationships",
                        )
                    ],
                )
            )
        return findings

from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalRole
from pdf_accessibility.models.validation import ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import SkillCategory, ValidationSkill


class HeadingHierarchySkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-MH-13-004"

    @property
    def name(self) -> str:
        return "Heading Hierarchy"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Detect skipped heading levels (e.g., H1 -> H3)."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.headings

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings = []
        last_level = 0
        
        heading_roles = {
            CanonicalRole.heading1: 1,
            CanonicalRole.heading2: 2,
            CanonicalRole.heading3: 3,
            CanonicalRole.heading4: 4,
            CanonicalRole.heading5: 5,
            CanonicalRole.heading6: 6,
        }

        for page in canonical_doc.pages:
            for block in page.blocks:
                if block.role in heading_roles:
                    current_level = heading_roles[block.role]
                    if current_level > last_level + 1:
                        findings.append(
                            ValidationFinding(
                                rule_id=self.skill_id,
                                severity=ValidationSeverity.error,
                                message=f"Skipped heading level: H{last_level} to H{current_level}",
                                page_number=page.page_number,
                                block_id=block.block_id,
                                bbox=block.bbox,
                                source=self.name,
                            )
                        )
                    last_level = current_level
        return findings


class FirstHeadingSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-MH-13-001"

    @property
    def name(self) -> str:
        return "First Heading Level"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Verify the first heading in the document is H1."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.headings

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings = []
        heading_roles = {
            CanonicalRole.heading1,
            CanonicalRole.heading2,
            CanonicalRole.heading3,
            CanonicalRole.heading4,
            CanonicalRole.heading5,
            CanonicalRole.heading6,
        }

        for page in canonical_doc.pages:
            for block in page.blocks:
                if block.role in heading_roles:
                    if block.role != CanonicalRole.heading1:
                        findings.append(
                            ValidationFinding(
                                rule_id=self.skill_id,
                                severity=ValidationSeverity.error,
                                message=f"First heading in document should be H1, found {block.role.value}",
                                page_number=page.page_number,
                                block_id=block.block_id,
                                bbox=block.bbox,
                                source=self.name,
                            )
                        )
                    return findings  # Only check the very first heading
        return findings


class TableTHSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-MH-15-001"

    @property
    def name(self) -> str:
        return "Table Header Check"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Check if tables have at least one Header cell (TH)."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.tables

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings = []
        for page in canonical_doc.pages:
            for table in page.tables:
                has_th = False
                for row in table.rows:
                    for cell in row.cells:
                        if cell.role == CanonicalRole.table_header:
                            has_th = True
                            break
                    if has_th:
                        break
                
                if not has_th:
                    findings.append(
                        ValidationFinding(
                            rule_id=self.skill_id,
                            severity=ValidationSeverity.error,
                            message="Table missing header cells (TH)",
                            page_number=page.page_number,
                            block_id=table.table_id,
                            bbox=table.bbox,
                            source=self.name,
                        )
                    )
        return findings

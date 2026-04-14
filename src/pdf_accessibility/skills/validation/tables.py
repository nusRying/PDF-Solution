from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.validation import ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import ValidationSkill, SkillCategory

class TableStructureSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-TBL-001"

    @property
    def name(self) -> str:
        return "Table Structural Integrity"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Ensures tables have at least one row and no empty cells where content is expected."

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
                if not table.rows:
                    findings.append(ValidationFinding(
                        rule_id=self.skill_id,
                        severity=ValidationSeverity.error,
                        message=f"Table '{table.table_id}' has no rows.",
                        page_number=page.page_number,
                        block_id=table.table_id,
                        bbox=table.bbox,
                        source=self.name,
                    ))
                    continue
                
                for r_idx, row in enumerate(table.rows):
                    if not row.cells:
                         findings.append(ValidationFinding(
                            rule_id=self.skill_id,
                            severity=ValidationSeverity.error,
                            message=f"Table '{table.table_id}', Row {r_idx} has no cells.",
                            page_number=page.page_number,
                            block_id=table.table_id,
                            bbox=table.bbox,
                            source=self.name,
                        ))
        
        return findings

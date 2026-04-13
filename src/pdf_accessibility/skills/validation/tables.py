from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.validation import ValidationFinding, ValidationLevel, ValidationStatus
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
        return SkillCategory.structural_validation

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
                        finding_id=f"{page.page_number}-{table.id}-VALID-TBL-001-EMPTY",
                        rule_id=self.skill_id,
                        page_number=page.page_number,
                        level=ValidationLevel.error,
                        status=ValidationStatus.fail,
                        description=f"Table '{table.id}' has no rows.",
                        location=f"Page {page.page_number}, Table {table.id}"
                    ))
                    continue
                
                for r_idx, row in enumerate(table.rows):
                    if not row.cells:
                         findings.append(ValidationFinding(
                            finding_id=f"{page.page_number}-{table.id}-ROW-{r_idx}-VALID-TBL-001-EMPTY",
                            rule_id=self.skill_id,
                            page_number=page.page_number,
                            level=ValidationLevel.error,
                            status=ValidationStatus.fail,
                            description=f"Table '{table.id}', Row {r_idx} has no cells.",
                            location=f"Page {page.page_number}, Table {table.id}, Row {r_idx}"
                        ))
        
        return findings

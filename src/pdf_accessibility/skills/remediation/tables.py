from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalRole
from pdf_accessibility.models.remediation import RemediationAction
from pdf_accessibility.skills.base import RemediationSkill, SkillCategory
from pdf_accessibility.services.tables import TableDetectionService

class TableRepairSkill(RemediationSkill):
    @property
    def skill_id(self) -> str:
        return "REMED-TBL-001"

    @property
    def name(self) -> str:
        return "Table Structure Repair"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Assigns correct roles (table_header, table_data) to blocks within detected table structures."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.tables

    def remediate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[RemediationAction]:
        actions = []
        detector = TableDetectionService()
        
        # Build block lookup
        block_lookup = {}
        for page in canonical_doc.pages:
            for block in page.blocks:
                block_lookup[block.block_id] = block
        
        for page in canonical_doc.pages:
            # If no tables detected yet, run detection
            if not page.tables:
                page.tables = detector.detect_tables(page)
                if page.tables:
                    actions.append(RemediationAction(
                        action_id=f"{page.page_number}-detect-REMED-TBL-001",
                        rule_id=self.skill_id,
                        page_number=page.page_number,
                        source="deterministic-remediation",
                        description=f"Detected {len(page.tables)} table(s) on page {page.page_number}.",
                        changed=True
                    ))

            for table in page.tables:
                for row_idx, row in enumerate(table.rows):
                    for cell in row.cells:
                        # Infer role: first row should be header unless explicitly already header
                        # If it's generic 'table' or 'table_data' in first row, promote to header
                        if cell.role == CanonicalRole.table or (row_idx == 0 and cell.role == CanonicalRole.table_data):
                             role = CanonicalRole.table_header if row_idx == 0 else CanonicalRole.table_data
                             cell.role = role
                        else:
                             role = cell.role
                        
                        for block_id in cell.block_ids:
                            if block_id in block_lookup:
                                block = block_lookup[block_id]
                                if block.role != role:
                                    old_role = block.role
                                    block.role = role
                                    actions.append(RemediationAction(
                                        action_id=f"{page.page_number}-{block_id}-REMED-TBL-001",
                                        rule_id=self.skill_id,
                                        page_number=page.page_number,
                                        block_id=block_id,
                                        source="deterministic-remediation",
                                        description=f"Assigned {role.value} role to table cell block.",
                                        changed=True,
                                        field_name="role",
                                        before_value=old_role.value if old_role else None,
                                        after_value=role.value
                                    ))
        
        return actions

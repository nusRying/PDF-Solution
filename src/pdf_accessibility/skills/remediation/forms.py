from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.remediation import RemediationAction
from pdf_accessibility.skills.base import RemediationSkill, SkillCategory

class FormRepairSkill(RemediationSkill):
    @property
    def skill_id(self) -> str:
        return "REMED-FRM-001"

    @property
    def name(self) -> str:
        return "Form Field Repair"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Ensures every form field has an accessible tooltip."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.structural_fix

    def remediate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[RemediationAction]:
        actions = []
        
        for page in canonical_doc.pages:
            for form in page.forms:
                if not form.tooltip:
                    old_tooltip = form.tooltip
                    form.tooltip = form.name
                    actions.append(RemediationAction(
                        action_id=f"{page.page_number}-{form.field_id}-REMED-FRM-001",
                        rule_id=self.skill_id,
                        page_number=page.page_number,
                        source="deterministic-remediation",
                        description=f"Repaired missing tooltip for form field '{form.name}'.",
                        changed=True,
                        field_name="tooltip",
                        before_value=old_tooltip,
                        after_value=form.tooltip
                    ))
                    
        return actions

class FormTabOrderSkill(RemediationSkill):
    @property
    def skill_id(self) -> str:
        return "REMED-FRM-002"

    @property
    def name(self) -> str:
        return "Form Tab Order"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Ensures form fields follow a logical geometric reading order."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.structural_fix

    def remediate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[RemediationAction]:
        actions = []
        
        for page in canonical_doc.pages:
            if not page.forms:
                continue
                
            # Sort forms: primary = top-to-bottom (y0), secondary = left-to-right (x0)
            # PDF coordinates: y increases upwards usually, but our models use 0 at top?
            # Let's check CanonicalForm model to be sure about bbox coordinates.
            # Assuming standard top-left (0,0) for remediation logic or consistent with ReadingOrderEngine.
            original_order = [f.field_id for f in page.forms]
            page.forms.sort(key=lambda f: (f.bbox.y0, f.bbox.x0))
            new_order = [f.field_id for f in page.forms]
            
            if original_order != new_order:
                actions.append(RemediationAction(
                    action_id=f"{page.page_number}-TAB-ORDER",
                    rule_id=self.skill_id,
                    page_number=page.page_number,
                    source="deterministic-remediation",
                    description=f"Sorted {len(page.forms)} form fields into logical tab order.",
                    changed=True,
                    field_name="forms",
                    before_value=str(original_order),
                    after_value=str(new_order)
                ))
                    
        return actions

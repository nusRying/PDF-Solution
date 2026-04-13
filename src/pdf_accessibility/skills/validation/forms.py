from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.validation import ValidationFinding, ValidationLevel, ValidationStatus
from pdf_accessibility.skills.base import ValidationSkill, SkillCategory

class FormFieldValidationSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-FRM-001"

    @property
    def name(self) -> str:
        return "Form Field Validation"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Ensures form fields have names and accessible tooltips."

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
            for form in page.forms:
                if not form.name:
                    findings.append(ValidationFinding(
                        finding_id=f"{page.page_number}-{form.field_id}-VALID-FRM-001-NAME",
                        rule_id=self.skill_id,
                        page_number=page.page_number,
                        level=ValidationLevel.error,
                        status=ValidationStatus.fail,
                        description=f"Form field on page {page.page_number} is missing a name.",
                        location=f"Page {page.page_number}, Field ID {form.field_id}"
                    ))
                
                if not form.tooltip:
                    findings.append(ValidationFinding(
                        finding_id=f"{page.page_number}-{form.field_id}-VALID-FRM-001-TOOLTIP",
                        rule_id=self.skill_id,
                        page_number=page.page_number,
                        level=ValidationLevel.error,
                        status=ValidationStatus.fail,
                        description=f"Form field '{form.name}' is missing an accessible tooltip.",
                        location=f"Page {page.page_number}, Field {form.name}"
                    ))
        
        return findings

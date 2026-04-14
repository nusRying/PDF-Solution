from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.validation import ValidationFinding, ValidationSeverity
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
        return SkillCategory.forms

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
                        rule_id=self.skill_id,
                        severity=ValidationSeverity.error,
                        message=f"Form field on page {page.page_number} is missing a name.",
                        page_number=page.page_number,
                        block_id=form.field_id,
                        bbox=form.bbox,
                        source=self.name,
                    ))
                
                if not form.tooltip:
                    findings.append(ValidationFinding(
                        rule_id=self.skill_id,
                        severity=ValidationSeverity.error,
                        message=f"Form field '{form.name}' is missing an accessible tooltip.",
                        page_number=page.page_number,
                        block_id=form.field_id,
                        bbox=form.bbox,
                        source=self.name,
                    ))
        
        return findings

from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.validation import ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import SkillCategory, ValidationSkill


class DocumentLanguageSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-WCAG-3.1.1"

    @property
    def name(self) -> str:
        return "Document Language"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Verify that document language metadata is set."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.metadata

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings = []
        if not canonical_doc.metadata.language or not canonical_doc.metadata.language.strip():
            findings.append(
                ValidationFinding(
                    rule_id=self.skill_id,
                    severity=ValidationSeverity.error,
                    message="Document language metadata is not set",
                    source=self.name,
                )
            )
        return findings


class PageTitleSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-WCAG-2.4.2"

    @property
    def name(self) -> str:
        return "Document Title"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Verify that document title metadata is set."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.metadata

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings = []
        if not canonical_doc.metadata.title or not canonical_doc.metadata.title.strip():
            findings.append(
                ValidationFinding(
                    rule_id=self.skill_id,
                    severity=ValidationSeverity.error,
                    message="Document title metadata is not set",
                    source=self.name,
                )
            )
        return findings

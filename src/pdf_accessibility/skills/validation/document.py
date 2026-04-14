from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.validation import ValidationFinding, ValidationSeverity
from pdf_accessibility.skills.base import SkillCategory, ValidationSkill


class MarkInfoSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-MH-01-001"

    @property
    def name(self) -> str:
        return "Tagged PDF Flag"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Verify is_tagged flag in document metadata."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.metadata

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings = []
        if not canonical_doc.metadata.is_tagged:
            findings.append(
                ValidationFinding(
                    rule_id=self.skill_id,
                    severity=ValidationSeverity.error,
                    message="Document is not marked as tagged",
                    source=self.name,
                )
            )
        return findings


class StructTreeSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-MH-01-004"

    @property
    def name(self) -> str:
        return "Structure Tree"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Verify has_struct_tree flag in document metadata."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.metadata

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings = []
        if not canonical_doc.metadata.has_struct_tree:
            findings.append(
                ValidationFinding(
                    rule_id=self.skill_id,
                    severity=ValidationSeverity.error,
                    message="Document missing structure tree",
                    source=self.name,
                )
            )
        return findings


class PDFUAIdentifierSkill(ValidationSkill):
    @property
    def skill_id(self) -> str:
        return "VALID-MH-04-001"

    @property
    def name(self) -> str:
        return "PDF/UA Identifier"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Verify is_pdf_ua_identifier_present flag in document metadata."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.metadata

    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        findings = []
        if not canonical_doc.metadata.is_pdf_ua_identifier_present:
            findings.append(
                ValidationFinding(
                    rule_id=self.skill_id,
                    severity=ValidationSeverity.warning,
                    message="Document missing PDF/UA identifier",
                    source=self.name,
                )
            )
        return findings

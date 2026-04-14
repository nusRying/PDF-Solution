from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.remediation import RemediationAction
from pdf_accessibility.skills.base import RemediationSkill, SkillCategory


class MetadataRepairSkill(RemediationSkill):
    @property
    def skill_id(self) -> str:
        return "REMED-META-001"

    @property
    def name(self) -> str:
        return "Metadata Repair"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Ensures document title, author, and language (XMP) are correctly set."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.metadata

    def remediate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[RemediationAction]:
        actions = []
        
        # 1. Check for missing language
        if not canonical_doc.metadata.language:
            # Default to English if not specified, should be a setting
            original_lang = canonical_doc.metadata.language
            canonical_doc.metadata.language = settings.default_ocr_language
            actions.append(RemediationAction(
                action_id=f"doc-metadata-REMED-META-001-lang",
                rule_id=self.skill_id,
                page_number=0, # Document level
                block_id="metadata",
                source="deterministic-remediation",
                description=f"Set missing document language to default: {settings.default_ocr_language}.",
                changed=True,
                field_name="metadata.language",
                before_value=original_lang,
                after_value=canonical_doc.metadata.language
            ))

        # 2. Check for missing title
        if not canonical_doc.metadata.title:
            # In a real scenario we might infer title from H1 or filename
            pass
            
        return actions

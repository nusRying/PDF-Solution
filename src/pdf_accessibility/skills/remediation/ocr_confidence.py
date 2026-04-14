from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument, ContentSource
from pdf_accessibility.models.remediation import RemediationAction
from pdf_accessibility.skills.base import RemediationSkill, SkillCategory


class OCRConfidenceSkill(RemediationSkill):
    @property
    def skill_id(self) -> str:
        return "REMED-OCR-010"

    @property
    def name(self) -> str:
        return "OCR Confidence Review Flag"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return "Flags OCR blocks with confidence below the configured threshold for manual review."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.ocr

    def remediate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[RemediationAction]:
        actions: list[RemediationAction] = []
        for page in canonical_doc.pages:
            for block in page.blocks:
                if block.source == ContentSource.ocr and block.confidence is not None:
                    if block.confidence < settings.ocr_low_confidence_threshold:
                        page.needs_review = True
                        actions.append(
                            RemediationAction(
                                action_id=f"{page.page_number}-{block.block_id}-OCR-010",
                                rule_id=self.skill_id,
                                page_number=page.page_number,
                                block_id=block.block_id,
                                source="deterministic-remediation",
                                description="Low-confidence OCR block flagged for review.",
                                changed=False,
                                confidence=block.confidence,
                            )
                        )
        return actions

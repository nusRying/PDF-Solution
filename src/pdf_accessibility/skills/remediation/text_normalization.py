from __future__ import annotations

import re

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.remediation import RemediationAction
from pdf_accessibility.skills.base import RemediationSkill, SkillCategory


class TextNormalizationSkill(RemediationSkill):
    @property
    def skill_id(self) -> str:
        return "REMED-TEXT-001"

    @property
    def name(self) -> str:
        return "Text Whitespace Normalization"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def description(self) -> str:
        return "Normalizes block text by removing control characters and collapsing whitespace."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.metadata

    def _normalize_text(self, text: str) -> str:
        without_nulls = text.replace("\x00", " ")
        return re.sub(r"\s+", " ", without_nulls).strip()

    def remediate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[RemediationAction]:
        actions: list[RemediationAction] = []
        for page in canonical_doc.pages:
            for block in page.blocks:
                normalized_text = self._normalize_text(block.text)
                if normalized_text != block.text:
                    actions.append(
                        RemediationAction(
                            action_id=f"{page.page_number}-{block.block_id}-TEXT-001",
                            rule_id=self.skill_id,
                            page_number=page.page_number,
                            block_id=block.block_id,
                            source="deterministic-remediation",
                            description="Normalized block text whitespace and control characters.",
                            changed=True,
                            before_text=block.text,
                            after_text=normalized_text,
                        )
                    )
                    block.text = normalized_text
                    block.char_count = len(normalized_text)
        return actions

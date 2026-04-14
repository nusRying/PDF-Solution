from __future__ import annotations

from collections import defaultdict
from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalRole
from pdf_accessibility.models.remediation import RemediationAction
from pdf_accessibility.skills.base import RemediationSkill, SkillCategory


class ArtifactClassificationSkill(RemediationSkill):
    @property
    def skill_id(self) -> str:
        return "REMED-ARTI-001"

    @property
    def name(self) -> str:
        return "Artifact Classification"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Marks repetitive headers/footers or decorative elements as artifacts."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.structural_fix

    def remediate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[RemediationAction]:
        actions = []
        
        # Simple heuristic for repetitive text (headers/footers)
        text_counts = defaultdict(int)
        for page in canonical_doc.pages:
            # We only check blocks at top (y0 < 50) or bottom (y1 > page_height - 50)
            for block in page.blocks:
                if block.bbox.y0 < 50 or block.bbox.y1 > (page.height - 50):
                    text_counts[block.text.strip()] += 1
        
        # If a block of text appears on multiple pages at the top/bottom, mark as artifact
        repetitive_text = {text for text, count in text_counts.items() if count > 1 and count >= canonical_doc.page_count * 0.5}

        for page in canonical_doc.pages:
            for block in page.blocks:
                if block.role != CanonicalRole.artifact and block.text.strip() in repetitive_text:
                    if block.bbox.y0 < 50 or block.bbox.y1 > (page.height - 50):
                        original_role = block.role
                        block.role = CanonicalRole.artifact
                        actions.append(RemediationAction(
                            action_id=f"{page.page_number}-{block.block_id}-REMED-ARTI-001",
                            rule_id=self.skill_id,
                            page_number=page.page_number,
                            block_id=block.block_id,
                            source="deterministic-remediation",
                            description=f"Classified repetitive text '{block.text[:20]}...' as artifact.",
                            changed=True,
                            field_name="role",
                            before_value=original_role.value,
                            after_value=block.role.value
                        ))
                        
        return actions

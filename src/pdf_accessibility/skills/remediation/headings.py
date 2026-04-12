from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalRole
from pdf_accessibility.models.remediation import RemediationAction
from pdf_accessibility.skills.base import RemediationSkill, SkillCategory


class HeadingNormalizationSkill(RemediationSkill):
    @property
    def skill_id(self) -> str:
        return "REMED-HEAD-001"

    @property
    def name(self) -> str:
        return "Heading Normalization"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Ensures heading levels follow a logical hierarchy and don't skip levels."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.headings

    def remediate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[RemediationAction]:
        actions = []
        last_level = 0
        
        # Mapping from level to role
        level_to_role = {
            1: CanonicalRole.heading1,
            2: CanonicalRole.heading2,
            3: CanonicalRole.heading3,
            4: CanonicalRole.heading4,
            5: CanonicalRole.heading5,
            6: CanonicalRole.heading6,
        }
        
        # Mapping from role to level
        role_to_level = {v: k for k, v in level_to_role.items()}

        for page in canonical_doc.pages:
            for block in page.blocks:
                if block.role in role_to_level:
                    original_level = role_to_level[block.role]
                    
                    # Target level should be at most last_level + 1
                    target_level = min(original_level, last_level + 1)
                    
                    # Special case: first heading should be H1
                    if last_level == 0:
                        target_level = 1
                    
                    if target_level != original_level:
                        original_role = block.role
                        block.role = level_to_role[target_level]
                        actions.append(RemediationAction(
                            action_id=f"{page.page_number}-{block.block_id}-REMED-HEAD-001",
                            rule_id=self.skill_id,
                            page_number=page.page_number,
                            block_id=block.block_id,
                            source="deterministic-remediation",
                            description=f"Normalized heading level from H{original_level} to H{target_level}.",
                            changed=True,
                            field_name="role",
                            before_value=original_role.value,
                            after_value=block.role.value
                        ))
                    
                    last_level = target_level
                    
        return actions

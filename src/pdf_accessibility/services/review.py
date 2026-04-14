from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalRole
from pdf_accessibility.models.remediation import RemediationAction
from pdf_accessibility.models.review import ManualOverride, ReviewArtifact

if TYPE_CHECKING:
    from pdf_accessibility.core.settings import Settings
    from pdf_accessibility.services.file_store import BaseFileStore

logger = logging.getLogger(__name__)


class ReviewService:
    """
    Manages manual review overrides and applies them to the canonical document.
    """

    def __init__(self, store: BaseFileStore):
        self.store = store

    def get_review_artifact(self, document_id: str) -> ReviewArtifact:
        """Fetches existing review overrides or returns a fresh artifact."""
        artifact = self.store.get_review_artifact(document_id)
        if artifact is None:
            artifact = ReviewArtifact(document_id=document_id)
        return artifact

    def add_override(self, document_id: str, override: ManualOverride) -> ReviewArtifact:
        """Adds or updates a manual override for a block."""
        artifact = self.get_review_artifact(document_id)
        
        # Remove existing override for the same block if it exists
        artifact.overrides = [o for o in artifact.overrides if o.block_id != override.block_id]
        artifact.overrides.append(override)
        
        self.store.save_review_artifact(artifact)
        return artifact

    def apply_overrides(
        self, document: CanonicalDocument, artifact: ReviewArtifact
    ) -> list[RemediationAction]:
        """Applies manual overrides to the canonical document."""
        actions = []
        
        # Create a lookup for overrides
        override_map = {o.block_id: o for o in artifact.overrides}
        
        for page in document.pages:
            # Handle blocks
            for block in page.blocks:
                if block.block_id in override_map:
                    override = override_map[block.block_id]
                    self._apply_to_element(page.page_number, block, override, actions)
            
            # Handle forms
            for form in page.forms:
                if form.field_id in override_map:
                    override = override_map[form.field_id]
                    self._apply_to_element(page.page_number, form, override, actions)
                    
        return actions

    def _apply_to_element(
        self, 
        page_num: int, 
        element: CanonicalBlock | CanonicalForm, 
        override: ManualOverride, 
        actions: list[RemediationAction]
    ):
        """Helper to apply overrides to a single canonical element (block or form)."""
        element_id = getattr(element, 'block_id', getattr(element, 'field_id', 'unknown'))

        # 1. Role override
        if override.role is not None and override.role != element.role:
            old_role = element.role
            element.role = override.role
            actions.append(
                RemediationAction(
                    action_id=f"{page_num}-{element_id}-REV-ROLE",
                    rule_id="MANUAL-REVIEW",
                    page_number=page_num,
                    block_id=element_id,
                    source="human-review",
                    description=f"Manual override: role changed from {old_role} to {override.role}",
                    changed=True,
                    before_value=old_role.value,
                    after_value=override.role.value,
                )
            )

        # 2. Alt-text override (for blocks)
        if hasattr(element, 'alt_text') and override.alt_text is not None and override.alt_text != element.alt_text:
            old_alt = element.alt_text
            element.alt_text = override.alt_text
            actions.append(
                RemediationAction(
                    action_id=f"{page_num}-{element_id}-REV-ALT",
                    rule_id="MANUAL-REVIEW",
                    page_number=page_num,
                    block_id=element_id,
                    source="human-review",
                    description="Manual override: alt-text updated.",
                    changed=True,
                    before_value=old_alt,
                    after_value=override.alt_text,
                )
            )

        # 3. Tooltip override (for forms)
        if hasattr(element, 'tooltip') and override.tooltip is not None and override.tooltip != element.tooltip:
            old_tooltip = element.tooltip
            element.tooltip = override.tooltip
            actions.append(
                RemediationAction(
                    action_id=f"{page_num}-{element_id}-REV-TU",
                    rule_id="MANUAL-REVIEW",
                    page_number=page_num,
                    block_id=element_id,
                    source="human-review",
                    description="Manual override: form tooltip updated.",
                    changed=True,
                    before_value=old_tooltip,
                    after_value=element.tooltip,
                )
            )

        # 4. Artifact override
        if override.is_artifact is True and element.role != CanonicalRole.artifact:
            old_role = element.role
            element.role = CanonicalRole.artifact
            actions.append(
                RemediationAction(
                    action_id=f"{page_num}-{element_id}-REV-ARTI",
                    rule_id="MANUAL-REVIEW",
                    page_number=page_num,
                    block_id=element_id,
                    source="human-review",
                    description="Manual override: element marked as artifact.",
                    changed=True,
                    before_value=old_role.value,
                    after_value=CanonicalRole.artifact.value,
                )
            )

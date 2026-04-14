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
            for block in page.blocks:
                if block.block_id in override_map:
                    override = override_map[block.block_id]
                    
                    if override.role is not None and override.role != block.role:
                        old_role = block.role
                        block.role = override.role
                        actions.append(
                            RemediationAction(
                                action_id=f"{page.page_number}-{block.block_id}-REV-ROLE",
                                rule_id="MANUAL-REVIEW",
                                page_number=page.page_number,
                                block_id=block.block_id,
                                source="human-review",
                                description=f"Manual override: role changed from {old_role} to {override.role}",
                                changed=True,
                                before_value=old_role.value,
                                after_value=override.role.value,
                            )
                        )
                    
                    if override.alt_text is not None and override.alt_text != block.alt_text:
                        old_alt = block.alt_text
                        block.alt_text = override.alt_text
                        actions.append(
                            RemediationAction(
                                action_id=f"{page.page_number}-{block.block_id}-REV-ALT",
                                rule_id="MANUAL-REVIEW",
                                page_number=page.page_number,
                                block_id=block.block_id,
                                source="human-review",
                                description="Manual override: alt-text updated.",
                                changed=True,
                                before_value=old_alt,
                                after_value=override.alt_text,
                            )
                        )

        for page in document.pages:
            for form in page.forms:
                if form.field_id in override_map:
                    override = override_map[form.field_id]
                    if hasattr(override, 'tooltip') and override.tooltip is not None and override.tooltip != form.tooltip:
                        old_tooltip = form.tooltip
                        form.tooltip = override.tooltip
                        actions.append(
                            RemediationAction(
                                action_id=f"{page.page_number}-{form.field_id}-REV-TU",
                                rule_id="MANUAL-REVIEW",
                                page_number=page.page_number,
                                block_id=form.field_id,
                                source="human-review",
                                description="Manual override: form tooltip updated.",
                                changed=True,
                                before_value=old_tooltip,
                                after_value=form.tooltip,
                            )
                        )
                        
                    if override.is_artifact is not None:
                        # If marked as artifact, we change role to artifact
                        if override.is_artifact and block.role != CanonicalRole.artifact:
                            old_role = block.role
                            block.role = CanonicalRole.artifact
                            actions.append(
                                RemediationAction(
                                    action_id=f"{page.page_number}-{block.block_id}-REV-ARTI",
                                    rule_id="MANUAL-REVIEW",
                                    page_number=page.page_number,
                                    block_id=block.block_id,
                                    source="human-review",
                                    description="Manual override: block marked as artifact.",
                                    changed=True,
                                    before_value=old_role.value,
                                    after_value=CanonicalRole.artifact.value,
                                )
                            )
        return actions

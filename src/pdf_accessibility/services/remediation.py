from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.compliance import ComplianceProfile, get_profile_definition
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.remediation import RemediationAction, RemediationArtifact
from pdf_accessibility.skills.registry import get_registry
from pdf_accessibility.skills.remediation.text_normalization import TextNormalizationSkill
from pdf_accessibility.skills.remediation.ocr_confidence import OCRConfidenceSkill

# Initialize Registry (usually done in a bootstrap phase)
_registry = get_registry()
_registry.register_remediation(TextNormalizationSkill())
_registry.register_remediation(OCRConfidenceSkill())


def run_remediation_pipeline(
    document: CanonicalDocument,
    settings: Settings,
    profile: ComplianceProfile = ComplianceProfile.profile_b,
) -> tuple[CanonicalDocument, RemediationArtifact]:
    remediated = document.model_copy(deep=True)
    all_actions: list[RemediationAction] = []
    
    profile_def = get_profile_definition(profile)
    skill_ids = profile_def.remediation_skill_ids
    
    registry = get_registry()
    
    for skill_id in skill_ids:
        skill = registry.get_remediation(skill_id)
        if skill:
            actions = skill.run(remediated, settings)
            all_actions.extend(actions)

    # Recalculate totals
    for page in remediated.pages:
        page.block_count = len(page.blocks)
        page.text_char_count = sum(block.char_count for block in page.blocks)

    remediated.total_block_count = sum(page.block_count for page in remediated.pages)
    remediated.total_text_char_count = sum(page.text_char_count for page in remediated.pages)
    remediated.ocr_page_count = sum(1 for page in remediated.pages if page.used_ocr)

    changed_action_count = sum(1 for action in all_actions if action.changed)
    review_flagged_pages = sum(1 for page in remediated.pages if page.needs_review)
    
    remediation_artifact = RemediationArtifact(
        document_id=remediated.document_id,
        action_count=len(all_actions),
        changed_action_count=changed_action_count,
        review_flagged_page_count=review_flagged_pages,
        actions=all_actions,
    )
    return remediated, remediation_artifact


def run_deterministic_remediation(
    canonical_document: CanonicalDocument,
    settings: Settings,
) -> tuple[CanonicalDocument, RemediationArtifact]:
    """Legacy wrapper for run_remediation_pipeline."""
    return run_remediation_pipeline(canonical_document, settings)

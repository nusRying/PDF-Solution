from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.core.settings import get_settings
from pdf_accessibility.models.compliance import ComplianceProfile, get_profile_definition
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.remediation import RemediationAction, RemediationArtifact
from pdf_accessibility.skills.registry import get_registry
from pdf_accessibility.skills.remediation.text_normalization import TextNormalizationSkill
from pdf_accessibility.skills.remediation.ocr_confidence import OCRConfidenceSkill
from pdf_accessibility.skills.remediation.headings import HeadingNormalizationSkill
from pdf_accessibility.skills.remediation.lists import ListRepairSkill
from pdf_accessibility.skills.remediation.metadata import MetadataRepairSkill
from pdf_accessibility.skills.remediation.artifacts import ArtifactClassificationSkill
from pdf_accessibility.skills.remediation.ai_assist import AIAltTextSkill, RoleDisambiguationSkill
from pdf_accessibility.skills.remediation.tables import TableRepairSkill
from pdf_accessibility.skills.remediation.forms import FormRepairSkill
from pdf_accessibility.skills.remediation.tables import TableRepairSkill
from pdf_accessibility.skills.remediation.forms import FormRepairSkill, FormTabOrderSkill
from pdf_accessibility.services.ai_assist import AIAssistService
from pdf_accessibility.services.file_store import get_file_store
from pdf_accessibility.services.review import ReviewService

# Initialize Registry
_registry = get_registry()
_settings = get_settings()
_ai_assist_service = AIAssistService(_settings)

_registry.register_remediation(TextNormalizationSkill())
_registry.register_remediation(OCRConfidenceSkill())
_registry.register_remediation(HeadingNormalizationSkill())
_registry.register_remediation(ListRepairSkill())
_registry.register_remediation(MetadataRepairSkill())
_registry.register_remediation(ArtifactClassificationSkill())
_registry.register_remediation(TableRepairSkill())
_registry.register_remediation(FormRepairSkill())
_registry.register_remediation(FormTabOrderSkill())
_registry.register_remediation(AIAltTextSkill(_ai_assist_service))
_registry.register_remediation(RoleDisambiguationSkill(_ai_assist_service))


def run_remediation_pipeline(
    document: CanonicalDocument,
    settings: Settings,
    profile: ComplianceProfile = ComplianceProfile.profile_b,
) -> tuple[CanonicalDocument, RemediationArtifact]:
    remediated = document.model_copy(deep=True)
    all_actions: list[RemediationAction] = []
    
    # 1. Apply Dynamic Skills from Registry
    profile_def = get_profile_definition(profile)
    skill_ids = profile_def.remediation_skill_ids
    
    registry = get_registry()
    
    for skill_id in skill_ids:
        skill = registry.get_remediation(skill_id)
        if skill:
            actions = skill.remediate(remediated, settings)
            all_actions.extend(actions)

    # 2. Apply Manual Overrides (Human-in-the-loop)
    store = get_file_store(settings)
    review_service = ReviewService(store)
    review_artifact = store.get_review_artifact(remediated.document_id)
    if review_artifact:
        manual_actions = review_service.apply_overrides(remediated, review_artifact)
        all_actions.extend(manual_actions)

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

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import fitz
from pdf_accessibility.models.canonical import CanonicalRole
from pdf_accessibility.models.remediation import RemediationAction
from pdf_accessibility.services.file_store import get_file_store
from pdf_accessibility.skills.base import RemediationSkill, SkillCategory

if TYPE_CHECKING:
    from pdf_accessibility.core.settings import Settings
    from pdf_accessibility.models.canonical import CanonicalDocument
    from pdf_accessibility.services.ai_assist import AIAssistService

logger = logging.getLogger(__name__)


class AIAltTextSkill(RemediationSkill):
    """
    ID: REMED-AI-001
    Skill to generate alt-text for figures using AI.
    """

    def __init__(self, ai_assist_service: AIAssistService):
        self.ai_assist_service = ai_assist_service

    @property
    def skill_id(self) -> str:
        return "REMED-AI-001"

    @property
    def name(self) -> str:
        return "AI Alt-Text Generation"

    @property
    def version(self) -> str:
        return "1.1.0"

    @property
    def description(self) -> str:
        return "Uses AI to generate descriptive alt-text for figure blocks using visual analysis."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.figures

    def remediate(
        self, canonical_doc: CanonicalDocument, settings: Settings
    ) -> list[RemediationAction]:
        actions = []
        
        # We need the original PDF to extract image crops for vision analysis
        store = get_file_store(settings)
        pdf_path = settings.originals_dir / f"{canonical_doc.document_id}.pdf"
        
        doc_handle = None
        if pdf_path.exists():
            try:
                doc_handle = fitz.open(pdf_path)
            except Exception as e:
                logger.warning(f"Could not open PDF for vision extraction: {e}")

        for page in canonical_doc.pages:
            pdf_page = None
            if doc_handle and page.page_number <= len(doc_handle):
                pdf_page = doc_handle[page.page_number - 1]

            for block in page.blocks:
                if block.role == CanonicalRole.figure and not block.alt_text:
                    image_bytes = None
                    if pdf_page:
                        # Extract crop of the figure
                        # bbox is (x0, y0, x1, y1)
                        rect = fitz.Rect(block.bbox.x0, block.bbox.y0, block.bbox.x1, block.bbox.y1)
                        if not rect.is_empty:
                            pix = pdf_page.get_pixmap(clip=rect, matrix=fitz.Matrix(2, 2)) # 2x zoom for clarity
                            image_bytes = pix.tobytes("jpeg")

                    # Provide context from surrounding blocks
                    context = ""
                    # Grab a few nearby blocks for context
                    idx = page.blocks.index(block)
                    nearby = page.blocks[max(0, idx-2):min(len(page.blocks), idx+3)]
                    context = " | ".join([b.text[:100] for b in nearby if b.text.strip()])

                    alt_text, confidence = self.ai_assist_service.generate_alt_text(
                        block, image_bytes=image_bytes, context=context
                    )
                    
                    block.alt_text = alt_text
                    block.confidence = confidence

                    if confidence < 0.7:
                        page.needs_review = True

                    actions.append(
                        RemediationAction(
                            action_id=f"{page.page_number}-{block.block_id}-AI-ALT-001",
                            rule_id=self.skill_id,
                            page_number=page.page_number,
                            block_id=block.block_id,
                            source="ai-assist",
                            description=f"AI generated alt-text for block {block.block_id} (confidence: {confidence:.2f})",
                            changed=True,
                            after_value=alt_text,
                            confidence=confidence,
                        )
                    )
        
        if doc_handle:
            doc_handle.close()
            
        return actions


class RoleDisambiguationSkill(RemediationSkill):
    """
    ID: REMED-AI-002
    Skill to disambiguate roles for ambiguous blocks using AI logic.
    """

    def __init__(self, ai_assist_service: AIAssistService):
        self.ai_assist_service = ai_assist_service

    @property
    def skill_id(self) -> str:
        return "REMED-AI-002"

    @property
    def name(self) -> str:
        return "AI Role Disambiguation"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Suggests correct roles for blocks with ambiguous formatting using LLM reasoning."

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.tagging

    def remediate(
        self, canonical_doc: CanonicalDocument, settings: Settings
    ) -> list[RemediationAction]:
        actions = []
        for page in canonical_doc.pages:
            for block in page.blocks:
                if block.role == CanonicalRole.text:
                    suggested_role, confidence = self.ai_assist_service.disambiguate_role(
                        block
                    )
                    if suggested_role != block.role:
                        old_role = block.role
                        block.role = suggested_role
                        block.confidence = confidence

                        if confidence < 0.8:
                            page.needs_review = True

                        actions.append(
                            RemediationAction(
                                action_id=f"{page.page_number}-{block.block_id}-AI-ROLE-001",
                                rule_id=self.skill_id,
                                page_number=page.page_number,
                                block_id=block.block_id,
                                source="ai-assist",
                                description=f"AI changed role from {old_role} to {suggested_role} (confidence: {confidence:.2f})",
                                changed=True,
                                before_value=old_role.value,
                                after_value=suggested_role.value,
                                confidence=confidence,
                            )
                        )
        return actions

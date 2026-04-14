import pytest
from pdf_accessibility.services.ai_assist import AIAssistService
from pdf_accessibility.skills.remediation.ai_assist import AIAltTextSkill, RoleDisambiguationSkill
from pdf_accessibility.core.settings import get_settings
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalPage, CanonicalBlock, CanonicalRole, CanonicalMetadata, ContentSource
from pdf_accessibility.models.documents import BoundingBox, DocumentSourceType

@pytest.fixture
def ai_service():
    return AIAssistService(get_settings())

@pytest.fixture
def sample_doc():
    return CanonicalDocument(
        document_id="doc1",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=2,
        total_text_char_count=50,
        ocr_page_count=0,
        metadata=CanonicalMetadata(),
        pages=[
            CanonicalPage(
                page_number=1,
                width=612,
                height=792,
                rotation=0,
                block_count=2,
                text_char_count=50,
                has_native_text=True,
                used_ocr=False,
                needs_review=False,
                blocks=[
                    CanonicalBlock(
                        block_id="b1",
                        page_number=1,
                        source=ContentSource.native,
                        bbox=BoundingBox(x0=0, y0=0, x1=100, y1=100),
                        text="This is an image",
                        char_count=16,
                        role=CanonicalRole.figure,
                        alt_text=None
                    ),
                    CanonicalBlock(
                        block_id="b2",
                        page_number=1,
                        source=ContentSource.native,
                        bbox=BoundingBox(x0=0, y0=110, x1=100, y1=150),
                        text="\u2022 This is a bullet",
                        char_count=18,
                        role=CanonicalRole.text
                    )
                ]
            )
        ]
    )

def test_ai_alt_text_skill(ai_service, sample_doc):
    skill = AIAltTextSkill(ai_service)
    actions = skill.remediate(sample_doc, get_settings())
    
    assert len(actions) == 1
    assert sample_doc.pages[0].blocks[0].alt_text is not None
    assert "image" in sample_doc.pages[0].blocks[0].alt_text.lower()

def test_role_disambiguation_skill(ai_service, sample_doc):
    skill = RoleDisambiguationSkill(ai_service)
    actions = skill.remediate(sample_doc, get_settings())
    
    assert len(actions) == 1
    assert sample_doc.pages[0].blocks[1].role == CanonicalRole.list_item

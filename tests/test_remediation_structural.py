import pytest
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalPage, CanonicalBlock, CanonicalRole, ContentSource
from pdf_accessibility.models.documents import BoundingBox, DocumentSourceType
from pdf_accessibility.skills.remediation.headings import HeadingNormalizationSkill
from pdf_accessibility.skills.remediation.lists import ListRepairSkill
from pdf_accessibility.core.settings import Settings

def create_mock_doc(roles: list[CanonicalRole], texts: list[str] = None, x0s: list[float] = None) -> CanonicalDocument:
    blocks = []
    for i, role in enumerate(roles):
        text = texts[i] if texts else f"Block {i}"
        x0 = x0s[i] if x0s else 0
        blocks.append(CanonicalBlock(
            block_id=f"b{i}",
            page_number=1,
            source=ContentSource.native,
            bbox=BoundingBox(x0=x0, y0=i*10, x1=x0+100, y1=i*10+10),
            text=text,
            char_count=len(text),
            role=role
        ))
    
    page = CanonicalPage(
        page_number=1,
        width=612,
        height=792,
        rotation=0,
        block_count=len(blocks),
        text_char_count=sum(len(b.text) for b in blocks),
        has_native_text=True,
        used_ocr=False,
        needs_review=False,
        blocks=blocks
    )
    
    return CanonicalDocument(
        document_id="test_doc",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=len(blocks),
        total_text_char_count=sum(len(b.text) for b in blocks),
        ocr_page_count=0,
        pages=[page]
    )

def test_heading_normalization():
    skill = HeadingNormalizationSkill()
    settings = Settings()
    
    # Case 1: Starts with H3 -> Should become H1
    doc = create_mock_doc([CanonicalRole.heading3, CanonicalRole.text])
    actions = skill.remediate(doc, settings)
    assert doc.pages[0].blocks[0].role == CanonicalRole.heading1
    assert len(actions) == 1
    assert actions[0].after_value == "heading1"

    # Case 2: H1 followed by H3 -> Should become H1, H2
    doc = create_mock_doc([CanonicalRole.heading1, CanonicalRole.heading3])
    actions = skill.remediate(doc, settings)
    assert doc.pages[0].blocks[1].role == CanonicalRole.heading2
    assert len(actions) == 1
    assert actions[0].after_value == "heading2"

    # Case 3: H1, H2, H4 -> H1, H2, H3
    doc = create_mock_doc([CanonicalRole.heading1, CanonicalRole.heading2, CanonicalRole.heading4])
    actions = skill.remediate(doc, settings)
    assert doc.pages[0].blocks[2].role == CanonicalRole.heading3
    
    # Case 4: H2 followed by H1 -> Remains H1
    doc = create_mock_doc([CanonicalRole.heading1, CanonicalRole.heading2, CanonicalRole.heading1])
    actions = skill.remediate(doc, settings)
    assert doc.pages[0].blocks[2].role == CanonicalRole.heading1
    assert len(actions) == 0 # No changes needed for the third block

def test_list_repair():
    skill = ListRepairSkill()
    settings = Settings()
    
    # Case 1: Bullet points with same indentation
    doc = create_mock_doc(
        roles=[CanonicalRole.text, CanonicalRole.text, CanonicalRole.text],
        texts=["• Item 1", "• Item 2", "Regular text"],
        x0s=[50, 50, 0]
    )
    actions = skill.remediate(doc, settings)
    assert doc.pages[0].blocks[0].role == CanonicalRole.list_item
    assert doc.pages[0].blocks[1].role == CanonicalRole.list_item
    assert doc.pages[0].blocks[2].role == CanonicalRole.text
    assert len(actions) == 2

    # Case 2: Numbered list
    doc = create_mock_doc(
        roles=[CanonicalRole.text, CanonicalRole.text],
        texts=["1. First", "2. Second"],
        x0s=[50, 50]
    )
    actions = skill.remediate(doc, settings)
    assert doc.pages[0].blocks[0].role == CanonicalRole.list_item
    assert doc.pages[0].blocks[1].role == CanonicalRole.list_item

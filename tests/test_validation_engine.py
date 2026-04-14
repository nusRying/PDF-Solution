from __future__ import annotations

import pytest
from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import (
    CanonicalBlock,
    CanonicalDocument,
    CanonicalMetadata,
    CanonicalPage,
    CanonicalRole,
    ContentSource,
)
from pdf_accessibility.models.documents import BoundingBox, DocumentSourceType
from pdf_accessibility.skills.validation.headings import HeadingHierarchyValidationSkill
from pdf_accessibility.skills.validation.metadata import DocumentTitleValidationSkill
from pdf_accessibility.skills.validation.figures import FigureAltTextValidationSkill


@pytest.fixture
def settings():
    return Settings()


def test_heading_hierarchy_validation(settings):
    skill = HeadingHierarchyValidationSkill()
    
    # Create doc with H1 -> H3 skip
    block1 = CanonicalBlock(
        block_id="b1", page_number=1, source=ContentSource.native,
        bbox=BoundingBox(x0=0, y0=0, x1=100, y1=20), text="H1", char_count=2, role=CanonicalRole.heading1
    )
    block2 = CanonicalBlock(
        block_id="b2", page_number=1, source=ContentSource.native,
        bbox=BoundingBox(x0=0, y0=30, x1=100, y1=50), text="H3", char_count=2, role=CanonicalRole.heading3
    )
    
    doc = CanonicalDocument(
        document_id="doc1", source_type=DocumentSourceType.digital, page_count=1,
        total_block_count=2, total_text_char_count=4, ocr_page_count=0,
        pages=[CanonicalPage(
            page_number=1, width=600, height=800, rotation=0, block_count=2,
            text_char_count=4, has_native_text=True, used_ocr=False, needs_review=False,
            blocks=[block1, block2]
        )]
    )
    
    findings = skill.validate(doc, settings)
    assert len(findings) == 1
    assert "jump from H1 to H3" in findings[0].message
    assert findings[0].rule_id == "VALID-HEAD-001"


def test_document_title_validation(settings):
    skill = DocumentTitleValidationSkill()
    
    doc = CanonicalDocument(
        document_id="doc1", source_type=DocumentSourceType.digital, page_count=1,
        total_block_count=0, total_text_char_count=0, ocr_page_count=0,
        metadata=CanonicalMetadata(title=""), # Empty title
        pages=[]
    )
    
    findings = skill.validate(doc, settings)
    assert len(findings) == 1
    assert "Document title is missing" in findings[0].message


def test_figure_alt_text_validation(settings):
    skill = FigureAltTextValidationSkill()
    
    fig_block = CanonicalBlock(
        block_id="f1", page_number=1, source=ContentSource.native,
        bbox=BoundingBox(x0=0, y0=0, x1=100, y1=100), text="", char_count=0, 
        role=CanonicalRole.figure, alt_text=None # Missing alt text
    )
    
    doc = CanonicalDocument(
        document_id="doc1", source_type=DocumentSourceType.digital, page_count=1,
        total_block_count=1, total_text_char_count=0, ocr_page_count=0,
        pages=[CanonicalPage(
            page_number=1, width=600, height=800, rotation=0, block_count=1,
            text_char_count=0, has_native_text=True, used_ocr=False, needs_review=False,
            blocks=[fig_block]
        )]
    )
    
    findings = skill.validate(doc, settings)
    assert len(findings) == 1
    assert "Figure missing alternative text" in findings[0].message

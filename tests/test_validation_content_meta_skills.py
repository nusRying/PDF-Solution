import pytest
from pdf_accessibility.models.canonical import (
    CanonicalDocument,
    CanonicalPage,
    CanonicalBlock,
    CanonicalRole,
    ContentSource,
    BoundingBox,
    DocumentSourceType,
    CanonicalMetadata,
)
from pdf_accessibility.models.validation import ValidationSeverity
from pdf_accessibility.skills.validation.content import FigureAltSkill
from pdf_accessibility.skills.validation.metadata import (
    DocumentLanguageValidationSkill,
    DocumentTitleValidationSkill,
)
from pdf_accessibility.core.settings import Settings

@pytest.fixture
def settings():
    return Settings()

def test_figure_alt_skill(settings):
    skill = FigureAltSkill()

    # Valid: Figure with alt text
    doc_valid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=1,
        total_text_char_count=0,
        ocr_page_count=0,
        pages=[
            CanonicalPage(
                page_number=1, width=100, height=100, rotation=0,
                block_count=1, text_char_count=0, has_native_text=True, used_ocr=False, needs_review=False,
                blocks=[
                    CanonicalBlock(
                        block_id="f1", page_number=1, source=ContentSource.native,
                        bbox=BoundingBox(x0=0, y0=0, x1=10, y1=10),
                        text="", char_count=0, role=CanonicalRole.figure, alt_text="A nice figure"
                    )
                ]
            )
        ]
    )
    findings = skill.validate(doc_valid, settings)
    assert len(findings) == 0

    # Invalid: Figure missing alt text
    doc_missing = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=1,
        total_text_char_count=0,
        ocr_page_count=0,
        pages=[
            CanonicalPage(
                page_number=1, width=100, height=100, rotation=0,
                block_count=1, text_char_count=0, has_native_text=True, used_ocr=False, needs_review=False,
                blocks=[
                    CanonicalBlock(
                        block_id="f1", page_number=1, source=ContentSource.native,
                        bbox=BoundingBox(x0=0, y0=0, x1=10, y1=10),
                        text="", char_count=0, role=CanonicalRole.figure, alt_text=None
                    )
                ]
            )
        ]
    )
    findings = skill.validate(doc_missing, settings)
    assert len(findings) == 1
    assert findings[0].rule_id == "VALID-MH-14-001"

    # Invalid: Figure with empty alt text
    doc_empty = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=1,
        total_text_char_count=0,
        ocr_page_count=0,
        pages=[
            CanonicalPage(
                page_number=1, width=100, height=100, rotation=0,
                block_count=1, text_char_count=0, has_native_text=True, used_ocr=False, needs_review=False,
                blocks=[
                    CanonicalBlock(
                        block_id="f1", page_number=1, source=ContentSource.native,
                        bbox=BoundingBox(x0=0, y0=0, x1=10, y1=10),
                        text="", char_count=0, role=CanonicalRole.figure, alt_text="  "
                    )
                ]
            )
        ]
    )
    findings = skill.validate(doc_empty, settings)
    assert len(findings) == 1
    assert findings[0].rule_id == "VALID-MH-14-003"

def test_document_language_validation_skill(settings):
    skill = DocumentLanguageValidationSkill()

    # Valid: Language set
    doc_valid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        metadata=CanonicalMetadata(language="en-US"),
        pages=[]
    )
    findings = skill.validate(doc_valid, settings)
    assert len(findings) == 0

    # Invalid: Language missing
    doc_invalid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        metadata=CanonicalMetadata(language=None),
        pages=[]
    )
    findings = skill.validate(doc_invalid, settings)
    assert len(findings) == 1
    assert findings[0].rule_id == "VALID-META-002"

def test_document_title_validation_skill(settings):
    skill = DocumentTitleValidationSkill()

    # Valid: Title set
    doc_valid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        metadata=CanonicalMetadata(title="My PDF"),
        pages=[]
    )
    findings = skill.validate(doc_valid, settings)
    assert len(findings) == 0

    # Invalid: Title missing
    doc_invalid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        metadata=CanonicalMetadata(title=None),
        pages=[]
    )
    findings = skill.validate(doc_invalid, settings)
    assert len(findings) == 1
    assert findings[0].rule_id == "VALID-META-001"

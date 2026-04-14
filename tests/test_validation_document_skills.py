import pytest
from pdf_accessibility.models.canonical import (
    CanonicalDocument,
    DocumentSourceType,
    CanonicalMetadata,
)
from pdf_accessibility.models.validation import ValidationSeverity
from pdf_accessibility.skills.validation.document import (
    MarkInfoSkill,
    StructTreeSkill,
    PDFUAIdentifierSkill,
)
from pdf_accessibility.core.settings import Settings

@pytest.fixture
def settings():
    return Settings()

def test_mark_info_skill(settings):
    skill = MarkInfoSkill()

    # Valid: is_tagged is True
    doc_valid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        metadata=CanonicalMetadata(is_tagged=True),
        pages=[]
    )
    findings = skill.validate(doc_valid, settings)
    assert len(findings) == 0

    # Invalid: is_tagged is False
    doc_invalid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        metadata=CanonicalMetadata(is_tagged=False),
        pages=[]
    )
    findings = skill.validate(doc_invalid, settings)
    assert len(findings) == 1
    assert findings[0].rule_id == "VALID-MH-01-001"

def test_struct_tree_skill(settings):
    skill = StructTreeSkill()

    # Valid: has_struct_tree is True
    doc_valid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        metadata=CanonicalMetadata(has_struct_tree=True),
        pages=[]
    )
    findings = skill.validate(doc_valid, settings)
    assert len(findings) == 0

    # Invalid: has_struct_tree is False
    doc_invalid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        metadata=CanonicalMetadata(has_struct_tree=False),
        pages=[]
    )
    findings = skill.validate(doc_invalid, settings)
    assert len(findings) == 1
    assert findings[0].rule_id == "VALID-MH-01-004"

def test_pdf_ua_identifier_skill(settings):
    skill = PDFUAIdentifierSkill()

    # Valid: is_pdf_ua_identifier_present is True
    doc_valid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        metadata=CanonicalMetadata(is_pdf_ua_identifier_present=True),
        pages=[]
    )
    findings = skill.validate(doc_valid, settings)
    assert len(findings) == 0

    # Invalid: is_pdf_ua_identifier_present is False
    doc_invalid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        metadata=CanonicalMetadata(is_pdf_ua_identifier_present=False),
        pages=[]
    )
    findings = skill.validate(doc_invalid, settings)
    assert len(findings) == 1
    assert findings[0].rule_id == "VALID-MH-04-001"

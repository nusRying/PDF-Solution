import pytest
from pdf_accessibility.models.validation import ValidationFinding, ValidationSeverity
from pdf_accessibility.models.canonical import CanonicalBlock, ContentSource, CanonicalRole, CanonicalMetadata
from pdf_accessibility.models.documents import BoundingBox, ParserDocumentMetadata

def test_validation_finding_with_block_id_and_bbox():
    bbox = BoundingBox(x0=0, y0=0, x1=100, y1=100)
    finding = ValidationFinding(
        rule_id="RULE-001",
        severity=ValidationSeverity.error,
        message="Test message",
        page_number=1,
        source="validator",
        block_id="block-1",
        bbox=bbox
    )
    assert finding.block_id == "block-1"
    assert finding.bbox == bbox
    
    # Verify optionality
    finding_minimal = ValidationFinding(
        rule_id="RULE-001",
        severity=ValidationSeverity.error,
        message="Test message",
        source="validator"
    )
    assert finding_minimal.block_id is None
    assert finding_minimal.bbox is None

def test_canonical_block_with_alt_text():
    bbox = BoundingBox(x0=0, y0=0, x1=100, y1=100)
    block = CanonicalBlock(
        block_id="block-1",
        page_number=1,
        source=ContentSource.native,
        bbox=bbox,
        text="Sample text",
        char_count=11,
        alt_text="Alternative text"
    )
    assert block.alt_text == "Alternative text"
    
    # Verify optionality
    block_no_alt = CanonicalBlock(
        block_id="block-1",
        page_number=1,
        source=ContentSource.native,
        bbox=bbox,
        text="Sample text",
        char_count=11
    )
    assert block_no_alt.alt_text is None

def test_canonical_metadata_accessibility_flags():
    meta = CanonicalMetadata(
        is_tagged=True,
        has_struct_tree=True,
        is_pdf_ua_identifier_present=True
    )
    assert meta.is_tagged is True
    assert meta.has_struct_tree is True
    assert meta.is_pdf_ua_identifier_present is True
    
    # Default values should be False or None? 
    # The plan says "boolean fields", usually default to False for flags like these.
    meta_default = CanonicalMetadata()
    assert meta_default.is_tagged is False
    assert meta_default.has_struct_tree is False
    assert meta_default.is_pdf_ua_identifier_present is False

def test_parser_document_metadata_accessibility_flags():
    meta = ParserDocumentMetadata(
        is_tagged=True,
        has_struct_tree=True,
        is_pdf_ua_identifier_present=True
    )
    assert meta.is_tagged is True
    assert meta.has_struct_tree is True
    assert meta.is_pdf_ua_identifier_present is True
    
    meta_default = ParserDocumentMetadata()
    assert meta_default.is_tagged is False
    assert meta_default.has_struct_tree is False
    assert meta_default.is_pdf_ua_identifier_present is False

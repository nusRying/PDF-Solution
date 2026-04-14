import pytest
from pathlib import Path
from pdf_accessibility.services.pdf_parser import parse_pdf

def test_parse_pdf_extracts_accessibility_metadata():
    # Use one of the existing PDFs
    pdf_path = Path("data/originals/74b32d0bd7d04029b4644cd7a5cc5051.pdf")
    if not pdf_path.exists():
        pytest.skip("Test PDF not found")
        
    artifact = parse_pdf("test-doc", pdf_path)
    
    # Check if the new fields exist in the metadata
    assert hasattr(artifact.metadata, "is_tagged")
    assert hasattr(artifact.metadata, "has_struct_tree")
    assert hasattr(artifact.metadata, "is_pdf_ua_identifier_present")
    
    # They should be boolean
    assert isinstance(artifact.metadata.is_tagged, bool)
    assert isinstance(artifact.metadata.has_struct_tree, bool)
    assert isinstance(artifact.metadata.is_pdf_ua_identifier_present, bool)

def test_canonicalize_populates_accessibility_flags():
    from pdf_accessibility.services.canonicalize import build_canonical_document
    from pdf_accessibility.models.documents import ParserArtifact, ParserDocumentMetadata
    
    # Mock ParserArtifact
    parser_meta = ParserDocumentMetadata(
        is_tagged=True,
        has_struct_tree=True,
        is_pdf_ua_identifier_present=True
    )
    artifact = ParserArtifact(
        document_id="test-doc",
        source_path="test.pdf",
        file_size_bytes=100,
        page_count=1,
        text_page_count=1,
        image_page_count=0,
        source_type="digital",
        metadata=parser_meta,
        pages=[]
    )
    
    canonical_doc = build_canonical_document(artifact, ocr_artifact=None)
    assert canonical_doc.metadata.is_tagged is True
    assert canonical_doc.metadata.has_struct_tree is True
    assert canonical_doc.metadata.is_pdf_ua_identifier_present is True

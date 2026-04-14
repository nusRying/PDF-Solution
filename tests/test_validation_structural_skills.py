import pytest
from pdf_accessibility.models.canonical import (
    CanonicalDocument,
    CanonicalPage,
    CanonicalBlock,
    CanonicalRole,
    ContentSource,
    BoundingBox,
    DocumentSourceType,
    CanonicalTable,
    CanonicalRow,
    CanonicalCell,
)
from pdf_accessibility.models.validation import ValidationSeverity
from pdf_accessibility.skills.validation.structural import (
    HeadingHierarchySkill,
    FirstHeadingSkill,
    TableTHSkill,
)
from pdf_accessibility.core.settings import Settings

@pytest.fixture
def settings():
    return Settings()

def create_block(block_id, page_number, role, text=""):
    return CanonicalBlock(
        block_id=block_id,
        page_number=page_number,
        source=ContentSource.native,
        bbox=BoundingBox(x0=0, y0=0, x1=10, y1=10),
        text=text,
        char_count=len(text),
        role=role,
    )

def test_heading_hierarchy_skill(settings):
    skill = HeadingHierarchySkill()
    
    # Valid hierarchy
    doc_valid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=2,
        total_text_char_count=0,
        ocr_page_count=0,
        pages=[
            CanonicalPage(
                page_number=1, width=100, height=100, rotation=0,
                block_count=2, text_char_count=0, has_native_text=True, used_ocr=False, needs_review=False,
                blocks=[
                    create_block("b1", 1, CanonicalRole.heading1),
                    create_block("b2", 1, CanonicalRole.heading2),
                ]
            )
        ]
    )
    findings = skill.validate(doc_valid, settings)
    assert len(findings) == 0

    # Invalid hierarchy (skipped H2)
    doc_invalid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=2,
        total_text_char_count=0,
        ocr_page_count=0,
        pages=[
            CanonicalPage(
                page_number=1, width=100, height=100, rotation=0,
                block_count=2, text_char_count=0, has_native_text=True, used_ocr=False, needs_review=False,
                blocks=[
                    create_block("b1", 1, CanonicalRole.heading1),
                    create_block("b2", 1, CanonicalRole.heading3),
                ]
            )
        ]
    )
    findings = skill.validate(doc_invalid, settings)
    assert len(findings) == 1
    assert findings[0].rule_id == "VALID-MH-13-004"
    assert findings[0].severity == ValidationSeverity.error
    assert findings[0].block_id == "b2"

def test_first_heading_skill(settings):
    skill = FirstHeadingSkill()

    # Valid: First heading is H1
    doc_valid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=2,
        total_text_char_count=0,
        ocr_page_count=0,
        pages=[
            CanonicalPage(
                page_number=1, width=100, height=100, rotation=0,
                block_count=2, text_char_count=0, has_native_text=True, used_ocr=False, needs_review=False,
                blocks=[
                    create_block("b1", 1, CanonicalRole.text),
                    create_block("b2", 1, CanonicalRole.heading1),
                ]
            )
        ]
    )
    findings = skill.validate(doc_valid, settings)
    assert len(findings) == 0

    # Invalid: First heading is H2
    doc_invalid = CanonicalDocument(
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
                    create_block("b1", 1, CanonicalRole.heading2),
                ]
            )
        ]
    )
    findings = skill.validate(doc_invalid, settings)
    assert len(findings) == 1
    assert findings[0].rule_id == "VALID-MH-13-001"
    assert findings[0].block_id == "b1"

def test_table_th_skill(settings):
    skill = TableTHSkill()

    # Valid: Table with TH
    doc_valid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        pages=[
            CanonicalPage(
                page_number=1, width=100, height=100, rotation=0,
                block_count=0, text_char_count=0, has_native_text=True, used_ocr=False, needs_review=False,
                tables=[
                    CanonicalTable(
                        table_id="t1",
                        bbox=BoundingBox(x0=0, y0=0, x1=10, y1=10),
                        rows=[
                            CanonicalRow(cells=[
                                CanonicalCell(bbox=BoundingBox(x0=0, y0=0, x1=5, y1=5), role=CanonicalRole.table_header),
                                CanonicalCell(bbox=BoundingBox(x0=5, y0=0, x1=10, y1=5), role=CanonicalRole.table_data),
                            ])
                        ]
                    )
                ]
            )
        ]
    )
    findings = skill.validate(doc_valid, settings)
    assert len(findings) == 0

    # Invalid: Table without TH
    doc_invalid = CanonicalDocument(
        document_id="test",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        pages=[
            CanonicalPage(
                page_number=1, width=100, height=100, rotation=0,
                block_count=0, text_char_count=0, has_native_text=True, used_ocr=False, needs_review=False,
                tables=[
                    CanonicalTable(
                        table_id="t1",
                        bbox=BoundingBox(x0=0, y0=0, x1=10, y1=10),
                        rows=[
                            CanonicalRow(cells=[
                                CanonicalCell(bbox=BoundingBox(x0=0, y0=0, x1=5, y1=5), role=CanonicalRole.table_data),
                                CanonicalCell(bbox=BoundingBox(x0=5, y0=0, x1=10, y1=5), role=CanonicalRole.table_data),
                            ])
                        ]
                    )
                ]
            )
        ]
    )
    findings = skill.validate(doc_invalid, settings)
    assert len(findings) == 1
    assert findings[0].rule_id == "VALID-MH-15-001"
    assert findings[0].block_id == "t1"

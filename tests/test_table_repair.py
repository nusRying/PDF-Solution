import pytest
from pdf_accessibility.models.canonical import (
    CanonicalDocument,
    CanonicalPage,
    CanonicalBlock,
    CanonicalTable,
    CanonicalRow,
    CanonicalCell,
    CanonicalRole,
    BoundingBox,
    ContentSource,
    DocumentSourceType
)
from pdf_accessibility.core.settings import Settings
from pdf_accessibility.skills.remediation.tables import TableRepairSkill

def test_table_repair_skill_basic():
    # Setup: Canonical document with a table that has blocks but incorrect roles
    block1 = CanonicalBlock(
        block_id="b1",
        page_number=1,
        source=ContentSource.native,
        bbox=BoundingBox(x0=10, y0=10, x1=50, y1=20),
        text="Header 1",
        char_count=8,
        role=CanonicalRole.text
    )
    block2 = CanonicalBlock(
        block_id="b2",
        page_number=1,
        source=ContentSource.native,
        bbox=BoundingBox(x0=10, y0=30, x1=50, y1=40),
        text="Data 1",
        char_count=6,
        role=CanonicalRole.text
    )
    
    cell1 = CanonicalCell(
        bbox=block1.bbox,
        role=CanonicalRole.table_data, # Incorrect role
        block_ids=["b1"]
    )
    cell2 = CanonicalCell(
        bbox=block2.bbox,
        role=CanonicalRole.table_data,
        block_ids=["b2"]
    )
    
    row1 = CanonicalRow(cells=[cell1])
    row2 = CanonicalRow(cells=[cell2])
    
    table = CanonicalTable(
        table_id="t1",
        bbox=BoundingBox(x0=10, y0=10, x1=50, y1=40),
        rows=[row1, row2]
    )
    
    page = CanonicalPage(
        page_number=1,
        width=612,
        height=792,
        rotation=0,
        block_count=2,
        text_char_count=14,
        has_native_text=True,
        used_ocr=False,
        needs_review=False,
        blocks=[block1, block2],
        tables=[table]
    )
    
    doc = CanonicalDocument(
        document_id="doc1",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=2,
        total_text_char_count=14,
        ocr_page_count=0,
        pages=[page]
    )
    
    skill = TableRepairSkill()
    settings = Settings()
    actions = skill.remediate(doc, settings)
    
    # Assertions
    assert len(actions) > 0
    assert block1.role == CanonicalRole.table_header
    assert block2.role == CanonicalRole.table_data
    assert cell1.role == CanonicalRole.table_header
    assert any(a.block_id == "b1" and a.after_value == "table_header" for a in actions)

def test_table_repair_skill_no_tables_uses_detection(mocker):
    # Setup: Page with blocks aligned like a table but no CanonicalTable yet
    block1 = CanonicalBlock(
        block_id="b1",
        page_number=1,
        source=ContentSource.native,
        bbox=BoundingBox(x0=10, y0=10, x1=50, y1=20),
        text="Header 1",
        char_count=8,
        role=CanonicalRole.text
    )
    block2 = CanonicalBlock(
        block_id="b2",
        page_number=1,
        source=ContentSource.native,
        bbox=BoundingBox(x0=10, y0=30, x1=50, y1=40),
        text="Data 1",
        char_count=6,
        role=CanonicalRole.text
    )
    
    page = CanonicalPage(
        page_number=1,
        width=612,
        height=792,
        rotation=0,
        block_count=2,
        text_char_count=14,
        has_native_text=True,
        used_ocr=False,
        needs_review=False,
        blocks=[block1, block2],
        tables=[] # Empty
    )
    
    doc = CanonicalDocument(
        document_id="doc1",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=2,
        total_text_char_count=14,
        ocr_page_count=0,
        pages=[page]
    )
    
    skill = TableRepairSkill()
    settings = Settings()
    
    # Patch TableDetectionService to return a table
    mock_table = CanonicalTable(
        table_id="t1",
        bbox=BoundingBox(x0=10, y0=10, x1=50, y1=40),
        rows=[
            CanonicalRow(cells=[CanonicalCell(bbox=block1.bbox, role=CanonicalRole.table_header, block_ids=["b1"])]),
            CanonicalRow(cells=[CanonicalCell(bbox=block2.bbox, role=CanonicalRole.table_data, block_ids=["b2"])])
        ]
    )
    
    mocker.patch(
        "pdf_accessibility.services.tables.TableDetectionService.detect_tables",
        return_value=[mock_table]
    )
    
    actions = skill.remediate(doc, settings)
    
    assert len(page.tables) == 1
    assert block1.role == CanonicalRole.table_header
    assert block2.role == CanonicalRole.table_data

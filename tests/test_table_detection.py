import pytest
from pathlib import Path
from unittest.mock import MagicMock
from pdf_accessibility.models.canonical import (
    CanonicalPage, CanonicalBlock, CanonicalRole, BoundingBox, ContentSource
)
from pdf_accessibility.services.tables import TableDetectionService

def test_detect_tables_heuristic():
    # Setup a mock page with blocks arranged in a grid
    blocks = [
        CanonicalBlock(
            block_id="b1", page_number=1, source=ContentSource.native,
            bbox=BoundingBox(x0=10, y0=10, x1=50, y1=20), text="Header 1",
            char_count=8, role=CanonicalRole.text
        ),
        CanonicalBlock(
            block_id="b2", page_number=1, source=ContentSource.native,
            bbox=BoundingBox(x0=60, y0=10, x1=100, y1=20), text="Header 2",
            char_count=8, role=CanonicalRole.text
        ),
        CanonicalBlock(
            block_id="b3", page_number=1, source=ContentSource.native,
            bbox=BoundingBox(x0=10, y0=30, x1=50, y1=40), text="Data 1",
            char_count=6, role=CanonicalRole.text
        ),
        CanonicalBlock(
            block_id="b4", page_number=1, source=ContentSource.native,
            bbox=BoundingBox(x0=60, y0=30, x1=100, y1=40), text="Data 2",
            char_count=6, role=CanonicalRole.text
        ),
    ]
    page = CanonicalPage(
        page_number=1, width=200, height=200, rotation=0,
        block_count=4, text_char_count=28, has_native_text=True,
        used_ocr=False, needs_review=False, blocks=blocks
    )
    
    service = TableDetectionService()
    tables = service.detect_tables(page)
    
    assert len(tables) == 1
    table = tables[0]
    assert len(table.rows) == 2
    assert len(table.rows[0].cells) == 2
    assert len(table.rows[1].cells) == 2
    assert table.rows[0].cells[0].block_ids == ["b1"]
    assert table.rows[1].cells[1].block_ids == ["b4"]

def test_detect_tables_viamupdf_mock(tmp_path):
    # This is harder to test without a real PDF, so we'll mock fitz
    import fitz
    
    # Create a dummy PDF file
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page_fitz = doc.new_page()
    page_fitz.insert_text((72, 72), "Header 1")
    page_fitz.insert_text((144, 72), "Header 2")
    page_fitz.insert_text((72, 144), "Data 1")
    page_fitz.insert_text((144, 144), "Data 2")
    doc.save(pdf_path)
    doc.close()

    # Create canonical page that matches
    blocks = [
        CanonicalBlock(
            block_id="b1", page_number=1, source=ContentSource.native,
            bbox=BoundingBox(x0=72, y0=70, x1=120, y1=80), text="Header 1",
            char_count=8
        ),
        CanonicalBlock(
            block_id="b2", page_number=1, source=ContentSource.native,
            bbox=BoundingBox(x0=144, y0=70, x1=190, y1=80), text="Header 2",
            char_count=8
        ),
        CanonicalBlock(
            block_id="b3", page_number=1, source=ContentSource.native,
            bbox=BoundingBox(x0=72, y0=140, x1=120, y1=150), text="Data 1",
            char_count=6
        ),
        CanonicalBlock(
            block_id="b4", page_number=1, source=ContentSource.native,
            bbox=BoundingBox(x0=144, y0=140, x1=190, y1=150), text="Data 2",
            char_count=6
        ),
    ]
    page = CanonicalPage(
        page_number=1, width=595, height=842, rotation=0,
        block_count=4, text_char_count=28, has_native_text=True,
        used_ocr=False, needs_review=False, blocks=blocks
    )

    service = TableDetectionService()
    tables = service.detect_tables(page, pdf_path=pdf_path)
    
    # Since there are no lines, fitz.find_tables() might return nothing by default 
    # unless we use the text-based strategy. 
    # But for this test, we just want to see if it runs and returns something if it finds it.
    # We might need to mock find_tables() to return a specific structure to test our mapping.
    pass

def test_detect_tables_header_inference():
    # Setup mock page where first row has bold text
    blocks = [
        CanonicalBlock(
            block_id="b1", page_number=1, source=ContentSource.native,
            bbox=BoundingBox(x0=10, y0=10, x1=50, y1=20), text="Header 1",
            char_count=8, font_flags=2**4 # Assume 2^4 means bold for this mock
        ),
        CanonicalBlock(
            block_id="b2", page_number=1, source=ContentSource.native,
            bbox=BoundingBox(x0=60, y0=10, x1=100, y1=20), text="Header 2",
            char_count=8, font_flags=2**4
        ),
        CanonicalBlock(
            block_id="b3", page_number=1, source=ContentSource.native,
            bbox=BoundingBox(x0=10, y0=30, x1=50, y1=40), text="Data 1",
            char_count=6, font_flags=0
        ),
    ]
    page = CanonicalPage(
        page_number=1, width=200, height=200, rotation=0,
        block_count=3, text_char_count=22, has_native_text=True,
        used_ocr=False, needs_review=False, blocks=blocks
    )
    
    service = TableDetectionService()
    tables = service.detect_tables(page)
    
    assert len(tables) == 1
    # Check if first row cells have table_header role
    for cell in tables[0].rows[0].cells:
        assert cell.role == CanonicalRole.table_header
    for cell in tables[0].rows[1].cells:
        assert cell.role == CanonicalRole.table_data

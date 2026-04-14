from __future__ import annotations

import pytest

from pdf_accessibility.models.documents import BoundingBox, ParserTextBlock
from pdf_accessibility.services.reading_order import ReadingOrderEngine


def test_reading_order_single_column():
    engine = ReadingOrderEngine()
    blocks = [
        ParserTextBlock(block_number=1, bbox=BoundingBox(x0=50, y0=200, x1=500, y1=250), text="Second", char_count=6),
        ParserTextBlock(block_number=2, bbox=BoundingBox(x0=50, y0=100, x1=500, y1=150), text="First", char_count=5),
    ]
    
    sorted_blocks = engine.sort_blocks(blocks)
    assert sorted_blocks[0].text == "First"
    assert sorted_blocks[1].text == "Second"


def test_reading_order_multi_column():
    engine = ReadingOrderEngine()
    # Layout:
    # Header (Spanning)
    # Col 1 | Col 2
    # Footer (Spanning)
    blocks = [
        ParserTextBlock(block_number=1, bbox=BoundingBox(x0=50, y0=50, x1=550, y1=80), text="Header", char_count=6),
        ParserTextBlock(block_number=2, bbox=BoundingBox(x0=50, y0=100, x1=280, y1=150), text="Col 1 Top", char_count=9),
        ParserTextBlock(block_number=3, bbox=BoundingBox(x0=50, y0=160, x1=280, y1=210), text="Col 1 Bottom", char_count=12),
        ParserTextBlock(block_number=4, bbox=BoundingBox(x0=300, y0=100, x1=550, y1=150), text="Col 2 Top", char_count=9),
        ParserTextBlock(block_number=5, bbox=BoundingBox(x0=300, y0=160, x1=550, y1=210), text="Col 2 Bottom", char_count=12),
        ParserTextBlock(block_number=6, bbox=BoundingBox(x0=50, y0=250, x1=550, y1=280), text="Footer", char_count=6),
    ]
    
    sorted_blocks = engine.sort_blocks(blocks)
    texts = [b.text for b in sorted_blocks]
    assert texts == ["Header", "Col 1 Top", "Col 1 Bottom", "Col 2 Top", "Col 2 Bottom", "Footer"]


def test_reading_order_empty():
    engine = ReadingOrderEngine()
    assert engine.sort_blocks([]) == []

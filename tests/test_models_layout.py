from pdf_accessibility.models.canonical import CanonicalBlock, CanonicalRole, ContentSource
from pdf_accessibility.models.documents import BoundingBox, ParserTextBlock


def test_canonical_block_with_role_and_font():
    bbox = BoundingBox(x0=0, y0=0, x1=100, y1=100)
    block = CanonicalBlock(
        block_id="1",
        page_number=1,
        source=ContentSource.native,
        bbox=bbox,
        text="Hello World",
        char_count=11,
        role=CanonicalRole.heading1,
        font_size=12.5,
        font_name="Arial-Bold",
        font_flags=4,
    )
    assert block.role == CanonicalRole.heading1
    assert block.font_size == 12.5
    assert block.font_name == "Arial-Bold"
    assert block.font_flags == 4


def test_parser_text_block_with_font():
    bbox = BoundingBox(x0=0, y0=0, x1=100, y1=100)
    block = ParserTextBlock(
        block_number=1,
        bbox=bbox,
        text="Hello World",
        char_count=11,
        font_size=12.5,
        font_name="Arial-Bold",
        font_flags=4,
    )
    assert block.font_size == 12.5
    assert block.font_name == "Arial-Bold"
    assert block.font_flags == 4


def test_canonical_role_enum():
    assert CanonicalRole.heading1 == "heading1"
    assert CanonicalRole.text == "text"
    assert CanonicalRole.list == "list"
    assert CanonicalRole.table == "table"

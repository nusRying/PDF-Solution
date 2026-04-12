import pytest
from pikepdf import Pdf, Name
from pdf_accessibility.services.tagging import TaggingEngine
from pdf_accessibility.models.canonical import CanonicalRole

def test_map_role_to_tag():
    engine = TaggingEngine()
    assert engine.map_role_to_tag(CanonicalRole.heading1) == "/H1"
    assert engine.map_role_to_tag(CanonicalRole.heading2) == "/H2"
    assert engine.map_role_to_tag(CanonicalRole.text) == "/P"
    assert engine.map_role_to_tag(CanonicalRole.list) == "/L"
    assert engine.map_role_to_tag(CanonicalRole.list_item) == "/LI"
    assert engine.map_role_to_tag(CanonicalRole.table) == "/Table"
    assert engine.map_role_to_tag(CanonicalRole.figure) == "/Figure"
    assert engine.map_role_to_tag(CanonicalRole.caption) == "/Caption"
    assert engine.map_role_to_tag(CanonicalRole.artifact) is None # Artifacts aren't tagged in StructTree

def test_invalid_role_mapping():
    engine = TaggingEngine()
    with pytest.raises(ValueError):
        engine.map_role_to_tag("invalid_role")

def test_build_struct_tree():
    import pikepdf
    from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalPage, CanonicalBlock, CanonicalMetadata
    from pdf_accessibility.models.documents import BoundingBox, DocumentSourceType
    from datetime import datetime

    pdf = pikepdf.new()
    pdf.add_blank_page()

    doc = CanonicalDocument(
        document_id="test_id",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=2,
        total_text_char_count=10,
        ocr_page_count=0,
        metadata=CanonicalMetadata(),
        pages=[
            CanonicalPage(
                page_number=1,
                width=612,
                height=792,
                rotation=0,
                block_count=2,
                text_char_count=10,
                has_native_text=True,
                used_ocr=False,
                needs_review=False,
                blocks=[
                    CanonicalBlock(
                        block_id="b1",
                        page_number=1,
                        source="native",
                        bbox=BoundingBox(x0=0, y0=0, x1=100, y1=100),
                        text="Heading",
                        char_count=7,
                        role=CanonicalRole.heading1
                    ),
                    CanonicalBlock(
                        block_id="b2",
                        page_number=1,
                        source="native",
                        bbox=BoundingBox(x0=0, y0=100, x1=100, y1=200),
                        text="Paragraph",
                        char_count=9,
                        role=CanonicalRole.text
                    )
                ]
            )
        ]
    )

    engine = TaggingEngine()
    engine.build_struct_tree(pdf, doc)

    assert "/StructTreeRoot" in pdf.Root
    struct_tree_root = pdf.Root.StructTreeRoot
    assert "/K" in struct_tree_root
    kids = struct_tree_root.K
    assert len(kids) == 2
    assert kids[0].S == "/H1"
    assert kids[1].S == "/P"

def test_build_struct_tree_list_nesting():
    import pikepdf
    from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalPage, CanonicalBlock, CanonicalMetadata
    from pdf_accessibility.models.documents import BoundingBox, DocumentSourceType

    pdf = pikepdf.new()
    pdf.add_blank_page()

    doc = CanonicalDocument(
        document_id="test_list_id",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=3,
        total_text_char_count=30,
        ocr_page_count=0,
        metadata=CanonicalMetadata(),
        pages=[
            CanonicalPage(
                page_number=1,
                width=612,
                height=792,
                rotation=0,
                block_count=3,
                text_char_count=30,
                has_native_text=True,
                used_ocr=False,
                needs_review=False,
                blocks=[
                    CanonicalBlock(
                        block_id="l1",
                        page_number=1,
                        source="native",
                        bbox=BoundingBox(x0=0, y0=0, x1=100, y1=100),
                        text="List parent",
                        char_count=10,
                        role=CanonicalRole.list
                    ),
                    CanonicalBlock(
                        block_id="li1",
                        page_number=1,
                        source="native",
                        bbox=BoundingBox(x0=0, y0=100, x1=100, y1=200),
                        text="Item 1",
                        char_count=6,
                        role=CanonicalRole.list_item
                    ),
                    CanonicalBlock(
                        block_id="li2",
                        page_number=1,
                        source="native",
                        bbox=BoundingBox(x0=0, y0=200, x1=100, y1=300),
                        text="Item 2",
                        char_count=6,
                        role=CanonicalRole.list_item
                    )
                ]
            )
        ]
    )

    engine = TaggingEngine()
    engine.build_struct_tree(pdf, doc)

    struct_tree_root = pdf.Root.StructTreeRoot
    kids = struct_tree_root.K
    assert len(kids) == 1
    list_elem = kids[0]
    assert list_elem.S == "/L"
    assert len(list_elem.K) == 2
    assert list_elem.K[0].S == "/LI"
    assert list_elem.K[1].S == "/LI"

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

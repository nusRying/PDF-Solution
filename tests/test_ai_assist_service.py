import pytest
from pdf_accessibility.services.ai_assist import AIAssistService
from pdf_accessibility.core.settings import get_settings
from pdf_accessibility.models.canonical import CanonicalBlock, CanonicalRole
from pdf_accessibility.models.documents import BoundingBox, DocumentSourceType

@pytest.fixture
def ai_service():
    return AIAssistService(get_settings())

def test_generate_alt_text_logo(ai_service):
    block = CanonicalBlock(
        block_id="b1",
        page_number=1,
        source="native",
        bbox=BoundingBox(x0=0, y0=0, x1=10, y1=10),
        text="Company Logo",
        char_count=12,
        role=CanonicalRole.figure
    )
    alt_text, confidence = ai_service.generate_alt_text(block)
    assert "logo" in alt_text.lower()
    assert confidence > 0.9

def test_generate_alt_text_chart(ai_service):
    block = CanonicalBlock(
        block_id="b2",
        page_number=1,
        source="native",
        bbox=BoundingBox(x0=0, y0=0, x1=10, y1=10),
        text="Sales Chart 2023",
        char_count=16,
        role=CanonicalRole.figure
    )
    alt_text, confidence = ai_service.generate_alt_text(block)
    assert "chart" in alt_text.lower()
    assert confidence > 0.8

def test_disambiguate_role_list(ai_service):
    block = CanonicalBlock(
        block_id="b3",
        page_number=1,
        source="native",
        bbox=BoundingBox(x0=0, y0=0, x1=10, y1=10),
        text="\u2022 This is a bullet point",
        char_count=23,
        role=CanonicalRole.text
    )
    role, confidence = ai_service.disambiguate_role(block)
    assert role == CanonicalRole.list_item
    assert confidence > 0.8

import pytest
from pdf_accessibility.models.canonical import (
    CanonicalDocument,
    CanonicalPage,
    CanonicalForm,
    BoundingBox,
    DocumentSourceType
)
from pdf_accessibility.core.settings import Settings
from pdf_accessibility.skills.remediation.forms import FormRepairSkill

def test_form_repair_skill_basic():
    # Setup: Canonical document with a form field missing a tooltip
    form1 = CanonicalForm(
        field_id="f1",
        page_number=1,
        name="email_address",
        tooltip=None,
        bbox=BoundingBox(x0=100, y0=100, x1=200, y1=120)
    )
    form2 = CanonicalForm(
        field_id="f2",
        page_number=1,
        name="phone_number",
        tooltip="Enter your phone number",
        bbox=BoundingBox(x0=100, y0=130, x1=200, y1=150)
    )
    
    page = CanonicalPage(
        page_number=1,
        width=612,
        height=792,
        rotation=0,
        block_count=0,
        text_char_count=0,
        has_native_text=True,
        used_ocr=False,
        needs_review=False,
        blocks=[],
        tables=[],
        forms=[form1, form2]
    )
    
    doc = CanonicalDocument(
        document_id="doc1",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        pages=[page]
    )
    
    skill = FormRepairSkill()
    settings = Settings()
    actions = skill.remediate(doc, settings)
    
    # Assertions
    assert len(actions) == 1
    assert form1.tooltip == "Email Address"
    assert form2.tooltip == "Enter your phone number"
    assert actions[0].block_id is None # form field id is stored elsewhere or not as block_id?
    # Actually RemediationAction has block_id field, maybe we should use it for field_id too?
    # Current implementation doesn't set block_id.

from pdf_accessibility.skills.remediation.forms import FormTabOrderSkill

def test_form_tab_order_skill_basic():
    # Setup: Canonical document with form fields in jumbled order
    form1 = CanonicalForm(
        field_id="f1",
        page_number=1,
        name="field1",
        bbox=BoundingBox(x0=100, y0=200, x1=200, y1=220)
    )
    form2 = CanonicalForm(
        field_id="f2",
        page_number=1,
        name="field2",
        bbox=BoundingBox(x0=100, y0=100, x1=200, y1=120)
    )
    
    page = CanonicalPage(
        page_number=1,
        width=612,
        height=792,
        rotation=0,
        block_count=0,
        text_char_count=0,
        has_native_text=True,
        used_ocr=False,
        needs_review=False,
        blocks=[],
        tables=[],
        forms=[form1, form2]
    )
    
    doc = CanonicalDocument(
        document_id="doc1",
        source_type=DocumentSourceType.digital,
        page_count=1,
        total_block_count=0,
        total_text_char_count=0,
        ocr_page_count=0,
        pages=[page]
    )
    
    skill = FormTabOrderSkill()
    settings = Settings()
    actions = skill.remediate(doc, settings)
    
    # Assertions
    assert len(actions) == 1
    assert page.forms[0].field_id == "f2" # f2 is at y=100, f1 is at y=200
    assert page.forms[1].field_id == "f1"

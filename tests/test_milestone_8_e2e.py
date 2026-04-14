from __future__ import annotations

import os
from pathlib import Path

import fitz
import pikepdf
import pytest
from fastapi.testclient import TestClient

from pdf_accessibility.core.settings import get_settings
from pdf_accessibility.models.canonical import CanonicalRole
from tests.test_health import _wait_for_terminal_job_state, client


def _build_pdf_with_table_and_form(tmp_path: Path) -> bytes:
    """Builds a PDF with a simple table and a text form field."""
    pdf_path = tmp_path / "test_input.pdf"
    doc = fitz.open()
    page = doc.new_page()
    
    # 1. Add some text that looks like a table
    # Header Row
    page.insert_text((72, 100), "Product", fontsize=12)
    page.insert_text((200, 100), "Price", fontsize=12)
    # Data Row
    page.insert_text((72, 120), "Widget", fontsize=10)
    page.insert_text((200, 120), "$10.00", fontsize=10)
    
    # 2. Add a form field
    widget = fitz.Widget()
    widget.rect = fitz.Rect(72, 200, 200, 220)
    widget.field_name = "user_name"
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.field_value = ""
    widget.field_label = "Enter your full name"
    page.add_widget(widget)
    
    doc.set_metadata({"title": "Milestone 8 Test"})
    doc.save(pdf_path)
    doc.close()
    
    pdf_bytes = pdf_path.read_bytes()
    return pdf_bytes


def test_table_and_form_detection_and_tagging(client: TestClient, tmp_path: Path):
    # 1. Upload the test PDF
    pdf_bytes = _build_pdf_with_table_and_form(tmp_path)
    
    upload_response = client.post(
        "/api/v1/documents",
        files={"file": ("milestone8.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_response.status_code == 202
    payload = upload_response.json()
    document_id = payload["document"]["document_id"]
    job_id = payload["job"]["job_id"]
    
    # 2. Wait for processing
    job_payload = _wait_for_terminal_job_state(client, job_id)
    assert job_payload["status"] == "succeeded"
    
    # 3. Verify Canonical Output contains tables and forms
    canonical_response = client.get(f"/api/v1/documents/{document_id}/canonical-output")
    assert canonical_response.status_code == 200
    canonical_data = canonical_response.json()
    
    page = canonical_data["pages"][0]
    # Check if a table was detected
    assert len(page["tables"]) >= 1
    table = page["tables"][0]
    assert len(table["rows"]) >= 2
    
    # Check if form was detected
    assert len(page["forms"]) >= 1
    form = page["forms"][0]
    assert form["name"] == "user_name"
    
    # 4. Verify Tagging in output PDF
    settings = get_settings()
    output_pdf_path = settings.output_dir / f"{document_id}.pdf"
    assert output_pdf_path.exists()
    
    with pikepdf.open(output_pdf_path) as pdf:
        assert "/StructTreeRoot" in pdf.Root
        struct_tree = pdf.Root.StructTreeRoot
        
        # We expect a /Table and a /Form tag in the structure tree
        tags = [str(k.S) for k in struct_tree.K]
        assert "/Table" in tags
        assert "/Form" in tags
        
        # Verify Table internal structure
        table_elem = next(k for k in struct_tree.K if k.S == "/Table")
        assert len(table_elem.K) >= 2 # Rows
        assert all(row.S == "/TR" for row in table_elem.K)

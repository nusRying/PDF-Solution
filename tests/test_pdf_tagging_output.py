from __future__ import annotations

from pathlib import Path

import fitz
import pikepdf
import pytest
from fastapi.testclient import TestClient

from pdf_accessibility.core.settings import get_settings
from tests.test_health import _build_pdf_bytes, _wait_for_terminal_job_state, client


def test_remediated_pdf_contains_tags_and_ua_metadata(client: TestClient, tmp_path: Path):
    # 1. Upload a PDF
    pdf_bytes = _build_pdf_bytes("Structural tagging test.")
    
    upload_response = client.post(
        "/api/v1/documents",
        files={"file": ("tagging_test.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_response.status_code == 202
    payload = upload_response.json()
    document_id = payload["document"]["document_id"]
    job_id = payload["job"]["job_id"]
    
    # 2. Wait for processing to finish
    _wait_for_terminal_job_state(client, job_id)
    
    # 3. Download the remediated PDF
    # In a real scenario, we'd have a download endpoint. 
    # For now, we access it from the file system via settings.
    settings = get_settings()
    # Note: tmp_path in fixture might be different from app's DATA_ROOT if not careful
    # But our client fixture sets DATA_ROOT to a subfolder of tmp_path.
    
    output_pdf_path = settings.output_dir / f"{document_id}.pdf"
    assert output_pdf_path.exists()
    
    # 4. Verify structural tags using pikepdf
    with pikepdf.open(output_pdf_path) as pdf:
        # Check for Structure Tree
        assert "/StructTreeRoot" in pdf.Root
        struct_tree = pdf.Root.StructTreeRoot
        assert len(struct_tree.K) >= 1
        
        # Check for MarkInfo
        assert pdf.Root.MarkInfo.Marked is True
        
        # Check for PDF/UA identifier in XMP
        xmp = str(pdf.open_metadata())
        assert "pdfuaid:part" in xmp or "http://www.aiim.org/pdfua/ns/id/" in xmp
        
        # Check for Language
        assert hasattr(pdf.Root, "Lang")
        
        # Check for DisplayDocTitle
        assert pdf.Root.ViewerPreferences.DisplayDocTitle is True

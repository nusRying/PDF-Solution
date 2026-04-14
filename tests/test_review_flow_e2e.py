from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pdf_accessibility.models.canonical import CanonicalRole
from pdf_accessibility.models.review import ManualOverride
from tests.test_health import client, _build_pdf_bytes, _wait_for_terminal_job_state


def test_human_in_the_loop_review_flow(client: TestClient) -> None:
    # 1. Upload a PDF
    pdf_bytes = _build_pdf_bytes("This should be a heading.")
    
    upload_response = client.post(
        "/api/v1/documents",
        files={"file": ("review_test.pdf", pdf_bytes, "application/pdf")},
    )
    assert upload_response.status_code == 202
    payload = upload_response.json()
    document_id = payload["document"]["document_id"]
    job_id = payload["job"]["job_id"]
    
    # 2. Wait for initial processing
    _wait_for_terminal_job_state(client, job_id)
    
    # 3. Check initial canonical output
    canonical_response = client.get(f"/api/v1/documents/{document_id}/canonical-output")
    assert canonical_response.status_code == 200
    canonical_payload = canonical_response.json()
    first_block = canonical_payload["pages"][0]["blocks"][0]
    block_id = first_block["block_id"]
    
    # 4. Submit a manual override (Human-in-the-loop)
    # Change role to heading1
    override_request = {
        "override": {
            "block_id": block_id,
            "role": "heading1",
            "alt_text": "Updated Alt Text"
        }
    }
    review_response = client.post(
        f"/api/v1/documents/{document_id}/review/actions",
        json=override_request
    )
    assert review_response.status_code == 200
    
    # Actually, let's just check if the ReviewService.apply_overrides works as expected.
    from pdf_accessibility.services.file_store import get_file_store
    from pdf_accessibility.services.review import ReviewService
    from pdf_accessibility.core.settings import get_settings
    from pdf_accessibility.models.canonical import CanonicalDocument
    
    settings = get_settings()
    store = get_file_store(settings)
    review_service = ReviewService(store)
    
    doc_artifact = store.get_canonical_artifact(document_id)
    review_artifact = store.get_review_artifact(document_id)
    
    actions = review_service.apply_overrides(doc_artifact, review_artifact)
    assert len(actions) >= 1
    assert doc_artifact.pages[0].blocks[0].role == CanonicalRole.heading1
    assert doc_artifact.pages[0].blocks[0].alt_text == "Updated Alt Text"

from __future__ import annotations

import os
import time
from pathlib import Path

import fitz
import pytest
from fastapi.testclient import TestClient

from pdf_accessibility.core.settings import get_settings
from pdf_accessibility.main import create_app


def _build_pdf_bytes(text: str) -> bytes:
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), text)
    document.set_metadata({"title": "Test Document"})
    pdf_bytes = document.tobytes()
    document.close()
    return pdf_bytes


def _build_image_only_pdf_bytes(text: str) -> bytes:
    source = fitz.open()
    source_page = source.new_page(width=595, height=842)
    source_page.insert_text((72, 120), text, fontsize=28)
    pixmap = source_page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
    source.close()

    scanned = fitz.open()
    page = scanned.new_page(width=595, height=842)
    page.insert_image(page.rect, stream=pixmap.tobytes("png"))
    scanned.set_metadata({"title": "Scanned Test Document"})
    pdf_bytes = scanned.tobytes()
    scanned.close()
    return pdf_bytes


def _wait_for_terminal_job_state(
    client: TestClient,
    job_id: str,
    timeout_seconds: float = 25.0,
) -> dict:
    deadline = time.monotonic() + timeout_seconds
    last_payload: dict | None = None

    while time.monotonic() < deadline:
        response = client.get(f"/api/v1/jobs/{job_id}")
        assert response.status_code == 200
        payload = response.json()
        last_payload = payload
        if payload["status"] in {"succeeded", "failed"}:
            return payload
        time.sleep(0.1)

    pytest.fail(f"Timed out waiting for job {job_id}. Last payload: {last_payload}")


def _lane_bucket(payload: dict, lane: str) -> dict:
    return next(bucket for bucket in payload["lanes"] if bucket["lane"] == lane)


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("DATA_ROOT", str(tmp_path / "data"))
    monkeypatch.setenv(
        "TESSERACT_EXE",
        os.environ.get("TESSERACT_EXE", r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
    )
    monkeypatch.setenv(
        "TESSDATA_PREFIX",
        os.environ.get("TESSDATA_PREFIX", r"C:\Program Files\Tesseract-OCR\tessdata"),
    )
    monkeypatch.setenv("QPDF_EXE", os.environ.get("QPDF_EXE", "qpdf"))
    get_settings.cache_clear()
    with TestClient(create_app()) as test_client:
        yield test_client
    get_settings.cache_clear()


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "PDF Accessibility Remediation Platform"


def test_healthz_endpoint(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_pdf_and_fetch_job_artifacts(client: TestClient) -> None:
    pdf_bytes = _build_pdf_bytes("Hello from the parser bootstrap.")

    upload_response = client.post(
        "/api/v1/documents",
        files={"file": ("sample.pdf", pdf_bytes, "application/pdf")},
    )

    assert upload_response.status_code == 202
    payload = upload_response.json()
    document_id = payload["document"]["document_id"]
    job_id = payload["job"]["job_id"]
    assert payload["job"]["status"] == "pending"

    job_payload = _wait_for_terminal_job_state(client, job_id)
    assert job_payload["status"] == "succeeded"
    assert job_payload["document_id"] == document_id
    assert "parser" in job_payload["artifacts"]
    assert "preflight" in job_payload["artifacts"]
    assert "remediation" in job_payload["artifacts"]
    assert "remediated_canonical" in job_payload["artifacts"]
    assert job_payload["current_stage"] == "completed"
    assert len(job_payload["stage_events"]) >= 8
    assert job_payload["summary"]["remediation_action_count"] is not None
    assert job_payload["summary"]["processing_lane"] in {"fast", "standard", "heavy", "manual"}
    assert job_payload["summary"]["lane_policy"] is not None
    assert job_payload["summary"]["ocr_mode"] in {"skip", "selective"}
    assert job_payload["summary"]["processing_duration_seconds"] is not None
    assert job_payload["summary"]["throughput_pages_per_second"] is not None
    assert isinstance(job_payload["summary"]["preflight_classes"], list)

    metrics_response = client.get(f"/api/v1/jobs/{job_id}/metrics")
    assert metrics_response.status_code == 200
    metrics_payload = metrics_response.json()
    assert metrics_payload["processing_lane"] == job_payload["summary"]["processing_lane"]
    assert metrics_payload["throughput_pages_per_second"] == job_payload["summary"]["throughput_pages_per_second"]
    assert metrics_payload["processing_duration_seconds"] == job_payload["summary"]["processing_duration_seconds"]

    lane_metrics_response = client.get("/api/v1/metrics/lanes")
    assert lane_metrics_response.status_code == 200
    lane_metrics_payload = lane_metrics_response.json()
    assert lane_metrics_payload["totals"]["total_attempt_count"] == 1
    assert lane_metrics_payload["totals"]["classified_attempt_count"] == 1
    assert lane_metrics_payload["totals"]["succeeded_count"] == 1
    standard_bucket = _lane_bucket(lane_metrics_payload, "standard")
    assert standard_bucket["total_attempt_count"] == 1
    assert standard_bucket["succeeded_count"] == 1
    assert standard_bucket["failed_count"] == 0
    assert standard_bucket["average_throughput_pages_per_second"] is not None

    parser_response = client.get(f"/api/v1/documents/{document_id}/parser-output")
    assert parser_response.status_code == 200
    parser_payload = parser_response.json()
    assert parser_payload["page_count"] == 1
    assert parser_payload["text_page_count"] == 1
    assert parser_payload["pages"][0]["has_text"] is True
    assert parser_payload["pages"][0]["text_blocks"]

    preflight_response = client.get(f"/api/v1/documents/{document_id}/preflight-output")
    assert preflight_response.status_code == 200
    preflight_payload = preflight_response.json()
    assert preflight_payload["lane"] == job_payload["summary"]["processing_lane"]
    assert any(
        item in {"tagged-digital-born", "untagged-digital-born"}
        for item in preflight_payload["classes"]
    )

    canonical_response = client.get(f"/api/v1/documents/{document_id}/canonical-output")
    assert canonical_response.status_code == 200
    canonical_payload = canonical_response.json()
    assert canonical_payload["total_block_count"] >= 1
    assert canonical_payload["pages"][0]["used_ocr"] is False

    remediated_canonical_response = client.get(
        f"/api/v1/documents/{document_id}/remediated-canonical-output"
    )
    assert remediated_canonical_response.status_code == 200
    remediated_canonical_payload = remediated_canonical_response.json()
    assert remediated_canonical_payload["total_block_count"] >= 1

    remediation_response = client.get(f"/api/v1/documents/{document_id}/remediation-output")
    assert remediation_response.status_code == 200
    remediation_payload = remediation_response.json()
    assert remediation_payload["document_id"] == document_id

    validation_response = client.get(f"/api/v1/documents/{document_id}/validation-output")
    assert validation_response.status_code == 200
    validation_payload = validation_response.json()
    assert validation_payload["status"] == "passed"
    assert validation_payload["finding_count"] >= 1
    assert any(finding["rule_id"] == "LANE-000" for finding in validation_payload["findings"])


def test_upload_image_only_pdf_runs_ocr_and_builds_canonical_output(client: TestClient) -> None:
    pdf_bytes = _build_image_only_pdf_bytes("Scanned OCR smoke test")

    upload_response = client.post(
        "/api/v1/documents",
        files={"file": ("scanned.pdf", pdf_bytes, "application/pdf")},
    )

    assert upload_response.status_code == 202
    payload = upload_response.json()
    document_id = payload["document"]["document_id"]
    job_id = payload["job"]["job_id"]
    job_payload = _wait_for_terminal_job_state(client, job_id)
    assert job_payload["status"] == "succeeded"
    assert job_payload["summary"]["source_type"] in {"scanned", "image-only"}
    assert job_payload["summary"]["processing_lane"] == "heavy"
    assert job_payload["summary"]["ocr_mode"] == "selective"

    ocr_response = client.get(f"/api/v1/documents/{document_id}/ocr-output")
    assert ocr_response.status_code == 200
    ocr_payload = ocr_response.json()
    assert ocr_payload["attempted_page_count"] == 1
    assert ocr_payload["engine"] == "tesseract"

    canonical_response = client.get(f"/api/v1/documents/{document_id}/canonical-output")
    assert canonical_response.status_code == 200
    canonical_payload = canonical_response.json()
    assert canonical_payload["ocr_page_count"] == 1
    assert canonical_payload["pages"][0]["used_ocr"] is True
    assert canonical_payload["pages"][0]["block_count"] >= 1

    preflight_response = client.get(f"/api/v1/documents/{document_id}/preflight-output")
    assert preflight_response.status_code == 200
    preflight_payload = preflight_response.json()
    assert preflight_payload["lane"] == "heavy"
    assert "scanned-image-only" in preflight_payload["classes"]

    metrics_response = client.get(f"/api/v1/jobs/{job_id}/metrics")
    assert metrics_response.status_code == 200
    metrics_payload = metrics_response.json()
    assert metrics_payload["processing_lane"] == "heavy"
    assert metrics_payload["ocr_attempted_page_count"] == 1
    assert metrics_payload["ocr_completed_page_count"] in {0, 1}

    lane_metrics_response = client.get("/api/v1/metrics/lanes")
    assert lane_metrics_response.status_code == 200
    lane_metrics_payload = lane_metrics_response.json()
    assert lane_metrics_payload["totals"]["total_attempt_count"] == 1
    assert lane_metrics_payload["totals"]["classified_attempt_count"] == 1
    assert lane_metrics_payload["totals"]["succeeded_count"] == 1
    heavy_bucket = _lane_bucket(lane_metrics_payload, "heavy")
    assert heavy_bucket["total_attempt_count"] == 1
    assert heavy_bucket["succeeded_count"] == 1
    assert heavy_bucket["total_ocr_attempted_page_count"] == 1

    remediation_response = client.get(f"/api/v1/documents/{document_id}/remediation-output")
    assert remediation_response.status_code == 200
    remediation_payload = remediation_response.json()
    assert remediation_payload["review_flagged_page_count"] >= 0

    validation_response = client.get(f"/api/v1/documents/{document_id}/validation-output")
    assert validation_response.status_code == 200
    validation_payload = validation_response.json()
    assert validation_payload["status"] == "needs-review"
    assert any(finding["rule_id"] == "VALID-OCR-002" for finding in validation_payload["findings"])

def test_upload_pdf_with_compliance_profile(client: TestClient) -> None:
    pdf_bytes = _build_pdf_bytes("Compliance profile test.")

    # Upload with Profile C (PDF/UA)
    upload_response = client.post(
        "/api/v1/documents",
        data={"profile": "Profile C: PDF/UA"},
        files={"file": ("profile.pdf", pdf_bytes, "application/pdf")},
    )

    assert upload_response.status_code == 202
    payload = upload_response.json()
    job_id = payload["job"]["job_id"]
    document_id = payload["document"]["document_id"]
    assert payload["job"]["compliance_profile"] == "Profile C: PDF/UA"

    job_payload = _wait_for_terminal_job_state(client, job_id)
    assert job_payload["status"] == "succeeded"
    assert job_payload["compliance_profile"] == "Profile C: PDF/UA"
    assert job_payload["summary"]["compliance_profile"] == "Profile C: PDF/UA"

    validation_response = client.get(f"/api/v1/documents/{document_id}/validation-output")
    assert validation_response.status_code == 200
    validation_payload = validation_response.json()
    assert validation_payload["profile"] == "Profile C: PDF/UA"

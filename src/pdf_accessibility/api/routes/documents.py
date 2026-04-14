from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status

from pdf_accessibility.core.settings import Settings, get_settings
from pdf_accessibility.models.compliance import ComplianceProfile
from pdf_accessibility.models.jobs import DocumentIngestResponse
from pdf_accessibility.services.file_store import get_file_store
from pdf_accessibility.services.ingestion import create_ingest_job
from pdf_accessibility.services.job_queue import BaseJobQueue

router = APIRouter(tags=["documents"])


@router.post(
    "/documents",
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    profile: ComplianceProfile = Form(default=ComplianceProfile.profile_b),
    settings: Settings = Depends(get_settings),
) -> DocumentIngestResponse:
    filename = (file.filename or "").lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF uploads are supported.",
        )

    try:
        document, job = await create_ingest_job(file, settings, profile=profile)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to ingest PDF: {exc}",
        ) from exc

    job_queue = getattr(request.app.state, "job_queue", None)
    if not isinstance(job_queue, BaseJobQueue):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ingestion queue is unavailable.",
        )
    job_queue.enqueue(job.job_id)

    return DocumentIngestResponse(document=document, job=job)


@router.get("/documents/{document_id}/parser-output")
def get_parser_output(
    document_id: str,
    settings: Settings = Depends(get_settings),
):
    store = get_file_store(settings)
    artifact = store.get_parser_artifact(document_id)
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document artifact not found.")
    return artifact


@router.get("/documents/{document_id}/ocr-output")
def get_ocr_output(
    document_id: str,
    settings: Settings = Depends(get_settings),
):
    store = get_file_store(settings)
    artifact = store.get_ocr_artifact(document_id)
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OCR artifact not found.")
    return artifact


@router.get("/documents/{document_id}/preflight-output")
def get_preflight_output(
    document_id: str,
    settings: Settings = Depends(get_settings),
):
    store = get_file_store(settings)
    artifact = store.get_preflight_artifact(document_id)
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Preflight artifact not found.")
    return artifact


@router.get("/documents/{document_id}/canonical-output")
def get_canonical_output(
    document_id: str,
    settings: Settings = Depends(get_settings),
):
    store = get_file_store(settings)
    artifact = store.get_canonical_artifact(document_id)
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Canonical artifact not found.")
    return artifact


@router.get("/documents/{document_id}/remediated-canonical-output")
def get_remediated_canonical_output(
    document_id: str,
    settings: Settings = Depends(get_settings),
):
    store = get_file_store(settings)
    artifact = store.get_remediated_canonical_artifact(document_id)
    if artifact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediated canonical artifact not found.",
        )
    return artifact


@router.get("/documents/{document_id}/remediation-output")
def get_remediation_output(
    document_id: str,
    settings: Settings = Depends(get_settings),
):
    store = get_file_store(settings)
    artifact = store.get_remediation_artifact(document_id)
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Remediation artifact not found.")
    return artifact


@router.get("/documents/{document_id}/validation-output")
def get_validation_output(
    document_id: str,
    settings: Settings = Depends(get_settings),
):
    store = get_file_store(settings)
    artifact = store.get_validation_artifact(document_id)
    if artifact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation artifact not found.")
    return artifact

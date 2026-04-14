from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from pdf_accessibility.core.settings import Settings, get_settings
from pdf_accessibility.models.review import ManualOverride, ReviewArtifact
from pdf_accessibility.services.file_store import get_file_store
from pdf_accessibility.services.review import ReviewService

router = APIRouter(tags=["review"])


class OverrideRequest(BaseModel):
    override: ManualOverride


@router.get("/documents/{document_id}/review", response_model=ReviewArtifact)
async def get_review_overrides(
    document_id: str,
    settings: Settings = Depends(get_settings),
):
    store = get_file_store(settings)
    review_service = ReviewService(store)
    return review_service.get_review_artifact(document_id)


@router.post("/documents/{document_id}/review/actions", status_code=status.HTTP_200_OK)
async def apply_review_action(
    document_id: str,
    request: OverrideRequest,
    settings: Settings = Depends(get_settings),
):
    store = get_file_store(settings)
    review_service = ReviewService(store)
    
    try:
        artifact = review_service.add_override(document_id, request.override)
        return {"status": "success", "artifact": artifact}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply override: {str(e)}"
        )

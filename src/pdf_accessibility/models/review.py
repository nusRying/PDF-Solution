from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field

from pdf_accessibility.models.documents import utc_now
from pdf_accessibility.models.canonical import CanonicalRole


class ManualOverride(BaseModel):
    """Represents a human-in-the-loop correction for a document block or form field."""
    block_id: str
    role: CanonicalRole | None = None
    alt_text: str | None = None
    tooltip: str | None = None
    is_artifact: bool | None = None


class ReviewArtifact(BaseModel):
    """Container for all manual overrides for a specific document."""
    document_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    overrides: list[ManualOverride] = Field(default_factory=list)

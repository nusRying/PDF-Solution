from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from pdf_accessibility.models.documents import utc_now


class RemediationAction(BaseModel):
    action_id: str
    rule_id: str
    page_number: int
    block_id: str | None = None
    source: str
    description: str
    changed: bool
    before_text: str | None = None
    after_text: str | None = None
    confidence: float | None = None


class RemediationArtifact(BaseModel):
    document_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    remediation_version: str = "0.1.0"
    action_count: int
    changed_action_count: int
    review_flagged_page_count: int
    actions: list[RemediationAction] = Field(default_factory=list)

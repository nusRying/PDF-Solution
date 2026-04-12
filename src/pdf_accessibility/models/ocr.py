from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from pdf_accessibility.models.documents import BoundingBox, utc_now


class OCRTextLine(BaseModel):
    line_number: int
    bbox: BoundingBox
    text: str
    confidence: float


class OCRPageResult(BaseModel):
    page_number: int
    width: float
    height: float
    line_count: int
    text_char_count: int
    average_confidence: float | None = None
    lines: list[OCRTextLine] = Field(default_factory=list)
    error: str | None = None


class OCRArtifact(BaseModel):
    document_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    engine: str
    engine_version: str | None = None
    language: str
    attempted_page_count: int
    completed_page_count: int
    pages: list[OCRPageResult] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from pdf_accessibility.models.documents import BoundingBox, DocumentSourceType, utc_now


class ContentSource(str, Enum):
    native = "native"
    ocr = "ocr"


class CanonicalBlock(BaseModel):
    block_id: str
    page_number: int
    source: ContentSource
    bbox: BoundingBox
    text: str
    char_count: int
    confidence: float | None = None


class CanonicalPage(BaseModel):
    page_number: int
    width: float
    height: float
    rotation: int
    block_count: int
    text_char_count: int
    has_native_text: bool
    used_ocr: bool
    needs_review: bool
    blocks: list[CanonicalBlock] = Field(default_factory=list)


class CanonicalDocument(BaseModel):
    document_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    source_type: DocumentSourceType
    page_count: int
    total_block_count: int
    total_text_char_count: int
    ocr_page_count: int
    pages: list[CanonicalPage]

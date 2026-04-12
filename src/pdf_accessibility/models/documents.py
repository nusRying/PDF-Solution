from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DocumentSourceType(str, Enum):
    digital = "digital"
    scanned = "scanned"
    hybrid = "hybrid"
    image_only = "image-only"
    unknown = "unknown"


class DocumentRecord(BaseModel):
    document_id: str
    original_filename: str
    stored_filename: str
    content_type: str | None = None
    file_size_bytes: int
    sha256: str
    source_type: DocumentSourceType = DocumentSourceType.unknown
    page_count: int | None = None
    original_path: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class ParserTextBlock(BaseModel):
    block_number: int
    bbox: BoundingBox
    text: str
    char_count: int


class ParserPageSummary(BaseModel):
    page_number: int
    width: float
    height: float
    rotation: int
    block_count: int
    image_count: int
    has_text: bool
    text_char_count: int
    text_preview: str
    text_blocks: list[ParserTextBlock] = Field(default_factory=list)


class ParserDocumentMetadata(BaseModel):
    title: str | None = None
    author: str | None = None
    subject: str | None = None
    creator: str | None = None
    producer: str | None = None
    creation_date: str | None = None
    modification_date: str | None = None


class ParserArtifact(BaseModel):
    document_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    parser_version: str = "0.1.0"
    source_path: str
    file_size_bytes: int
    page_count: int
    text_page_count: int
    image_page_count: int
    source_type: DocumentSourceType
    metadata: ParserDocumentMetadata
    pages: list[ParserPageSummary]

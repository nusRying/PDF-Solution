from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from pdf_accessibility.models.documents import BoundingBox, DocumentSourceType, utc_now


class ContentSource(str, Enum):
    native = "native"
    ocr = "ocr"


class CanonicalRole(str, Enum):
    heading1 = "heading1"
    heading2 = "heading2"
    heading3 = "heading3"
    heading4 = "heading4"
    heading5 = "heading5"
    heading6 = "heading6"
    list = "list"
    list_item = "list_item"
    table = "table"
    table_row = "table_row"
    table_header = "table_header"
    table_data = "table_data"
    form_field = "form_field"
    figure = "figure"
    caption = "caption"
    text = "text"
    artifact = "artifact"


class CanonicalMetadata(BaseModel):
    title: str | None = None
    author: str | None = None
    subject: str | None = None
    language: str | None = None
    keywords: str | None = None
    creator: str | None = None
    producer: str | None = None
    is_tagged: bool = False
    has_struct_tree: bool = False
    is_pdf_ua_identifier_present: bool = False


class CanonicalBlock(BaseModel):
    block_id: str
    page_number: int
    source: ContentSource
    bbox: BoundingBox
    text: str
    char_count: int
    alt_text: str | None = None
    confidence: float | None = None
    role: CanonicalRole = CanonicalRole.text
    font_size: float | None = None
    font_name: str | None = None
    font_flags: int | None = None


class CanonicalCell(BaseModel):
    bbox: BoundingBox
    role: CanonicalRole  # table_header or table_data
    rowspan: int = 1
    colspan: int = 1
    block_ids: list[str] = Field(default_factory=list)


class CanonicalRow(BaseModel):
    cells: list[CanonicalCell] = Field(default_factory=list)


class CanonicalTable(BaseModel):
    table_id: str
    bbox: BoundingBox
    rows: list[CanonicalRow] = Field(default_factory=list)
    caption: str | None = None


class CanonicalForm(BaseModel):
    field_id: str
    page_number: int = 1
    name: str
    tooltip: str | None = None
    bbox: BoundingBox
    role: CanonicalRole = CanonicalRole.form_field


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
    tables: list[CanonicalTable] = Field(default_factory=list)
    forms: list[CanonicalForm] = Field(default_factory=list)


class CanonicalDocument(BaseModel):
    document_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    source_type: DocumentSourceType
    page_count: int
    total_block_count: int
    total_text_char_count: int
    ocr_page_count: int
    metadata: CanonicalMetadata = Field(default_factory=CanonicalMetadata)
    pages: list[CanonicalPage]

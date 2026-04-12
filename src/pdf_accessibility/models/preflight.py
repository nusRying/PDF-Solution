from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from pdf_accessibility.models.documents import utc_now


class ProcessingLane(str, Enum):
    fast = "fast"
    standard = "standard"
    heavy = "heavy"
    manual = "manual"


class PreflightClass(str, Enum):
    tagged_digital_born = "tagged-digital-born"
    untagged_digital_born = "untagged-digital-born"
    scanned_image_only = "scanned-image-only"
    hybrid_ocr_layer_present = "hybrid-ocr-layer-present"
    form_heavy = "form-heavy"
    table_heavy = "table-heavy"
    multilingual_or_rtl = "multilingual-or-rtl"
    oversized_or_complex_layout = "oversized-or-complex-layout"


class PreflightSignals(BaseModel):
    is_tagged_pdf: bool = False
    has_forms: bool = False
    form_field_count: int = 0
    detected_language: str | None = None
    rtl_detected: bool = False
    multi_column_page_count: int = 0
    estimated_table_page_count: int = 0
    average_block_count_per_page: float = 0.0
    max_block_count_on_page: int = 0


class PreflightArtifact(BaseModel):
    document_id: str
    generated_at: datetime = Field(default_factory=utc_now)
    classifier_version: str = "0.1.0"
    lane: ProcessingLane
    classes: list[PreflightClass] = Field(default_factory=list)
    signals: PreflightSignals = Field(default_factory=PreflightSignals)
    notes: list[str] = Field(default_factory=list)

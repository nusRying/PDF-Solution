from __future__ import annotations

import math
import re
from pathlib import Path

from pypdf import PdfReader

from pdf_accessibility.models.documents import DocumentSourceType, ParserArtifact
from pdf_accessibility.models.preflight import (
    PreflightArtifact,
    PreflightClass,
    PreflightSignals,
    ProcessingLane,
)

_RTL_PATTERN = re.compile(r"[\u0590-\u05FF\u0600-\u06FF\u0750-\u08FF\uFB1D-\uFDFD\uFE70-\uFEFC]")


def _normalize_pdf_lang(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).replace("/", "").strip().lower()
    return normalized or None


def _extract_pdf_signals(pdf_path: Path) -> tuple[bool, int, str | None, list[str]]:
    notes: list[str] = []
    is_tagged_pdf = False
    form_field_count = 0
    detected_language: str | None = None

    try:
        reader = PdfReader(str(pdf_path))
        trailer_root = reader.trailer.get("/Root")
        if trailer_root is not None:
            is_tagged_pdf = trailer_root.get("/StructTreeRoot") is not None
            detected_language = _normalize_pdf_lang(trailer_root.get("/Lang"))
            acro_form = trailer_root.get("/AcroForm")
            if acro_form is not None:
                fields = acro_form.get("/Fields")
                form_field_count = len(fields) if fields is not None else 0
    except Exception as exc:
        notes.append(f"PDF metadata preflight degraded: {exc}")

    return is_tagged_pdf, form_field_count, detected_language, notes


def _looks_like_table_line(line: str) -> bool:
    normalized = line.strip()
    if not normalized:
        return False
    if "|" in normalized or "\t" in normalized:
        return True

    chunks = [chunk for chunk in re.split(r"\s{2,}", normalized) if chunk]
    if len(chunks) < 3:
        return False
    compact_chunks = sum(1 for chunk in chunks if len(chunk) <= 24)
    return compact_chunks >= 2


def _count_table_pages(parser_artifact: ParserArtifact) -> int:
    table_pages = 0
    for page in parser_artifact.pages:
        table_line_count = 0
        for block in page.text_blocks:
            for line in block.text.splitlines():
                if _looks_like_table_line(line):
                    table_line_count += 1
                if table_line_count >= 2:
                    table_pages += 1
                    break
            if table_line_count >= 2:
                break
    return table_pages


def _count_multi_column_pages(parser_artifact: ParserArtifact) -> int:
    multi_column_pages = 0
    for page in parser_artifact.pages:
        if page.width <= 0:
            continue
        left_column_blocks = 0
        right_column_blocks = 0
        for block in page.text_blocks:
            block_width = block.bbox.x1 - block.bbox.x0
            if block_width <= 0 or block_width >= page.width * 0.7:
                continue
            center_x = (block.bbox.x0 + block.bbox.x1) / 2
            if center_x < page.width * 0.47:
                left_column_blocks += 1
            elif center_x > page.width * 0.53:
                right_column_blocks += 1
        if left_column_blocks >= 2 and right_column_blocks >= 2:
            multi_column_pages += 1
    return multi_column_pages


def _sample_text(parser_artifact: ParserArtifact, max_characters: int = 24000) -> str:
    segments: list[str] = []
    current_length = 0
    for page in parser_artifact.pages:
        for block in page.text_blocks:
            text = block.text.strip()
            if not text:
                continue
            remaining = max_characters - current_length
            if remaining <= 0:
                return "\n".join(segments)
            snippet = text[:remaining]
            segments.append(snippet)
            current_length += len(snippet)
    return "\n".join(segments)


def _contains_multilingual_signal(sample_text: str, detected_language: str | None) -> tuple[bool, bool]:
    rtl_detected = bool(_RTL_PATTERN.search(sample_text))

    multilingual_hint = False
    if detected_language and not detected_language.startswith("en"):
        multilingual_hint = True

    alpha_chars = [character for character in sample_text if character.isalpha()]
    if alpha_chars:
        ascii_chars = sum(1 for character in alpha_chars if ord(character) < 128)
        non_ascii_ratio = 1 - (ascii_chars / len(alpha_chars))
        if non_ascii_ratio >= 0.25:
            multilingual_hint = True

    return rtl_detected, multilingual_hint


def _classify_lane(classes: list[PreflightClass]) -> ProcessingLane:
    if not classes:
        return ProcessingLane.manual

    heavy_classes = {
        PreflightClass.scanned_image_only,
        PreflightClass.hybrid_ocr_layer_present,
        PreflightClass.form_heavy,
        PreflightClass.table_heavy,
        PreflightClass.multilingual_or_rtl,
        PreflightClass.oversized_or_complex_layout,
    }
    if any(item in heavy_classes for item in classes):
        return ProcessingLane.heavy
    if PreflightClass.tagged_digital_born in classes:
        return ProcessingLane.fast
    return ProcessingLane.standard


def classify_preflight(document_id: str, pdf_path: Path, parser_artifact: ParserArtifact) -> PreflightArtifact:
    page_count = max(1, parser_artifact.page_count)
    source_type = parser_artifact.source_type
    classes: list[PreflightClass] = []
    notes: list[str] = []

    is_tagged_pdf, form_field_count, detected_language, metadata_notes = _extract_pdf_signals(pdf_path)
    notes.extend(metadata_notes)

    table_page_count = _count_table_pages(parser_artifact)
    multi_column_page_count = _count_multi_column_pages(parser_artifact)
    average_block_count = (
        round(sum(page.block_count for page in parser_artifact.pages) / page_count, 2)
        if parser_artifact.pages
        else 0.0
    )
    max_block_count = max((page.block_count for page in parser_artifact.pages), default=0)
    sample_text = _sample_text(parser_artifact)
    rtl_detected, multilingual_hint = _contains_multilingual_signal(sample_text, detected_language)

    if source_type == DocumentSourceType.digital:
        if is_tagged_pdf:
            classes.append(PreflightClass.tagged_digital_born)
        else:
            classes.append(PreflightClass.untagged_digital_born)
    elif source_type in {DocumentSourceType.scanned, DocumentSourceType.image_only}:
        classes.append(PreflightClass.scanned_image_only)
    elif source_type == DocumentSourceType.hybrid:
        classes.append(PreflightClass.hybrid_ocr_layer_present)

    if form_field_count >= 10:
        classes.append(PreflightClass.form_heavy)

    table_threshold = max(2, math.ceil(page_count * 0.2))
    if table_page_count >= table_threshold:
        classes.append(PreflightClass.table_heavy)

    if multilingual_hint or rtl_detected:
        classes.append(PreflightClass.multilingual_or_rtl)

    complex_layout_threshold = max(2, math.ceil(page_count * 0.25))
    if (
        parser_artifact.page_count >= 120
        or max_block_count >= 80
        or average_block_count >= 22
        or multi_column_page_count >= complex_layout_threshold
    ):
        classes.append(PreflightClass.oversized_or_complex_layout)

    lane = _classify_lane(classes)
    if lane == ProcessingLane.manual and source_type == DocumentSourceType.unknown:
        notes.append("Source type could not be classified from parser output.")

    return PreflightArtifact(
        document_id=document_id,
        lane=lane,
        classes=classes,
        signals=PreflightSignals(
            is_tagged_pdf=is_tagged_pdf,
            has_forms=form_field_count > 0,
            form_field_count=form_field_count,
            detected_language=detected_language,
            rtl_detected=rtl_detected,
            multi_column_page_count=multi_column_page_count,
            estimated_table_page_count=table_page_count,
            average_block_count_per_page=average_block_count,
            max_block_count_on_page=max_block_count,
        ),
        notes=notes,
    )

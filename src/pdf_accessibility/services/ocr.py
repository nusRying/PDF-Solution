from __future__ import annotations

import io
import os
from collections import defaultdict
from pathlib import Path

import fitz
import pytesseract
from PIL import Image
from pytesseract import Output

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.documents import BoundingBox, ParserArtifact
from pdf_accessibility.models.ocr import OCRArtifact, OCRPageResult, OCRTextLine
from pdf_accessibility.services.runtime_checks import resolve_executable, resolve_tessdata_prefix


def _configure_tesseract(settings: Settings) -> tuple[str, Path]:
    tesseract_exe = resolve_executable("tesseract", settings.tesseract_exe)
    tessdata_prefix = resolve_tessdata_prefix(settings, tesseract_exe)
    if not tesseract_exe:
        raise RuntimeError("Tesseract executable could not be resolved.")
    if tessdata_prefix is None:
        raise RuntimeError(
            f"No tessdata directory with {settings.default_ocr_language}.traineddata could be resolved."
        )

    pytesseract.pytesseract.tesseract_cmd = tesseract_exe
    os.environ["TESSDATA_PREFIX"] = str(tessdata_prefix)
    return tesseract_exe, tessdata_prefix


def _safe_confidence(value: str | int | float) -> float | None:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return None
    return None if confidence < 0 else confidence


def _build_ocr_lines(
    page_data: dict,
    x_scale: float,
    y_scale: float,
) -> list[OCRTextLine]:
    grouped: dict[tuple[int, int, int], list[dict]] = defaultdict(list)

    for index, text in enumerate(page_data["text"]):
        normalized_text = str(text).strip()
        confidence = _safe_confidence(page_data["conf"][index])
        if not normalized_text or confidence is None:
            continue

        key = (
            int(page_data["block_num"][index]),
            int(page_data["par_num"][index]),
            int(page_data["line_num"][index]),
        )
        grouped[key].append(
            {
                "text": normalized_text,
                "confidence": confidence,
                "left": int(page_data["left"][index]),
                "top": int(page_data["top"][index]),
                "width": int(page_data["width"][index]),
                "height": int(page_data["height"][index]),
            }
        )

    lines: list[OCRTextLine] = []
    for line_number, items in enumerate(grouped.values(), start=1):
        left = min(item["left"] for item in items)
        top = min(item["top"] for item in items)
        right = max(item["left"] + item["width"] for item in items)
        bottom = max(item["top"] + item["height"] for item in items)
        text = " ".join(item["text"] for item in items)
        confidence = sum(item["confidence"] for item in items) / len(items)

        lines.append(
            OCRTextLine(
                line_number=line_number,
                bbox=BoundingBox(
                    x0=round(left / x_scale, 2),
                    y0=round(top / y_scale, 2),
                    x1=round(right / x_scale, 2),
                    y1=round(bottom / y_scale, 2),
                ),
                text=text,
                confidence=round(confidence, 2),
            )
        )

    return lines


def run_tesseract_ocr(
    document_id: str,
    pdf_path: Path,
    parser_artifact: ParserArtifact,
    settings: Settings,
) -> OCRArtifact:
    pages_to_ocr = [page for page in parser_artifact.pages if not page.has_text]
    if not pages_to_ocr:
        return OCRArtifact(
            document_id=document_id,
            engine="tesseract",
            engine_version=None,
            language=settings.default_ocr_language,
            attempted_page_count=0,
            completed_page_count=0,
            pages=[],
            errors=[],
        )

    _, _ = _configure_tesseract(settings)

    results: list[OCRPageResult] = []
    errors: list[str] = []
    completed = 0

    with fitz.open(pdf_path) as document:
        for page_summary in pages_to_ocr:
            page = document.load_page(page_summary.page_number - 1)
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(io.BytesIO(pixmap.tobytes("png")))
            x_scale = pixmap.width / page.rect.width if page.rect.width else 1.0
            y_scale = pixmap.height / page.rect.height if page.rect.height else 1.0

            try:
                page_data = pytesseract.image_to_data(
                    image,
                    lang=settings.default_ocr_language,
                    config="--psm 6",
                    output_type=Output.DICT,
                )
                lines = _build_ocr_lines(page_data=page_data, x_scale=x_scale, y_scale=y_scale)
                average_confidence = (
                    round(sum(line.confidence or 0 for line in lines) / len(lines), 2)
                    if lines
                    else None
                )
                results.append(
                    OCRPageResult(
                        page_number=page_summary.page_number,
                        width=page_summary.width,
                        height=page_summary.height,
                        line_count=len(lines),
                        text_char_count=sum(len(line.text) for line in lines),
                        average_confidence=average_confidence,
                        lines=lines,
                    )
                )
                completed += 1
            except Exception as exc:  # pragma: no cover - defensive fallback
                error_text = f"page {page_summary.page_number}: {exc}"
                errors.append(error_text)
                results.append(
                    OCRPageResult(
                        page_number=page_summary.page_number,
                        width=page_summary.width,
                        height=page_summary.height,
                        line_count=0,
                        text_char_count=0,
                        lines=[],
                        error=error_text,
                    )
                )

    return OCRArtifact(
        document_id=document_id,
        engine="tesseract",
        engine_version=str(pytesseract.get_tesseract_version()),
        language=settings.default_ocr_language,
        attempted_page_count=len(pages_to_ocr),
        completed_page_count=completed,
        pages=results,
        errors=errors,
    )

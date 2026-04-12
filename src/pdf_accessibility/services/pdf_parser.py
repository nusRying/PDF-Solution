from __future__ import annotations

from collections import Counter
from pathlib import Path

import fitz
from pypdf import PdfReader

from pdf_accessibility.models.documents import (
    BoundingBox,
    DocumentSourceType,
    ParserArtifact,
    ParserDocumentMetadata,
    ParserPageSummary,
    ParserTextBlock,
)


def _clean_metadata_value(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _classify_source_type(
    page_count: int,
    text_page_count: int,
    image_page_count: int,
) -> DocumentSourceType:
    if page_count == 0:
        return DocumentSourceType.unknown
    if text_page_count == 0 and image_page_count > 0:
        return DocumentSourceType.scanned
    if text_page_count == page_count and image_page_count == 0:
        return DocumentSourceType.digital
    if text_page_count > 0 and image_page_count > 0:
        return DocumentSourceType.hybrid
    if text_page_count == 0:
        return DocumentSourceType.image_only
    return DocumentSourceType.digital


def parse_pdf(document_id: str, pdf_path: Path) -> ParserArtifact:
    reader = PdfReader(str(pdf_path))
    metadata = reader.metadata or {}

    with fitz.open(pdf_path) as document:
        pages: list[ParserPageSummary] = []
        text_page_count = 0
        image_page_count = 0

        for page_index, page in enumerate(document, start=1):
            page_text = page.get_text("text")
            page_dict = page.get_text("dict")
            images = page.get_images(full=True)
            has_text = bool(page_text.strip())
            if has_text:
                text_page_count += 1
            if images:
                image_page_count += 1

            text_blocks: list[ParserTextBlock] = []
            for block_number, block in enumerate(page_dict.get("blocks", []), start=1):
                if block.get("type") != 0:  # Only process text blocks
                    continue

                bbox = block.get("bbox")
                block_text_parts = []
                font_sizes = []
                font_names = []
                font_flags = []

                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        span_text = span.get("text", "").replace("\x00", "")
                        if span_text.strip():
                            block_text_parts.append(span_text)
                            font_sizes.append(span.get("size"))
                            font_names.append(span.get("font"))
                            font_flags.append(span.get("flags"))

                normalized_text = " ".join(block_text_parts).strip()
                if not normalized_text:
                    continue

                # Aggregate font metadata (most frequent)
                most_common_size = (
                    Counter(font_sizes).most_common(1)[0][0] if font_sizes else None
                )
                most_common_name = (
                    Counter(font_names).most_common(1)[0][0] if font_names else None
                )
                most_common_flags = (
                    Counter(font_flags).most_common(1)[0][0] if font_flags else None
                )

                text_blocks.append(
                    ParserTextBlock(
                        block_number=block_number,
                        bbox=BoundingBox(
                            x0=round(float(bbox[0]), 2),
                            y0=round(float(bbox[1]), 2),
                            x1=round(float(bbox[2]), 2),
                            y1=round(float(bbox[3]), 2),
                        ),
                        text=normalized_text,
                        char_count=len(normalized_text),
                        font_size=most_common_size,
                        font_name=most_common_name,
                        font_flags=most_common_flags,
                    )
                )

            pages.append(
                ParserPageSummary(
                    page_number=page_index,
                    width=round(page.rect.width, 2),
                    height=round(page.rect.height, 2),
                    rotation=int(page.rotation),
                    block_count=len(text_blocks),
                    image_count=len(images),
                    has_text=has_text,
                    text_char_count=len(page_text),
                    text_preview=page_text.strip().replace("\x00", "")[:500],
                    text_blocks=text_blocks,
                )
            )

        source_type = _classify_source_type(
            page_count=len(document),
            text_page_count=text_page_count,
            image_page_count=image_page_count,
        )

        artifact = ParserArtifact(
            document_id=document_id,
            source_path=str(pdf_path),
            file_size_bytes=pdf_path.stat().st_size,
            page_count=len(document),
            text_page_count=text_page_count,
            image_page_count=image_page_count,
            source_type=source_type,
            metadata=ParserDocumentMetadata(
                title=_clean_metadata_value(metadata.get("/Title")),
                author=_clean_metadata_value(metadata.get("/Author")),
                subject=_clean_metadata_value(metadata.get("/Subject")),
                creator=_clean_metadata_value(metadata.get("/Creator")),
                producer=_clean_metadata_value(metadata.get("/Producer")),
                creation_date=_clean_metadata_value(metadata.get("/CreationDate")),
                modification_date=_clean_metadata_value(metadata.get("/ModDate")),
            ),
            pages=pages,
        )

    return artifact

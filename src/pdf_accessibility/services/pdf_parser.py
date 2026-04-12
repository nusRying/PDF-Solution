from __future__ import annotations

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
            blocks = page.get_text("blocks")
            images = page.get_images(full=True)
            has_text = bool(page_text.strip())
            if has_text:
                text_page_count += 1
            if images:
                image_page_count += 1

            text_blocks: list[ParserTextBlock] = []
            for block_number, block in enumerate(blocks, start=1):
                x0, y0, x1, y1, block_text, *_ = block
                normalized_text = str(block_text).replace("\x00", "").strip()
                if not normalized_text:
                    continue
                text_blocks.append(
                    ParserTextBlock(
                        block_number=block_number,
                        bbox=BoundingBox(
                            x0=round(float(x0), 2),
                            y0=round(float(y0), 2),
                            x1=round(float(x1), 2),
                            y1=round(float(y1), 2),
                        ),
                        text=normalized_text,
                        char_count=len(normalized_text),
                    )
                )

            pages.append(
                ParserPageSummary(
                    page_number=page_index,
                    width=round(page.rect.width, 2),
                    height=round(page.rect.height, 2),
                    rotation=int(page.rotation),
                    block_count=len(blocks),
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

from __future__ import annotations

from pdf_accessibility.models.canonical import CanonicalBlock, CanonicalDocument, CanonicalPage, ContentSource
from pdf_accessibility.models.documents import ParserArtifact
from pdf_accessibility.models.ocr import OCRArtifact


def build_canonical_document(
    parser_artifact: ParserArtifact,
    ocr_artifact: OCRArtifact | None,
) -> CanonicalDocument:
    ocr_page_lookup = {
        page.page_number: page for page in (ocr_artifact.pages if ocr_artifact else [])
    }

    pages: list[CanonicalPage] = []
    total_blocks = 0
    total_text_chars = 0
    ocr_page_count = 0

    for parser_page in parser_artifact.pages:
        blocks: list[CanonicalBlock] = []

        for native_block in parser_page.text_blocks:
            blocks.append(
                CanonicalBlock(
                    block_id=f"p{parser_page.page_number}-native-{native_block.block_number}",
                    page_number=parser_page.page_number,
                    source=ContentSource.native,
                    bbox=native_block.bbox,
                    text=native_block.text,
                    char_count=native_block.char_count,
                )
            )

        used_ocr = False
        ocr_page = ocr_page_lookup.get(parser_page.page_number)
        if not blocks and ocr_page and ocr_page.lines:
            used_ocr = True
            ocr_page_count += 1
            for line in ocr_page.lines:
                blocks.append(
                    CanonicalBlock(
                        block_id=f"p{parser_page.page_number}-ocr-{line.line_number}",
                        page_number=parser_page.page_number,
                        source=ContentSource.ocr,
                        bbox=line.bbox,
                        text=line.text,
                        char_count=len(line.text),
                        confidence=line.confidence,
                    )
                )

        page_text_char_count = sum(block.char_count for block in blocks)
        needs_review = not blocks or (ocr_page is not None and bool(ocr_page.error))
        page = CanonicalPage(
            page_number=parser_page.page_number,
            width=parser_page.width,
            height=parser_page.height,
            rotation=parser_page.rotation,
            block_count=len(blocks),
            text_char_count=page_text_char_count,
            has_native_text=parser_page.has_text,
            used_ocr=used_ocr,
            needs_review=needs_review,
            blocks=blocks,
        )
        pages.append(page)
        total_blocks += len(blocks)
        total_text_chars += page_text_char_count

    return CanonicalDocument(
        document_id=parser_artifact.document_id,
        source_type=parser_artifact.source_type,
        page_count=parser_artifact.page_count,
        total_block_count=total_blocks,
        total_text_char_count=total_text_chars,
        ocr_page_count=ocr_page_count,
        pages=pages,
    )

from __future__ import annotations

from pathlib import Path

from pdf_accessibility.models.canonical import (
    CanonicalBlock,
    CanonicalDocument,
    CanonicalMetadata,
    CanonicalPage,
    CanonicalRole,
    ContentSource,
)
from pdf_accessibility.models.documents import ParserArtifact
from pdf_accessibility.models.ocr import OCRArtifact
from pdf_accessibility.services.reading_order import ReadingOrderEngine
from pdf_accessibility.services.tables import TableDetectionService
from pdf_accessibility.services.forms import FormDetectionService


def _infer_role(block: CanonicalBlock) -> CanonicalRole:
    """Simple heuristic-based role inference."""
    if not block.font_size:
        return CanonicalRole.text
    
    # Heuristics based on common font sizes for headings
    # These should ideally be calibrated per document or configured in settings
    if block.font_size >= 18:
        return CanonicalRole.heading1
    if block.font_size >= 16:
        return CanonicalRole.heading2
    if block.font_size >= 14:
        return CanonicalRole.heading3
    
    # Bold text that is slightly larger than base might be H4-H6
    is_bold = bool(block.font_flags and (block.font_flags & 2))
    if is_bold:
        if block.font_size >= 12:
            return CanonicalRole.heading4
        return CanonicalRole.heading5
        
    return CanonicalRole.text


def build_canonical_document(
    parser_artifact: ParserArtifact,
    ocr_artifact: OCRArtifact | None,
) -> CanonicalDocument:
    ocr_page_lookup = {
        page.page_number: page for page in (ocr_artifact.pages if ocr_artifact else [])
    }
    
    engine = ReadingOrderEngine()
    table_service = TableDetectionService()
    form_service = FormDetectionService()
    
    # Extract forms for the whole document and group by page
    all_forms = form_service.extract_forms(parser_artifact.source_path)
    forms_by_page: dict[int, list] = {}
    for f in all_forms:
        p_num = f.page_number
        if p_num not in forms_by_page:
            forms_by_page[p_num] = []
        forms_by_page[p_num].append(f)
    
    pages: list[CanonicalPage] = []
    total_blocks = 0
    total_text_chars = 0
    ocr_page_count = 0

    for parser_page in parser_artifact.pages:
        blocks: list[CanonicalBlock] = []

        # Sort native blocks using the ReadingOrderEngine
        sorted_native_blocks = engine.sort_blocks(parser_page.text_blocks)

        for native_block in sorted_native_blocks:
            block = CanonicalBlock(
                block_id=f"p{parser_page.page_number}-native-{native_block.block_number}",
                page_number=parser_page.page_number,
                source=ContentSource.native,
                bbox=native_block.bbox,
                text=native_block.text,
                char_count=native_block.char_count,
                font_size=native_block.font_size,
                font_name=native_block.font_name,
                font_flags=native_block.font_flags,
            )
            block.role = _infer_role(block)
            blocks.append(block)

        used_ocr = False
        ocr_page = ocr_page_lookup.get(parser_page.page_number)
        if not blocks and ocr_page and ocr_page.lines:
            used_ocr = True
            ocr_page_count += 1
            # For OCR, we currently assume a simple top-to-bottom order 
            # as Tesseract usually provides blocks in a reasonable sequence.
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
                        role=CanonicalRole.text,
                    )
                )

        page_text_char_count = sum(block.char_count for block in blocks)
        needs_review = not blocks or (ocr_page is not None and bool(ocr_page.error))
        
        # Create page and then detect tables
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
            forms=forms_by_page.get(parser_page.page_number, [])
        )
        
        # Detect tables using source PDF for high accuracy
        page.tables = table_service.detect_tables(
            page, 
            pdf_path=Path(parser_artifact.source_path) if parser_artifact.source_path else None
        )
        
        pages.append(page)
        total_blocks += len(blocks)
        total_text_chars += page_text_char_count

    metadata = CanonicalMetadata(
        title=parser_artifact.metadata.title,
        author=parser_artifact.metadata.author,
        subject=parser_artifact.metadata.subject,
        creator=parser_artifact.metadata.creator,
        producer=parser_artifact.metadata.producer,
        is_tagged=parser_artifact.metadata.is_tagged,
        has_struct_tree=parser_artifact.metadata.has_struct_tree,
        is_pdf_ua_identifier_present=parser_artifact.metadata.is_pdf_ua_identifier_present,
    )

    return CanonicalDocument(
        document_id=parser_artifact.document_id,
        source_type=parser_artifact.source_type,
        page_count=parser_artifact.page_count,
        total_block_count=total_blocks,
        total_text_char_count=total_text_chars,
        ocr_page_count=ocr_page_count,
        metadata=metadata,
        pages=pages,
    )

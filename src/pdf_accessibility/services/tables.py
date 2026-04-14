from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import fitz
from pdf_accessibility.models.canonical import (
    BoundingBox,
    CanonicalCell,
    CanonicalPage,
    CanonicalRole,
    CanonicalRow,
    CanonicalTable,
)

if TYPE_CHECKING:
    from pathlib import Path


class TableDetectionService:
    """
    Advanced table detection service using PyMuPDF's built-in table finder.
    This replaces basic geometric heuristics with structural line/border analysis.
    """

    def detect_tables(self, page: CanonicalPage, pdf_path: Path | None = None) -> list[CanonicalTable]:
        """
        Detect table structures. 
        If pdf_path is provided, uses PyMuPDF's find_tables() for high accuracy.
        Otherwise, falls back to basic geometric grouping.
        """
        if not pdf_path or not pdf_path.exists():
            return self._detect_tables_heuristic(page)

        return self._detect_tables_viamupdf(page, pdf_path)

    def _detect_tables_viamupdf(self, page: CanonicalPage, pdf_path: Path) -> list[CanonicalTable]:
        tables = []
        try:
            doc = fitz.open(pdf_path)
            # fitz page numbers are 0-indexed, CanonicalPage is 1-indexed
            fitz_page = doc[page.page_number - 1]
            
            # Use fitz's sophisticated table finder
            tabs = fitz_page.find_tables()
            
            if not tabs.tables:
                doc.close()
                return self._detect_tables_heuristic(page)

            for tab in tabs:
                canonical_rows = []
                # Extract cells and map to our canonical blocks
                for row in tab.extract():
                    cells = []
                    # tab.cells provides geometric info for each cell
                    # We'll map the row's content
                    pass 
                
                # A better way is to iterate tab.rows
                for r in tab.header.external_names if hasattr(tab, 'header') else []:
                    # This is getting complex, let's use the basic cells first
                    pass

                # Implementation using tab.cells which contains Rects
                # We need to group them by row
                row_map: dict[int, list[CanonicalCell]] = {}
                for cell_info in tab.cells:
                    r_idx = cell_info[0] # row index
                    # cell_info[1] is col_idx
                    rspan = cell_info[2] # rowspan
                    cspan = cell_info[3] # colspan
                    rect = cell_info[4] # fitz.Rect
                    
                    # Find which canonical blocks intersect with this cell rect
                    intersecting_block_ids = []
                    is_header = False
                    for block in page.blocks:
                        block_rect = fitz.Rect(block.bbox.x0, block.bbox.y0, block.bbox.x1, block.bbox.y1)
                        if rect.intersects(block_rect):
                            intersecting_block_ids.append(block.block_id)
                            # Simple heuristic: if any block in cell is bold, might be header
                            # MuPDF also has tab.header info but it's per column
                            if block.font_flags and (block.font_flags & 2**4): # 2^4 is often Bold
                                is_header = True
                    
                    # Alternatively, use tab.header info if it exists
                    if hasattr(tab, "header") and tab.header:
                        # If this cell is in the header row
                        if r_idx < tab.header.row_count:
                            is_header = True

                    cell = CanonicalCell(
                        bbox=BoundingBox(x0=rect.x0, y0=rect.y0, x1=rect.x1, y1=rect.y1),
                        role=CanonicalRole.table_header if is_header else CanonicalRole.table_data,
                        rowspan=rspan,
                        colspan=cspan,
                        block_ids=intersecting_block_ids
                    )
                    if r_idx not in row_map:
                        row_map[r_idx] = []
                    row_map[r_idx].append(cell)
                
                for r_idx in sorted(row_map.keys()):
                    canonical_rows.append(CanonicalRow(cells=row_map[r_idx]))

                if canonical_rows:
                    tables.append(CanonicalTable(
                        table_id=str(uuid.uuid4()),
                        bbox=BoundingBox(x0=tab.bbox[0], y0=tab.bbox[1], x1=tab.bbox[2], y1=tab.bbox[3]),
                        rows=canonical_rows
                    ))
            doc.close()
        except Exception as e:
            # Fallback to heuristics if MuPDF fails
            return self._detect_tables_heuristic(page)
            
        return tables

    def _detect_tables_heuristic(self, page: CanonicalPage) -> list[CanonicalTable]:
        """Original heuristic logic as fallback."""
        tables = []
        rows_map = {}
        threshold = 5.0
        
        for block in page.blocks:
            if block.role == CanonicalRole.artifact:
                continue
            y_mid = (block.bbox.y0 + block.bbox.y1) / 2
            found_row = False
            for y_key in rows_map:
                if abs(y_key - y_mid) < threshold:
                    rows_map[y_key].append(block)
                    found_row = True
                    break
            if not found_row:
                rows_map[y_mid] = [block]
                
        if len(rows_map) >= 2:
            canonical_rows = []
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')
            sorted_y = sorted(rows_map.keys())
            for idx, y in enumerate(sorted_y):
                row_blocks = sorted(rows_map[y], key=lambda b: b.bbox.x0)
                cells = []
                # Simple heuristic for header: first row or bold text
                is_header_row = (idx == 0)
                
                for block in row_blocks:
                    is_header = is_header_row or (block.font_flags and (block.font_flags & 16))
                    cells.append(CanonicalCell(
                        bbox=block.bbox,
                        role=CanonicalRole.table_header if is_header else CanonicalRole.table_data,
                        block_ids=[block.block_id]
                    ))
                    min_x = min(min_x, block.bbox.x0)
                    min_y = min(min_y, block.bbox.y0)
                    max_x = max(max_x, block.bbox.x1)
                    max_y = max(max_y, block.bbox.y1)
                canonical_rows.append(CanonicalRow(cells=cells))
            if canonical_rows:
                tables.append(CanonicalTable(
                    table_id=str(uuid.uuid4()),
                    bbox=BoundingBox(x0=min_x, y0=min_y, x1=max_x, y1=max_y),
                    rows=canonical_rows
                ))
        return tables

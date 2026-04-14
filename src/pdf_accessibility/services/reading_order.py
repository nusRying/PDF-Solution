from typing import List
from pdf_accessibility.models.documents import ParserTextBlock


class ReadingOrderEngine:
    """
    Engine for reconstructing the logical reading order of document blocks,
    handling multi-column layouts.
    """

    def sort_blocks(self, blocks: List[ParserTextBlock]) -> List[ParserTextBlock]:
        if not blocks:
            return []

        # Sort all blocks by Y position first to process them top-down
        blocks_sorted_y = sorted(blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))

        # We'll group blocks into horizontal 'bands' or 'sections'
        # A section is a vertical range where the layout (columns) is consistent.
        # For simplicity, we'll use a more direct approach:
        # We use a sort key that favors columns.
        
        # If we have two blocks A and B:
        # If they don't overlap vertically, the one with lower y0 comes first.
        # If they DO overlap vertically, we need to decide if they are in different columns.
        
        # A more robust way:
        # Use a custom comparison function.
        
        from functools import cmp_to_key

        def compare_blocks(a: ParserTextBlock, b: ParserTextBlock):
            # 1. Check vertical overlap
            overlap_y = min(a.bbox.y1, b.bbox.y1) - max(a.bbox.y0, b.bbox.y0)
            height_a = a.bbox.y1 - a.bbox.y0
            height_b = b.bbox.y1 - b.bbox.y0
            
            # If significant vertical overlap, they might be in the same "row" or in different columns
            if overlap_y > 0.5 * min(height_a, height_b):
                # Significant vertical overlap -> check columns
                # If they are horizontally separated, the one on the left comes first
                # ONLY if they are part of the same logical flow (like a row in a table)
                # BUT for reading order, if they are in different columns, the entire left column
                # should come before the right column.
                
                # This comparison is hard because it's local. 
                # Reading order is global.
                pass
            
            return 0 # Default

        # Let's use the grouping approach instead.
        
        # 1. Identify columns by finding vertical strips of whitespace.
        # For now, let's use a simpler heuristic:
        # A block is in the 'left' or 'right' side of the page.
        
        mid_x = (min(b.bbox.x0 for b in blocks) + max(b.bbox.x1 for b in blocks)) / 2
        
        # This is too simple.
        
        # Back to basics:
        # 1. Sort by Y.
        # 2. Group blocks into "rows" where they have vertical overlap.
        # 3. For each row, check if it's multi-column.
        # 4. If a sequence of rows has the same column structure, group them into a section.
        
        # Actually, let's use the simple X-grouping I thought of before, 
        # but with a twist: Spanning blocks.
        
        # A block is 'spanning' if it covers more than 60% of the horizontal range of all blocks.
        all_x0 = min(b.bbox.x0 for b in blocks)
        all_x1 = max(b.bbox.x1 for b in blocks)
        total_width = all_x1 - all_x0
        
        spanning_blocks = [b for b in blocks if (b.bbox.x1 - b.bbox.x0) > 0.8 * total_width]
        other_blocks = [b for b in blocks if b not in spanning_blocks]
        
        # Now, use spanning blocks to split the page into vertical sections
        sections = []
        current_section = []
        
        # Sort all by Y
        all_sorted = sorted(blocks, key=lambda b: (b.bbox.y0, b.bbox.x0))
        
        for b in all_sorted:
            if b in spanning_blocks:
                if current_section:
                    sections.append(current_section)
                    current_section = []
                sections.append([b]) # Spanning block is its own section
            else:
                current_section.append(b)
        if current_section:
            sections.append(current_section)
            
        # For each section, if it's not a spanning block, sort by columns
        final_blocks = []
        for section in sections:
            if len(section) == 1 and section[0] in spanning_blocks:
                final_blocks.append(section[0])
            else:
                # Sort this section by columns
                # Group by horizontal overlap
                columns = []
                # Sort section blocks by X
                for b in sorted(section, key=lambda b: b.bbox.x0):
                    assigned = False
                    for col in columns:
                        col_x0 = min(cb.bbox.x0 for cb in col)
                        col_x1 = max(cb.bbox.x1 for cb in col)
                        overlap = min(b.bbox.x1, col_x1) - max(b.bbox.x0, col_x0)
                        if overlap > 0:
                            col.append(b)
                            assigned = True
                            break
                    if not assigned:
                        columns.append([b])
                
                # Sort columns by X
                columns.sort(key=lambda col: min(cb.bbox.x0 for cb in col))
                # Sort blocks within columns by Y
                for col in columns:
                    col.sort(key=lambda cb: cb.bbox.y0)
                    final_blocks.extend(col)
                    
        return final_blocks

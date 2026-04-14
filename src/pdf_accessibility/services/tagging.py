from __future__ import annotations
import pikepdf
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalRole, CanonicalBlock, CanonicalPage

ROLE_TO_TAG_MAP = {
    CanonicalRole.heading1: "/H1",
    CanonicalRole.heading2: "/H2",
    CanonicalRole.heading3: "/H3",
    CanonicalRole.heading4: "/H4",
    CanonicalRole.heading5: "/H5",
    CanonicalRole.heading6: "/H6",
    CanonicalRole.list: "/L",
    CanonicalRole.list_item: "/LI",
    CanonicalRole.table: "/Table",
    CanonicalRole.table_row: "/TR",
    CanonicalRole.table_header: "/TH",
    CanonicalRole.table_data: "/TD",
    CanonicalRole.form_field: "/Form",
    CanonicalRole.figure: "/Figure",
    CanonicalRole.caption: "/Caption",
    CanonicalRole.text: "/P",
    CanonicalRole.artifact: None,
}

class TaggingEngine:
    def map_role_to_tag(self, role: CanonicalRole | str) -> str | None:
        if isinstance(role, str):
            try:
                role = CanonicalRole(role)
            except ValueError:
                raise ValueError(f"Invalid CanonicalRole: {role}")
        
        if role not in ROLE_TO_TAG_MAP:
             raise ValueError(f"No tag mapping for role: {role}")

        return ROLE_TO_TAG_MAP[role]

    def build_struct_tree(self, pdf: pikepdf.Pdf, doc: CanonicalDocument):
        """Builds the initial Structure Tree from the CanonicalDocument."""
        if "/StructTreeRoot" in pdf.Root:
            del pdf.Root.StructTreeRoot
            
        struct_tree_root = pdf.make_indirect(pikepdf.Dictionary(
            Type=pikepdf.Name("/StructTreeRoot"),
            K=pikepdf.Array()
        ))
        pdf.Root.StructTreeRoot = struct_tree_root
        
        # Initialize ParentTree
        struct_tree_root.ParentTree = pdf.make_indirect(pikepdf.Dictionary(
            Nums=pikepdf.Array()
        ))
        
        current_list = None
        block_to_elem = {} # block_id -> StructElem
        
        for page_idx, page_data in enumerate(doc.pages):
            # Collect all taggable items on the page
            items = []
            for table in page_data.tables:
                items.append(("table", table, table.bbox))
            for form in page_data.forms:
                items.append(("form", form, form.bbox))
            for block in page_data.blocks:
                items.append(("block", block, block.bbox))
                
            # Sort items by geometric position (top-to-bottom, then left-to-right)
            # This ensures logical tagging order if items are interleaved on the page.
            items.sort(key=lambda x: (x[2].y0, x[2].x0))
            
            for item_type, item_data, _ in items:
                if item_type == "table":
                    table = item_data
                    table_tag = self.map_role_to_tag(CanonicalRole.table)
                    table_elem = pdf.make_indirect(pikepdf.Dictionary(
                        Type=pikepdf.Name("/StructElem"),
                        S=pikepdf.Name(table_tag),
                        P=struct_tree_root,
                        K=pikepdf.Array()
                    ))
                    struct_tree_root.K.append(table_elem)

                    if table.caption:
                        caption_tag = self.map_role_to_tag(CanonicalRole.caption)
                        caption_elem = pdf.make_indirect(pikepdf.Dictionary(
                            Type=pikepdf.Name("/StructElem"),
                            S=pikepdf.Name(caption_tag),
                            P=table_elem,
                            K=pikepdf.Array(),
                            Alt=table.caption
                        ))
                        table_elem.K.append(caption_elem)
                    
                    for row in table.rows:
                        row_tag = self.map_role_to_tag(CanonicalRole.table_row)
                        row_elem = pdf.make_indirect(pikepdf.Dictionary(
                            Type=pikepdf.Name("/StructElem"),
                            S=pikepdf.Name(row_tag),
                            P=table_elem,
                            K=pikepdf.Array()
                        ))
                        table_elem.K.append(row_elem)
                        
                        for cell in row.cells:
                            cell_tag = self.map_role_to_tag(cell.role)
                            cell_elem = pdf.make_indirect(pikepdf.Dictionary(
                                Type=pikepdf.Name("/StructElem"),
                                S=pikepdf.Name(cell_tag),
                                P=row_elem,
                                K=pikepdf.Array()
                            ))
                            row_elem.K.append(cell_elem)
                            
                            # Set col/rowspan attributes if needed
                            if cell.colspan > 1 or cell.rowspan > 1:
                                attr_dict = pikepdf.Dictionary(O=pikepdf.Name("/Table"))
                                if cell.colspan > 1:
                                    attr_dict.ColSpan = cell.colspan
                                if cell.rowspan > 1:
                                    attr_dict.RowSpan = cell.rowspan
                                cell_elem.A = attr_dict
                            
                            # Map constituent blocks to this cell
                            for block_id in cell.block_ids:
                                block_to_elem[block_id] = cell_elem

                elif item_type == "form":
                    form = item_data
                    form_tag = self.map_role_to_tag(CanonicalRole.form_field)
                    form_elem = pdf.make_indirect(pikepdf.Dictionary(
                        Type=pikepdf.Name("/StructElem"),
                        S=pikepdf.Name(form_tag),
                        P=struct_tree_root,
                        K=pikepdf.Array(),
                        Alt=form.tooltip or form.name
                    ))
                    struct_tree_root.K.append(form_elem)
                    
                    # Link Widget Annotation
                    pdf_page = pdf.pages[page_idx]
                    if "/Annots" in pdf_page:
                        for annot in pdf_page.Annots:
                            if annot.get("/Subtype") == "/Widget":
                                # Match by field name if available
                                if "/T" in annot and str(annot.T) == form.name:
                                    objr = pikepdf.Dictionary(
                                        Type=pikepdf.Name("/OBJR"),
                                        Obj=annot
                                    )
                                    form_elem.K.append(objr)
                                    annot.Pg = pdf_page.obj
                                    break

                elif item_type == "block":
                    block = item_data
                    # If block is already mapped to a table cell, skip
                    if block.block_id in block_to_elem:
                        continue
                        
                    tag = self.map_role_to_tag(block.role)
                    if tag is None:
                        continue
                    
                    elem = pdf.make_indirect(pikepdf.Dictionary(
                        Type=pikepdf.Name("/StructElem"),
                        S=pikepdf.Name(tag),
                        P=struct_tree_root,
                        K=pikepdf.Array()
                    ))
                    block_to_elem[block.block_id] = elem
                    
                    if block.role == CanonicalRole.list:
                        current_list = elem
                        struct_tree_root.K.append(elem)
                    elif block.role == CanonicalRole.list_item:
                        if current_list:
                            elem.P = current_list
                            if pikepdf.Name("/K") not in current_list:
                                current_list.K = pikepdf.Array()
                            current_list.K.append(elem)
                        else:
                            struct_tree_root.K.append(elem)
                    else:
                        current_list = None
                        struct_tree_root.K.append(elem)
        
        # Content marking and ParentTree population
        parent_tree_nums = struct_tree_root.ParentTree.Nums
        
        for page_idx, page_data in enumerate(doc.pages):
            pdf_page = pdf.pages[page_idx]
            mcid_map = self.mark_content_on_page(pdf, pdf_page, page_data)
            
            # Map MCIDs back to StructElems
            page_parent_array = pikepdf.Array()
            inv_map = {mcid: block_id for block_id, mcid in mcid_map.items()}
            for mcid in range(max(inv_map.keys()) + 1 if inv_map else 0):
                block_id = inv_map.get(mcid)
                if block_id and block_id in block_to_elem:
                    elem = block_to_elem[block_id]
                    page_parent_array.append(elem)
                    elem.K.append(mcid)
                    elem.Pg = pdf_page.obj
                else:
                    page_parent_array.append(pikepdf.Null())
            
            parent_tree_nums.append(page_idx)
            parent_tree_nums.append(pdf.make_indirect(page_parent_array))
            
            # Set StructParents on page
            pdf_page.StructParents = page_idx
            
        return struct_tree_root

    def mark_content_on_page(self, pdf: pikepdf.Pdf, pdf_page: pikepdf.Page, canonical_page: CanonicalPage) -> dict[str, int]:
        """
        Marks content on a page with BDC/EMC operators and MCIDs.
        Returns a map of block_id to MCID.
        """
        # Only mark blocks that are leaf nodes in the structure tree
        # Container roles like 'list' ( /L ) should not have MCIDs themselves
        leaf_roles = {
            CanonicalRole.heading1,
            CanonicalRole.heading2,
            CanonicalRole.heading3,
            CanonicalRole.heading4,
            CanonicalRole.heading5,
            CanonicalRole.heading6,
            CanonicalRole.list_item,
            CanonicalRole.text,
            CanonicalRole.caption,
            CanonicalRole.figure,
            CanonicalRole.table,
        }
        
        blocks = [b for b in canonical_page.blocks if b.role in leaf_roles]
        if not blocks:
            return {}

        mcid_map = {}
        original_contents = bytes(pdf_page.Contents)
        
        new_content = b""
        for i, block in enumerate(blocks):
            tag = self.map_role_to_tag(block.role)
            mcid = i
            mcid_map[block.block_id] = mcid
            
            # Wrap content
            new_content += f"{tag} << /MCID {mcid} >> BDC\n".encode()
            if i == 0:
                # Put all original content in the first block for now
                new_content += original_contents + b"\n"
            new_content += b"EMC\n"
            
        pdf_page.Contents = pdf.make_stream(new_content)
        return mcid_map

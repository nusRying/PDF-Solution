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
        
        current_list = None
        
        for page_data in doc.pages:
            for block in page_data.blocks:
                tag = self.map_role_to_tag(block.role)
                if tag is None:
                    continue
                
                elem = pdf.make_indirect(pikepdf.Dictionary(
                    Type=pikepdf.Name("/StructElem"),
                    S=pikepdf.Name(tag),
                    P=struct_tree_root
                ))
                
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
        
        return struct_tree_root

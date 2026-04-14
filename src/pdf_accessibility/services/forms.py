import pikepdf
from pdf_accessibility.models.canonical import CanonicalForm, BoundingBox, CanonicalRole

class FormDetectionService:
    def extract_forms(self, pdf_path: str) -> list[CanonicalForm]:
        """
        Extract AcroForm fields from the PDF using pikepdf.
        Returns a list of CanonicalForm objects for the entire document,
        resolving the page number for each field.
        """
        forms = []
        
        try:
            with pikepdf.open(pdf_path) as pdf:
                # Create a mapping of page object IDs to page numbers (1-indexed)
                page_id_to_num = {}
                for i, page in enumerate(pdf.pages):
                    page_id_to_num[page.objgen] = i + 1
                
                if "/AcroForm" not in pdf.Root:
                    return []
                
                acroform = pdf.Root["/AcroForm"]
                if "/Fields" not in acroform:
                    return []
                
                fields = acroform["/Fields"]
                
                # Recursively extract fields (handling potential nesting)
                def process_field(field):
                    if "/Kids" in field:
                        for kid in field["/Kids"]:
                            process_field(kid)
                    
                    # A field is a leaf if it has a field type (/FT) or is a widget
                    if "/FT" in field or "/Subtype" in field and field["/Subtype"] == "/Widget":
                        name = str(field.get("/T", ""))
                        tooltip = str(field.get("/TU", ""))
                        
                        # Rect is [x0, y0, x1, y1]
                        rect = field.get("/Rect")
                        if rect:
                            bbox = BoundingBox(
                                x0=float(rect[0]),
                                y0=float(rect[1]),
                                x1=float(rect[2]),
                                y1=float(rect[3])
                            )
                            
                            # Resolve page number using /P or searching
                            page_num = 1
                            if "/P" in field:
                                p_ref = field["/P"]
                                if p_ref.objgen in page_id_to_num:
                                    page_num = page_id_to_num[p_ref.objgen]
                            else:
                                # Fallback: search which page contains this widget if /P is missing
                                # This is more expensive but robust.
                                for p_num, p in enumerate(pdf.pages):
                                    if "/Annots" in p:
                                        for annot in p["/Annots"]:
                                            if annot.objgen == field.objgen:
                                                page_num = p_num + 1
                                                break
                                        else:
                                            continue
                                        break

                            form_field = CanonicalForm(
                                field_id=name or f"field_{id(field)}",
                                page_number=page_num,
                                name=name,
                                tooltip=tooltip if tooltip else None,
                                bbox=bbox,
                                role=CanonicalRole.form_field
                            )
                            forms.append(form_field)

                for field in fields:
                    process_field(field)
                    
        except Exception as e:
            # Handle error (log it)
            print(f"Error extracting forms with pikepdf: {e}")
            
        return forms

import fitz
from pdf_accessibility.models.canonical import CanonicalForm, BoundingBox, CanonicalRole

class FormDetectionService:
    def extract_forms(self, pdf_path: str) -> dict[int, list[CanonicalForm]]:
        """
        Extract form fields from the PDF using PyMuPDF's widgets.
        Returns a dictionary mapping page numbers (0-indexed) to lists of CanonicalForm objects.
        """
        forms_by_page = {}
        
        try:
            doc = fitz.open(pdf_path)
            for page_index in range(len(doc)):
                page = doc[page_index]
                page_forms = []
                
                # Get widgets (form fields)
                for widget in page.widgets():
                    # widget.rect is the bounding box
                    bbox = BoundingBox(
                        x0=widget.rect.x0,
                        y0=widget.rect.y0,
                        x1=widget.rect.x1,
                        y1=widget.rect.y1
                    )
                    
                    # Extract field name and tooltip
                    # widget.field_name corresponds to 'T'
                    # widget.field_label corresponds to 'TU' (tooltip)
                    
                    form_field = CanonicalForm(
                        field_id=widget.field_name or f"field_{page_index}_{widget.xref}",
                        name=widget.field_name or "",
                        tooltip=widget.field_label,
                        bbox=bbox,
                        role=CanonicalRole.form_field
                    )
                    page_forms.append(form_field)
                
                if page_forms:
                    forms_by_page[page_index] = page_forms
            
            doc.close()
        except Exception as e:
            # Handle error (log it)
            print(f"Error extracting forms: {e}")
            
        return forms_by_page

import fitz
from pathlib import Path
from pdf_accessibility.services.file_store import get_file_store
from pdf_accessibility.core.settings import get_settings

def generate_render():
    from pdf_accessibility.services.pdf_parser import parse_pdf
    from pdf_accessibility.services.canonicalize import build_canonical_document

    pdf_path = Path("smoke_test.pdf")
    if not pdf_path.exists():
        print(f"Error: Original PDF {pdf_path} not found.")
        return

    parser_artifact = parse_pdf(pdf_path.stem, pdf_path)
    canonical = build_canonical_document(parser_artifact, None)

    doc = fitz.open(pdf_path)
    page = doc[0]
    
    # Create a copy to draw on
    img_pdf = fitz.open("pdf", doc.tobytes())
    img_page = img_pdf[0]
    
    # Draw blocks with their roles
    for block in canonical.pages[0].blocks:
        role_val = block.role.value if hasattr(block.role, 'value') else str(block.role)
        
        # Color coding: Headings (Red), Text (Blue), Tables/Forms (Purple)
        color = (1, 0, 0) # Red
        if "text" in role_val:
            color = (0, 0, 1) # Blue
        elif "table" in role_val or "form" in role_val:
            color = (0.5, 0, 0.5) # Purple
            
        rect = fitz.Rect(block.bbox.x0, block.bbox.y0, block.bbox.x1, block.bbox.y1)
        img_page.draw_rect(rect, color=color, width=1)
        
        # Label the block
        img_page.insert_text(
            (block.bbox.x0, block.bbox.y0 - 2), 
            role_val, 
            fontsize=7, 
            color=color
        )

    # Save high-res render
    pix = img_page.get_pixmap(matrix=fitz.Matrix(3, 3))
    output_path = Path("docs/images/actual_output_render.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(output_path))
    print(f"Successfully generated actual output render at {output_path}")
    
    doc.close()
    img_pdf.close()

if __name__ == "__main__":
    generate_render()

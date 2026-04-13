from __future__ import annotations

import logging
from pathlib import Path

import pikepdf
from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.services.tagging import TaggingEngine

logger = logging.getLogger(__name__)


class PdfWriterService:
    """
    Service for writing remediated structural and metadata changes back to a PDF file.
    Performs full structural tagging and PDF/UA-1 compliance marking.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.tagging_engine = TaggingEngine()

    def write_remediated_pdf(
        self,
        original_pdf_path: Path,
        output_pdf_path: Path,
        remediated_doc: CanonicalDocument,
    ) -> Path:
        """
        Applies remediation changes to the PDF and saves it to the output path.
        """
        logger.info(f"Writing remediated PDF to {output_pdf_path}")
        
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        with pikepdf.open(original_pdf_path) as pdf:
            # 1. Build Structure Tree
            self.tagging_engine.build_struct_tree(pdf, remediated_doc)

            # 2. Update Metadata
            with pdf.open_metadata() as meta:
                if remediated_doc.metadata.title:
                    meta["dc:title"] = remediated_doc.metadata.title
                if remediated_doc.metadata.author:
                    meta["dc:creator"] = [remediated_doc.metadata.author]
                if remediated_doc.metadata.language:
                    meta["dc:language"] = [remediated_doc.metadata.language]
                if remediated_doc.metadata.subject:
                    meta["dc:description"] = remediated_doc.metadata.subject
                
                # Mark as PDF/UA-1
                meta["pdfuaid:part"] = "1"

            # 3. Update Basic PDF Info Dictionary (Legacy support)
            info = pdf.docinfo
            if remediated_doc.metadata.title:
                info.Title = remediated_doc.metadata.title
            if remediated_doc.metadata.author:
                info.Author = remediated_doc.metadata.author
            if remediated_doc.metadata.subject:
                info.Subject = remediated_doc.metadata.subject

            # 4. Set MarkInfo and Document Language
            if "/MarkInfo" not in pdf.Root:
                pdf.Root.MarkInfo = pikepdf.Dictionary(Marked=True)
            else:
                pdf.Root.MarkInfo.Marked = True
            
            if remediated_doc.metadata.language:
                pdf.Root.Lang = remediated_doc.metadata.language
            elif not hasattr(pdf.Root, "Lang"):
                pdf.Root.Lang = "en-US"

            # 5. Viewer Preferences (DisplayDocTitle)
            if "/ViewerPreferences" not in pdf.Root:
                pdf.Root.ViewerPreferences = pikepdf.Dictionary(DisplayDocTitle=True)
            else:
                pdf.Root.ViewerPreferences.DisplayDocTitle = True

            # 6. Set /Tabs /S on pages with forms
            for page_idx, page_data in enumerate(remediated_doc.pages):
                if page_data.forms:
                    pdf_page = pdf.pages[page_idx]
                    pdf_page.Tabs = pikepdf.Name("/S")

            pdf.save(output_pdf_path)
            
        return output_pdf_path

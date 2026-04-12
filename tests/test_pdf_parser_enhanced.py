from pathlib import Path
from unittest.mock import MagicMock, patch

from pdf_accessibility.services.pdf_parser import parse_pdf


@patch("fitz.open")
@patch("pdf_accessibility.services.pdf_parser.PdfReader")
@patch("pathlib.Path.stat")
def test_parse_pdf_extracts_font_metadata(mock_stat, mock_pdf_reader, mock_fitz_open):
    # Mock Path.stat
    mock_stat_instance = MagicMock()
    mock_stat_instance.st_size = 1024
    mock_stat.return_value = mock_stat_instance

    # Mock PyPDF2 PdfReader
    mock_reader_instance = MagicMock()
    mock_reader_instance.metadata = {"/Title": "Test Doc"}
    mock_pdf_reader.return_value = mock_reader_instance

    # Mock fitz Document
    mock_doc = MagicMock()
    mock_fitz_open.return_value.__enter__.return_value = mock_doc
    mock_doc.__len__.return_value = 1

    # Mock fitz Page
    mock_page = MagicMock()
    mock_doc.__iter__.return_value = [mock_page]
    mock_page.rect.width = 595.0
    mock_page.rect.height = 842.0
    mock_page.rotation = 0
    mock_page.get_images.return_value = []
    mock_page.get_text.side_effect = lambda mode: {
        "text": "Heading\nParagraph",
        "dict": {
            "blocks": [
                {
                    "type": 0,
                    "bbox": [10, 10, 100, 30],
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Heading",
                                    "size": 18.0,
                                    "font": "Arial-Bold",
                                    "flags": 4,
                                    "bbox": [10, 10, 100, 30],
                                }
                            ]
                        }
                    ],
                },
                {
                    "type": 0,
                    "bbox": [10, 40, 100, 60],
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Paragraph",
                                    "size": 12.0,
                                    "font": "Arial",
                                    "flags": 0,
                                    "bbox": [10, 40, 100, 60],
                                }
                            ]
                        }
                    ],
                },
            ]
        },
    }.get(mode)

    artifact = parse_pdf("test-id", Path("dummy.pdf"))

    assert len(artifact.pages) == 1
    page = artifact.pages[0]
    assert len(page.text_blocks) == 2

    # Heading block
    h_block = page.text_blocks[0]
    assert h_block.text == "Heading"
    assert h_block.font_size == 18.0
    assert h_block.font_name == "Arial-Bold"
    assert h_block.font_flags == 4

    # Paragraph block
    p_block = page.text_blocks[1]
    assert p_block.text == "Paragraph"
    assert p_block.font_size == 12.0
    assert p_block.font_name == "Arial"
    assert p_block.font_flags == 0

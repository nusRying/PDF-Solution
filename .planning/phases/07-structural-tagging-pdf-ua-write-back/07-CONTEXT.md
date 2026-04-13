# Phase 7: Structural Tagging & PDF/UA Write-back Context

## Objective
Generate PDF/UA-1 compliant output by implementing a full structural tagging engine and PDF/UA-1 metadata write-back.

## Core Requirements
- `TaggingEngine` in `src/pdf_accessibility/services/tagging.py` using `pikepdf`.
- Map `CanonicalRole` to standard PDF tags (e.g., `heading1` -> `H1`, `text` -> `P`).
- Logical nesting for lists (`L` -> `LI`) and headings.
- Content marking using BDC/EMC and MCIDs in content streams.
- PDF/UA-1 compliant output (MarkInfo, XMP, Language).
- Update `PdfWriterService` to use `TaggingEngine`.
- Verification via `PACIntegrationService` and `pytest`.

## Decisions (D-07-XX)
- D-07-01: Use `pikepdf` for all structural edits (already a project decision, but reinforced here).
- D-07-02: Content marking will be done at the block level from `CanonicalDocument`.
- D-07-03: `PACIntegrationService` will be updated to support structural verification.

## Deferred Ideas
- Complex table tagging (multi-header, merged cells) is deferred to a specialized table remediation phase if needed.
- Automated alt-text for all figures is deferred (assumed already handled or suggested by AI).
- Footnote/Endnote structural linking.

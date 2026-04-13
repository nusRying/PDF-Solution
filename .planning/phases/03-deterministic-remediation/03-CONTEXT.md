# Phase 03: Deterministic Remediation Context

## Goal
Implement procedural rules for PDF structural repair and develop a standards-compliant PDF writer to generate accessible output.

## Objectives
- Implement `HeadingNormalizationSkill` to ensure a logical heading hierarchy (H1 -> H2 -> H3, no skipping levels).
- Implement `ListRepairSkill` to identify and group list items based on bullet/numbering patterns and indentation.
- Implement `MetadataRepairSkill` to ensure document title, author, and language (XMP) are correctly set.
- Implement `ArtifactClassificationSkill` to mark repetitive headers/footers or decorative elements as artifacts.
- Implement `PdfWriterService` in `src/pdf_accessibility/services/pdf_writer.py` (using `pikepdf` or `PyMuPDF`) for structural write-back of tags and metadata.
- Integrate these skills into the `RemediationArtifact` and audit logs.
- Verify everything with tests in the `revival` environment.

## Requirements
- **REMED-01**: Deterministic remediation skills (tagging, metadata, lists, tables).
- **CORE-04**: PDF Writer for standards-grade output delivery.
- **SKILL-03**: Traceable provenance for every skill execution.

## Strategy
1. **Vertical Slicing**:
   - Plan 01: Core structural repairs (Headings, Lists).
   - Plan 02: Metadata and Artifact classification.
   - Plan 03: Output Generation and Pipeline Integration.
2. **Deterministic Logic**:
   - Skills will use the layout-aware Canonical Document Model developed in Phase 2.
   - Every skill execution must return a `RemediationAction` for the audit log.
3. **Write-back**:
   - `PdfWriterService` will consume the remediated `CanonicalDocument` and the original PDF to produce a tagged PDF/UA-1 compliant output.
   - `pikepdf` is preferred for low-level structure tree manipulation.

## Decisions
- Use `pikepdf` for `PdfWriterService` due to its robust support for structure tree (tags) and XMP metadata manipulation.
- Skill ID format:
  - Heading Normalization: `REMED-HEAD-001`
  - List Repair: `REMED-LIST-001`
  - Metadata Repair: `REMED-META-001`
  - Artifact Classification: `REMED-ART-001`

## Open Questions (Discretion)
- How to handle tables? (Deferred to later if not explicitly asked, but Milestone 3 goal in ROADMAP mentions tables).
- The user didn't mention tables specifically in this request, so I'll stick to the 4 skills mentioned.

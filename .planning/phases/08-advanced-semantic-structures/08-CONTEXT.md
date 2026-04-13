# Phase 08 Context: Advanced Semantic Structures (Tables & Forms)

## Objective
The goal of this phase is to extend the platform's support to advanced semantic structures, specifically tables and interactive forms. This involves accurate detection of table grids, header cell identification, cell spanning (colspan/rowspan), and the extraction/remediation of form field accessibility metadata.

## User Decisions (D-01 to D-03)
- **D-01 (Table Detection)**: Implement a custom heuristic-based `TableDetectionService` that uses visual cues (bold, background shading, position) to identify grid layouts and header cells.
- **D-02 (Form Extraction)**: Use `pikepdf` to extract AcroForm fields and their current metadata (Name, Tooltip).
- **D-03 (Nested Tagging)**: Update the `TaggingEngine` to support recursive structure generation for `/Table` (TR, TH, TD) and `/Form`.

## Deferred Ideas
- AI-based table parsing (using LayoutLM/Donut) is deferred for now; stick to deterministic/heuristic methods first.
- Support for complex forms with custom widgets (not AcroForms) is deferred.

## the agent's Discretion
- The exact bounding-box overlap thresholds for cell grouping are at the agent's discretion during implementation.
- Choice of internal data structures for representing the grid in `TableDetectionService` is at the agent's discretion.

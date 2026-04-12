# Codebase Structure

**Analysis Date:** 2024-05-23

## Directory Layout

```
[project-root]/
├── data/                    # Local storage for all job artifacts
│   ├── intermediate/        # Intermediate JSON artifacts (parser, ocr, canonical, remediated-canonical)
│   ├── manifests/           # Metadata records for documents and jobs
│   ├── originals/           # Stored original PDF files
│   ├── reports/             # Final validation and remediation reports
│   └── output/              # Remediated PDF output files (empty in current state)
├── src/pdf_accessibility/   # Primary source code
│   ├── api/                 # FastAPI routes and server
│   ├── core/                # Global configuration, settings, and logging
│   ├── models/              # Pydantic models (data-first design)
│   ├── services/            # Business logic and pipeline components
│   └── main.py              # Application entry point
├── tests/                   # Test suite
└── pyproject.toml           # Project configuration and dependencies
```

## Directory Purposes

**`src/pdf_accessibility/api/`:**
- Purpose: Exposes the system's capabilities as a RESTful service.
- Contains: Route handlers for documents, jobs, health, and metrics.
- Key files: `routes/documents.py`, `routes/jobs.py`, `routes/health.py`.

**`src/pdf_accessibility/models/`:**
- Purpose: Defines the "Contract" for every piece of data in the system.
- Contains: Schemas for ingestion, preflight, OCR, canonical IR, validation, and remediation.
- Key files: `canonical.py`, `compliance.py`, `preflight.py`, `jobs.py`.

**`src/pdf_accessibility/services/`:**
- Purpose: Implements the "Work" of the platform.
- Contains: Individual pipeline components (Parser, OCR, etc.) and the ingestion orchestrator.
- Key files: `ingestion.py` (Orchestrator), `pdf_parser.py`, `lane_policy.py`, `remediation.py`, `validation.py`.

**`src/pdf_accessibility/core/`:**
- Purpose: Infrastructure and cross-cutting concerns.
- Contains: Environment variable mapping, directory setup, and telemetry recorders.
- Key files: `settings.py`, `logging.py`.

**`data/`:**
- Purpose: Local development and testing storage for artifacts.
- Contains: File-based persistence that mimics a production object store/DB.

## Key File Locations

**Entry Points:**
- `src/pdf_accessibility/main.py`: The FastAPI application entry point.
- `src/pdf_accessibility/services/ingestion.py`: The core pipeline orchestration entry point (`process_ingest_job`).

**Configuration:**
- `src/pdf_accessibility/core/settings.py`: The single source of truth for app configuration.

**Core Logic (Canonical Model):**
- `src/pdf_accessibility/models/canonical.py`: The definition of the central Intermediate Representation.
- `src/pdf_accessibility/services/canonicalize.py`: The logic for building the canonical model from extraction outputs.

**Testing:**
- `tests/`: Basic unit and integration tests (mostly empty in current state).

## Naming Conventions

**Files:**
- snake_case: `pdf_parser.py`, `lane_policy.py`.

**Directories:**
- snake_case: `pdf_accessibility/`, `api/`, `models/`.

## Where to Add New Code

**New Processing "Skill" (Rule):**
- Currently added procedurally to `services/remediation.py` or `services/validation.py`.
- Future recommended location: `src/pdf_accessibility/skills/` (new directory for rule classes).

**New Compliance Standard:**
- Add to the `ComplianceStandard` Enum in `src/pdf_accessibility/models/compliance.py`.
- Define a new `ProfileDefinition` in `src/pdf_accessibility/models/compliance.py`.

**New Extraction Component (e.g., Layout Engine):**
- Implementation: `src/pdf_accessibility/services/layout.py`.
- Model: `src/pdf_accessibility/models/layout.py`.
- Integrate into `process_ingest_job` in `src/pdf_accessibility/services/ingestion.py`.

## Special Directories

**`src/pdf_accessibility/__pycache__/`:**
- Purpose: Python bytecode cache.
- Generated: Yes.
- Committed: No.

**`.pytest_cache/`:**
- Purpose: Pytest configuration and state.
- Generated: Yes.
- Committed: No.

---

*Structure analysis: 2024-05-23*

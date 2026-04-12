# Architecture

**Analysis Date:** 2024-05-23

## Pattern Overview

**Overall:** Pipeline-based Asynchronous Processing (Orchestrator Pattern)

**Key Characteristics:**
- **Immutable Artifacts**: Each stage produces a new artifact (JSON), which is persisted for audit and replay.
- **Canonical Representation**: A unified `CanonicalDocument` model acts as the central interface between extraction (Parser/OCR) and remediation/validation.
- **Profile-Driven Execution**: `ProcessingLane` and `ComplianceProfile` control the behavior and rigor of the pipeline.

## Layers

**API Layer:**
- Purpose: Provides REST endpoints for job management and artifact retrieval.
- Location: `src/pdf_accessibility/api/`
- Contains: FastAPI routes, request/response schemas.
- Depends on: Service Layer, Model Layer.
- Used by: External clients (CLI, Web UI).

**Service Layer:**
- Purpose: Implements business logic and orchestrates the processing pipeline.
- Location: `src/pdf_accessibility/services/`
- Contains: Ingestion orchestrator, PDF parser, OCR adapters, canonicalization, remediation, and validation logic.
- Depends on: Model Layer, Core Configuration.
- Used by: API Layer.

**Model Layer:**
- Purpose: Defines the domain entities and the schemas for all intermediate artifacts.
- Location: `src/pdf_accessibility/models/`
- Contains: Pydantic models for `JobRecord`, `CanonicalDocument`, `PreflightArtifact`, `ValidationArtifact`, etc.
- Depends on: None.
- Used by: Service Layer, API Layer.

**Core Configuration:**
- Purpose: Global settings, logging, and environment management.
- Location: `src/pdf_accessibility/core/`
- Contains: `Settings` class (Pydantic-settings), logging configuration.
- Depends on: None.
- Used by: All layers.

## Data Flow

**Ingestion & Processing Flow:**

1. **Ingest**: `POST /documents` stores the PDF and creates a `JobRecord` in `PENDING` state.
2. **Parse**: `pdf_parser.py` extracts raw PDF objects, fonts, and metadata into a `ParserArtifact`.
3. **Preflight**: `preflight.py` analyzes the parser output to classify the document and assign a `ProcessingLane`.
4. **Lane Policy**: `lane_policy.py` resolves the `ProcessingLane` into an execution policy (e.g., skip OCR for "fast" lane).
5. **OCR (Optional)**: `ocr.py` runs Tesseract on pages identified by the lane policy as needing enrichment.
6. **Canonicalize**: `canonicalize.py` merges native text and OCR results into a single `CanonicalDocument`.
7. **Remediate**: `remediation.py` applies deterministic fixes (e.g., whitespace normalization) to the canonical model.
8. **Validate**: `validation.py` runs checks against the remediated model based on the `ComplianceProfile`.
9. **Persist**: All artifacts and the final `JobRecord` are saved to the `FileStore`.

**State Management:**
- `JobRecord` (`src/pdf_accessibility/models/jobs.py`) tracks the `JobStatus` and current `JobStage`.
- `FileStore` (`src/pdf_accessibility/services/file_store.py`) manages the persistence of JSON artifacts to disk.

## Key Abstractions

**CanonicalDocument:**
- Purpose: The "Source of Truth" for document content after extraction and enrichment.
- Examples: `src/pdf_accessibility/models/canonical.py`
- Pattern: Intermediate Representation (IR).

**ProcessingLane:**
- Purpose: Defines the **"How"** of processing—resource allocation, speed vs. quality tradeoffs.
- Examples: `src/pdf_accessibility/models/preflight.py`, `src/pdf_accessibility/services/lane_policy.py`
- Pattern: Strategy Pattern (Execution Policy).

**ComplianceProfile:**
- Purpose: Defines the **"What"** of processing—which standards and rules apply.
- Examples: `src/pdf_accessibility/models/compliance.py`
- Pattern: Policy-Based Configuration.

## Entry Points

**API Server:**
- Location: `src/pdf_accessibility/main.py`
- Triggers: HTTP requests.
- Responsibilities: Server initialization, route registration, middleware configuration.

**Ingest Orchestrator:**
- Location: `src/pdf_accessibility/services/ingestion.py`
- Triggers: API calls.
- Responsibilities: Coordinating the multi-stage pipeline, error handling, and telemetry recording.

## Error Handling

**Strategy:** Fail-fast with detailed audit events.

**Patterns:**
- **Job Events**: Every stage transition or failure is logged in the `JobRecord.stage_events` list.
- **Exception Wrapping**: The orchestrator catches exceptions and updates the `JobRecord` status to `FAILED` with the error message.

## Profiles and Skills Integration (Current State)

Currently, "skills" (remediation and validation rules) are loosely integrated with profiles:
- **ComplianceProfile** is passed to the validation service but rules are mostly hardcoded.
- **ProcessingLane** determines the `OCRMode` and whether `manual_review_required` is set, which impacts both remediation and validation.
- **Rules** are currently implemented as procedural loops in `services/remediation.py` and `services/validation.py`.

## Future Integration Strategy (Suggestions)

1. **Rule Registry**: Implement a central registry for all `ValidationRule` and `RemediationRule` classes.
2. **Profile-Rule Mapping**: Update `ProfileDefinition` to explicitly list the rule IDs that should be active for each profile.
3. **Skill Abstraction**: Encapsulate logic into "Skill" objects that can be shared across services.
4. **Lane-Aware Rules**: Allow rules to have "cost" metadata so that the `ProcessingLane` can filter out expensive rules for high-throughput paths.

---

*Architecture analysis: 2024-05-23*

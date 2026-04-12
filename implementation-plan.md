# PDF Accessibility Remediation Platform Implementation Plan

## 1. Brief interpretation

The brief in `project.md` is not asking for a single OCR script or a document converter. It is asking for a production platform that:

- ingests PDFs through API, CLI, and cloud connectors
- classifies document type and processing path
- performs OCR when needed, with pluggable local and cloud engines
- parses low-level PDF internals, not just extracted text
- reconstructs logical reading order across difficult layouts
- remediates structure with deterministic rules and LLM-assisted suggestions
- validates output against PDF/UA and WCAG-oriented requirements
- produces audit logs, machine-readable reports, and review workflows
- ships as an operable system with deployment, observability, and documentation

This means we are building a document-processing platform with a compliance engine, not a model demo.

## 2. What "done" actually means

The final deliverable must produce:

- remediated PDF output
- validation reports
- WCAG EARL-style result artifacts
- document-level audit history
- human review surfaces for cases automation cannot safely resolve
- deployable services and operational runbooks

It also has explicit contractual metrics:

- auto-fix rate >= 95%
- throughput >= 30 pages/sec
- PAC pass rate >= 98%

These numbers are not implementable until we define:

- the benchmark corpus
- hardware assumptions
- supported languages and scripts
- scanned vs digital-born document mix
- what counts as an "auto-fix"
- whether PAC pass rate is measured per document, per rule, or per batch

We should treat those as milestone-0 acceptance-contract items, not leave them implicit.

## 3. Compliance baseline

We should design for a compliance profile system, because the brief mixes legal, policy, and technical standards that do not map 1:1.

Working baseline:

- Section 508: use WCAG 2.0 A/AA for non-web electronic content under the Revised 508 Standards.
- ADA Title II: the April 24, 2024 DOJ final rule for state and local government web content and mobile apps uses WCAG 2.1 AA.
- WCAG 2.1 AA: contract target for accessibility reporting and gap mapping.
- PDF/UA: technical PDF accessibility target for structure and output semantics.
- Matterhorn Protocol: operational test catalog for PDF/UA-related failure conditions.

**Profile-Rule Mapping**: To manage these standards, the system uses a `ComplianceProfile` that maps a target standard to a specific set of validation and remediation rules (skills). This ensures that a single document can be processed against different compliance targets without changing the underlying engine.

## 4. Key constraints that shape the build

1. PDF accessibility is only partly machine-verifiable.
2. Reading order, heading semantics, table semantics, artifacts, and alt text often require judgment.
3. The brief requires "all 136 Matterhorn checks", but current tooling and guidance still distinguish machine-verifiable and judgment-heavy conditions.
4. Therefore the platform must include a human-review loop with provenance, not pretend full autonomy.
5. Throughput and quality will fight each other unless the system routes documents by complexity.
6. PDF writing and structural repair are the riskiest parts of the system; this is where a strong PDF engine matters most.

## 5. Build strategy

We should build this in six layers, in this order:

1. Acceptance harness and corpus
2. Core document model and PDF parser
3. OCR/layout enrichment pipeline
4. Deterministic remediation engine (using the Skill Registry)
5. LLM-assisted remediation and review workflow
6. Validation, reporting, hardening, and deployment (using the Skill Registry)

Do not start with the UI. Do not start with the LLM. The hard part is the canonical document model plus trustworthy write-back.

## 6. Recommended architecture

### 6.1 Control plane

- `API service`: REST endpoints for upload, job status, report download, and admin operations
- `CLI`: batch submit, status polling, connector sync, and report export
- `connector services`: SharePoint, S3, Google Drive, Box, or customer-specific sources
- `job orchestrator`: queues, retries, priorities, fan-out/fan-in
- `metadata DB`: Postgres for jobs, findings, review decisions, configs, tenants
- `object storage`: originals, intermediate artifacts, rendered previews, outputs, reports
- `cache/queue`: Redis or RabbitMQ

### 6.2 Worker plane

- `document classifier`
- `PDF parser`
- `OCR adapter layer`
- `layout and reading-order engine`
- `Skill Registry`: A centralized registry for all remediation and validation "skills" (rules).
- `semantic remediation engine`: Executes skills from the registry based on the active `ComplianceProfile`.
- `PDF writer/exporter`
- `validation engine`: Executes validation skills from the registry.
- `report generator`

### 6.3 Review plane

- `review dashboard`
- `finding triage`
- `document/page preview`
- `tag tree explorer`
- `reading-order overlay`
- `AI suggestion approval/reject flow`
- `audit trail explorer`

## 7. Technology choices

### 7.1 Core implementation language

Use Python for the pipeline and orchestration layer because:

- OCR and document-AI ecosystem is strongest there
- fast iteration for parsing, ML, and adapters
- easy integration with cloud OCR and LLM providers

Use a typed boundary for the most fragile contracts:

- Pydantic or equivalent schema validation for all internal messages
- JSON schema contracts for LLM outputs

### 7.2 API and services

- FastAPI for REST API
- Postgres for metadata and review state
- Redis for queueing and caching, or RabbitMQ if delivery guarantees need stronger broker semantics
- S3-compatible object storage for binaries and artifacts

### 7.3 PDF stack

This is where we should be conservative.

Recommendation:

- use open-source tools for inspection and enrichment
- use a commercial-grade PDF SDK for structural repair and standards-grade output writing

Why:

- parsing is not the same as safe tagged-PDF reconstruction
- accessibility repair requires low-level edits to structure tree, role maps, MCIDs, annotations, XMP, language metadata, and content associations
- production write-back quality is usually where open-source-only stacks break down

Likely evaluation candidates:

- PDFix
- Apryse/PDFTron
- Datalogics
- iText
- callas-based workflows where licensing and integration permit

We should run a bakeoff before committing to the writer/repair engine.

### 7.4 OCR and document AI

Provide a unified adapter interface:

- local: Tesseract
- cloud: AWS Textract, Google Document AI, Azure AI Document Intelligence

The adapter contract should return:

- page text
- words/spans with coordinates
- line and block grouping
- table candidates
- detected language/script
- confidence scores

### 7.5 LLM layer

Use LLMs only for ambiguity, never as the sole source of structural truth.

Good uses:

- alt text generation
- heading-vs-paragraph disambiguation
- artifact-vs-meaningful figure judgment support
- table summary/help text suggestion
- remediation explanation text for reviewers

Bad uses:

- direct raw PDF edits
- unbounded reasoning without schema constraints
- silent changes to semantic structure without traceable confidence

## 8. Canonical document model

This is the center of the whole system. Everything should translate into and out of this model.

Core entities:

- document
- page
- region/block
- line
- span/token
- figure
- table
- annotation
- form field
- structure node
- artifact
- metadata record
- validation finding
- remediation action
- review decision

Core relationships:

- geometric containment
- reading-order graph
- structure-tree parent/child
- content-to-tag mapping
- tag-to-page references
- annotation-to-anchor associations
- OCR-to-native-text alignment

Without this model we cannot reliably combine OCR, parser output, LLM suggestions, and validator findings.

## 9. End-to-end processing pipeline

### 9.1 Ingestion

Input channels:

- REST API upload
- CLI batch submit
- cloud connector pull
- optional watched-folder drop for enterprise environments

At ingest, compute:

- checksum
- document fingerprint
- tenant/workspace
- source metadata
- page count
- encrypted/password-protected status
- preliminary digital-born vs scanned vs hybrid classification

### 9.2 Preflight classification

Route documents into classes:

- digital-born, already tagged
- digital-born, untagged
- scanned image-only
- hybrid OCR layer present
- form-heavy
- table-heavy
- multilingual/RTL
- oversized/complex engineering layouts

This routing is mandatory if we care about throughput.

### 9.3 Parsing and normalization

Extract and normalize:

- catalog and page tree
- structure tree
- content streams
- marked content IDs
- role map
- fonts and ToUnicode maps
- XMP metadata
- annotations and forms
- article threads if present
- page geometry and rotation

Also detect failure modes:

- broken tags
- orphaned MCIDs
- missing role mappings
- unembedded fonts
- bad Unicode extraction
- malformed annotation semantics

### 9.4 OCR and layout enrichment

For scanned or degraded documents:

- render page images
- run OCR
- recover word/line/block geometry
- detect tables, figures, headings, footnotes, marginalia
- align OCR output back to page coordinates

For digital-born documents:

- do selective OCR only when native extraction quality is low
- avoid paying OCR cost on clean text PDFs

### 9.5 Reading-order reconstruction

Build a reading-order graph using:

- existing tag order
- geometric layout
- column detection
- text baselines
- whitespace gaps
- footnote anchors
- page headers/footers repetition
- RTL/LTR language cues
- article threads where present

Hard cases requiring dedicated logic:

- two-column and three-column layouts
- sidebars and callouts
- footnotes/endnotes
- floating figures
- tables split across pages
- rotated pages
- mixed RTL/LTR pages

### 9.6 Remediation

Split remediation into deterministic passes and AI-assisted passes.

**Skill Registry Pattern**: Every remediation rule is a "skill" registered in a central registry. Skills are self-contained modules that operate on the canonical model.
- **Deterministic passes**: Skills that apply mechanical fixes (e.g., tagging repair, metadata injection) where confidence is high.
- **AI-assisted passes**: Skills that provide suggestions (e.g., alt text, heading disambiguation) for human review.

Every change must write a provenance record:

- input evidence
- rule or model used (Skill ID)
- confidence
- before/after state
- reviewer override if any

### 9.7 Output generation

Generate:

- remediated PDF
- machine-readable validation report
- WCAG EARL output
- audit log
- review summary
- optional sidecar JSON representing structure and findings

## 10. Validation engine design

The validator is a rule engine that executes validation "skills" from the Skill Registry.

### 10.1 Internal validator responsibilities

- **Skill-Based Execution**: Every validation rule is a skill in the registry.
- **Profile-Rule Mapping**: The `ComplianceProfile` determines which validation skills are executed.
- represent each validation rule as a stable rule ID (Skill ID)
- map rule IDs to Matterhorn checkpoints/failure conditions
- map applicable findings to WCAG 2.1 criteria
- classify rules as:
  - machine-pass/fail
  - machine-suspect-needs-review
  - human-review-required
- provide finding locations and remediation guidance

### 10.2 External validators for acceptance and regression

Use external tools as oracle checks in QA:

- PAC for practical market-facing conformance checks
- additional vendor/tool cross-check where licensing allows
- screen reader smoke tests on gold documents

### 10.3 Important constraint

Because some conditions remain judgment-heavy, "all 136 checks" should mean:

- all conditions represented in the rule catalog
- every condition has an execution mode: automated, assisted-review, or manual-review
- no condition is simply omitted because it is hard

That is the only credible interpretation.

## 11. Review dashboard requirements

The dashboard is part of the product, not an afterthought.

It should support:

- queue by severity, confidence, customer, and SLA
- side-by-side original vs remediated preview
- page overlay showing reading order
- logical tag tree view
- finding list with exact anchors
- approve/reject/edit AI suggestions
- alt text editor
- table/header correction workflow
- audit history per document
- rerun selected validation passes after edits
- export reviewer decisions for model and rule improvement

## 12. Performance design

To approach >= 30 pages/sec, we need routing and horizontal parallelism.

Principles:

- avoid OCR on clean digital-born PDFs
- split by page for OCR and layout stages
- keep write-back and final validation at document scope
- use worker pools by capability, not one giant worker
- cache rendered pages and reusable intermediates
- short-circuit documents that are already compliant enough

Performance tiers:

- fast lane: tagged, digital-born, low-complexity docs
- standard lane: untagged digital-born docs
- heavy lane: scanned or complex-layout docs
- manual lane: documents with high ambiguity or unsupported constructs

The benchmark must be reported per lane, not as one meaningless blended average.

## 13. Security and data governance

Required controls:

- encryption in transit and at rest
- tenant isolation
- configurable retention and purge
- PII-sensitive audit handling
- secrets management
- optional on-prem or VPC deployment mode
- model routing policy: local-only, approved-cloud-only, or disabled

For public-sector or regulated buyers, LLM usage must be able to run in:

- disabled mode
- private-endpoint mode
- local model mode

## 14. Deployment model

### 14.1 Containers

- Docker images for API, workers, UI, and scheduled connector jobs

### 14.2 Orchestration

- Kubernetes for production
- Helm charts for deployment
- autoscaling on queue depth, OCR saturation, and CPU/memory

### 14.3 Observability

- structured logs
- traces by document/job ID
- metrics by stage and rule family
- failure dashboards
- SLOs for ingest latency, processing latency, and validation latency

## 15. Testing and evaluation plan

We should treat testing as a first-class stream from week 1.

### 15.1 Gold corpus

Build a labeled corpus that includes:

- clean tagged PDFs
- common office-generated PDFs
- scans
- low-quality scans
- tables
- forms
- footnotes
- multi-column reports
- RTL documents
- mixed-language documents
- documents with annotations
- mathematically complex or chart-heavy documents

For each corpus item, store:

- expected structure traits
- expected reading order
- expected validator outcome
- manual review notes

### 15.2 Automated test layers

- unit tests for parsers and rule evaluators
- fixture-based tests for remediation passes
- contract tests for OCR/LLM adapters
- document-level regression tests
- load tests and throughput tests
- deterministic replay tests for previous failures

### 15.3 Human evaluation

- screen-reader usability review on sample sets
- accessibility expert review for ambiguous semantics
- reviewer agreement scoring on manual-check classes

## 16. Milestone plan

### Milestone 0: Contract and acceptance definition

Deliver:

- agreed compliance profile matrix (Section 508, ADA Title II, PDF/UA)
- benchmark corpus definition
- throughput hardware definition
- pass/fail rubric for auto-fix and PAC metrics
- SDK bakeoff plan

Exit criteria:

- no ambiguous acceptance metrics remain
- compliance profile schemas integrated into core models

### Milestone 1: Platform skeleton and Skill Registry Core

Deliver:

- API skeleton with Compliance Profile support
- CLI skeleton
- job orchestration with profile-based routing
- **Skill Registry Core**: Implementation of the registry infrastructure for remediation and validation rules.
- **Profile-Rule Mapping**: Logic to activate skills based on the `ComplianceProfile`.
- storage model
- auth and tenancy baseline
- observability baseline

Exit criteria:

- documents can be ingested, queued, tracked, and persisted end to end
- compliance profiles correctly drive the selection of (initially empty) skill sets

### Milestone 2: Parsing, OCR, and Rule Migration

Deliver:

- PDF parser
- document classifier
- OCR adapter layer
- canonical document model
- rendered page previews
- **Rule Migration**: Transition of first-set procedural rules (tagging, metadata) into registered "skills".
- **Validation Baseline**: First set of automated validation skills registered.

Exit criteria:

- mixed corpus can be parsed into normalized intermediate representation
- the system can execute its first set of registered skills against a parsed document

### Milestone 3: Deterministic remediation

Deliver:

- tagging repair baseline
- metadata repair
- list/table/heading repair where confidence is high
- artifact classification baseline
- first PDF writer/export path

Exit criteria:

- measurable improvement on gold corpus without reviewer intervention

### Milestone 4: Validation engine and reports

Deliver:

- internal rule catalog
- Matterhorn mapping
- WCAG mapping
- EARL output
- audit log model

Exit criteria:

- every supported finding is explainable and reportable

### Milestone 5: Review dashboard and AI assist

Deliver:

- reviewer UI
- AI suggestion pipeline
- confidence-based triage
- reviewer decision capture

Exit criteria:

- ambiguous documents can be completed through assisted review without leaving the platform

### Milestone 6: Performance and hardening

Deliver:

- worker scaling
- benchmark runs
- retry/error handling hardening
- deployment charts
- runbooks and docs

Exit criteria:

- contractual throughput and quality targets met on the agreed benchmark corpus

## 17. Success Criteria for Skill-Driven Architecture

The transition to a skill-driven architecture is successful when:

1. **Selective Activation**: A job can be submitted with a `ComplianceProfile` that activates exactly the required remediation and validation rules without code changes.
2. **Rule Isolation**: Every remediation and validation rule is a self-contained "skill" that can be tested, versioned, and updated independently of the pipeline orchestration.
3. **Traceable Provenance**: Every remediation action is linked to a specific Skill ID in the audit log, providing clear traceability back to the rule logic.
4. **Extensibility**: A new compliance rule (e.g., a specific WCAG 2.2 criterion) can be added to the platform by registering a new skill and updating the profile mapping.
5. **Observability**: Metrics can be tracked per skill, allowing identification of rules with high failure rates or high performance impact.

## 18. Staffing plan

Minimum serious team:

- principal PDF systems engineer
- backend/platform engineer
- OCR/document-AI engineer
- frontend engineer for review UI
- DevOps/SRE engineer
- accessibility QA lead with PDF/UA expertise

One person can cover more than one role early, but not all of them well for long.

## 19. Biggest risks

1. Choosing the wrong PDF write/edit stack.
2. Pretending manual-check classes can be fully automated.
3. Accepting vague benchmark metrics.
4. Ignoring multilingual and RTL cases until late.
5. Treating PAC as the whole compliance story.
6. Overusing LLMs without deterministic guards and provenance.
7. Underestimating review UX and auditability.

## 20. Recommended implementation principles

- keep LLMs advisory, not authoritative
- store every intermediate artifact needed for replay
- make every remediation pass idempotent
- separate parse, infer, repair, validate, and review concerns
- route by document complexity
- keep standards mappings versioned and configurable
- never let a model mutate PDFs directly

## 21. Immediate next actions

Before writing production code, we should do these in order:

1. Turn the brief into a signed acceptance matrix.
2. Run a PDF SDK bakeoff on 20-30 representative documents.
3. Build the canonical document model and failure corpus.
4. Implement ingest, parsing, OCR adapters, and artifact persistence.
5. Add deterministic remediation before any LLM-assisted logic.
6. Add validator and review UI once findings are anchored to the document model.

## 22. Open questions from the brief

These need answers before engineering estimates are trustworthy:

- Which cloud connectors are mandatory for v1?
- Which languages must be supported in v1?
- Is math/chem notation in scope?
- Are tagged forms required in v1?
- Are digital signatures/encryption-preserving rewrites required?
- What exact PAC/version/tooling defines the 98% target?
- What hardware and concurrency assumptions define 30 pages/sec?
- What document corpus defines the 95% auto-fix rate?
- Is on-prem deployment a hard requirement?
- What data residency constraints apply to OCR and LLM providers?

## 23. Recommended delivery posture

This should be sold and managed as:

- a phased platform build
- with explicit acceptance corpus and compliance profiles
- with hybrid automation plus reviewer workflow
- with conservative PDF engine choices
- and with performance claims validated on named hardware and named document mixes

Anything looser will create disputes at acceptance time.

## Sources used to anchor the plan

- `project.md`
- U.S. Access Board Revised 508 Standards
- ADA.gov Title II web/mobile accessibility rule materials
- W3C WCAG 2.1 Recommendation
- PDF Association PDF/UA and Matterhorn materials
- PAC guidance on Matterhorn checks and manual review limits

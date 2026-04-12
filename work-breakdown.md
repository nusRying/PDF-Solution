# Work Breakdown and Dependency Plan

## 1. Workstream model

Implementation should run as eight coordinated workstreams:

1. Acceptance and standards
2. Platform and orchestration
3. PDF core and canonical model
4. OCR and layout intelligence
5. Remediation engine
6. Validation and reporting
7. Review application
8. Operations, security, and performance

Each workstream has dependencies. They should not be staffed or sequenced as if they were independent.

## 2. Dependency graph

### Foundation dependencies

- Acceptance and standards -> all workstreams
- PDF core and canonical model -> remediation, validation, review
- Platform and orchestration -> every runtime-facing component
- Operations baseline -> every deployable service

### Midstream dependencies

- OCR and layout intelligence -> reading order, remediation quality
- Remediation engine -> validation usefulness, review usefulness
- Validation and reporting -> reviewer workflow and acceptance testing

### Late-stage dependencies

- Review application depends on:
  - canonical model
  - validation anchors
  - remediation provenance
- Performance hardening depends on:
  - stable pipeline stages
  - reproducible corpus
  - observability

## 3. Workstream details

### Workstream 1: Acceptance and standards

Goal:

- eliminate ambiguity in compliance and success criteria

Tasks:

- define compliance profiles
- define benchmark corpus
- define lane taxonomy
- define PAC acceptance method
- define auto-fix scoring method
- define out-of-scope exclusions
- define rule coverage policy

Deliverables:

- signed acceptance matrix
- corpus manifest
- standards mapping register
- rule taxonomy draft

Exit criteria:

- engineering can estimate milestones without unresolved acceptance ambiguity

### Workstream 2: Platform and orchestration

Goal:

- create the runtime shell that can ingest, queue, persist, and track processing

Tasks:

- define service boundaries
- implement REST API
- implement CLI
- implement job model
- implement queueing and retries
- implement object storage integration
- implement metadata persistence
- implement auth baseline
- implement job status and artifact retrieval

Deliverables:

- API service
- CLI
- job orchestrator
- metadata schema
- storage contract

Exit criteria:

- a document can move from ingestion to persisted artifact state through a tracked job lifecycle

### Workstream 3: PDF core and canonical model

Goal:

- create the authoritative representation of the document and its structural semantics

Tasks:

- evaluate PDF SDK candidates
- define canonical document schema
- parse page tree and content streams
- parse structure tree and role maps
- parse MCIDs and content associations
- parse annotations and forms
- extract metadata and XMP
- detect structural corruption patterns
- define versioned intermediate artifact format

Deliverables:

- PDF SDK decision memo
- canonical document schema
- parser library
- normalized intermediate artifacts

Exit criteria:

- representative documents can be converted into stable canonical form with reproducible output

### Workstream 4: OCR and layout intelligence

Goal:

- enrich documents with layout and text structure when native PDF information is incomplete

Tasks:

- define OCR adapter interface
- integrate Tesseract
- integrate at least one cloud OCR provider
- implement native-text quality heuristics
- implement selective OCR routing
- implement layout block extraction
- implement heading/table/figure candidate detection
- implement OCR/native alignment
- implement reading-order graph generation
- implement multilingual and RTL support baseline

Deliverables:

- OCR adapter layer
- layout enrichment module
- reading-order engine

Exit criteria:

- scanned and hybrid documents can be converted into aligned canonical structure with usable reading-order output

### Workstream 5: Remediation engine

Goal:

- apply structural accessibility repairs with deterministic control and reviewable provenance

Tasks:

- implement tagging bootstrap for untagged documents
- implement metadata and language repair
- implement heading normalization
- implement list repair
- implement table repair where inferable
- implement artifact classification heuristics
- implement form and annotation accessibility repair baseline
- implement PDF structural write-back
- record remediation provenance
- implement AI suggestion contracts
- integrate alt-text suggestion flow
- integrate ambiguity scoring

Deliverables:

- deterministic remediation library
- provenance recorder
- AI suggestion service
- remediated PDF writer path

Exit criteria:

- the system can generate corrected PDFs and explain what changed

### Workstream 6: Validation and reporting

Goal:

- provide explainable validation and external-tool acceptance evidence

Tasks:

- define internal rule IDs
- map rules to Matterhorn conditions
- map rules to WCAG criteria where applicable
- define rule execution modes
- implement finding anchors
- implement finding severities
- generate machine-readable report artifacts
- generate EARL-style output
- integrate PAC benchmark execution
- implement regression comparison tooling

Deliverables:

- rule catalog
- validation engine
- report generator
- PAC acceptance harness

Exit criteria:

- every reported finding has a stable identity, location, explanation, and standards mapping

### Workstream 7: Review application

Goal:

- make ambiguous cases resolvable inside the product

Tasks:

- define reviewer workflow states
- implement triage queue
- implement page/image preview
- implement tag-tree viewer
- implement reading-order overlay
- implement alt-text editing
- implement approve/reject controls for AI suggestions
- implement save and revalidate flow
- implement reviewer audit history

Deliverables:

- review UI
- reviewer workflow backend
- audit trail browser

Exit criteria:

- review-required benchmark documents can be resolved without leaving the system

### Workstream 8: Operations, security, and performance

Goal:

- make the platform operable under enterprise conditions

Tasks:

- implement structured logging
- implement tracing and metrics
- implement fault handling and retries
- implement idempotent replay
- implement tenant isolation
- implement encryption and secret handling
- implement retention controls
- implement Docker packaging
- implement Kubernetes deployment
- implement autoscaling policies
- implement load test harness
- implement lane-based benchmark dashboards

Deliverables:

- deployment artifacts
- observability stack
- security baseline
- performance benchmark reports

Exit criteria:

- system can be deployed, observed, replayed, and benchmarked repeatably

## 4. Suggested milestone-to-workstream mapping

### Milestone 0

- Workstream 1
- early Workstream 3 SDK bakeoff

### Milestone 1

- Workstream 2
- Workstream 8 baseline

### Milestone 2

- Workstream 3
- Workstream 4 foundation

### Milestone 3

- Workstream 5 deterministic core

### Milestone 4

- Workstream 6

### Milestone 5

- Workstream 7
- Workstream 5 AI-assist features

### Milestone 6

- Workstream 8 hardening
- acceptance reruns across Workstreams 3 to 7

## 5. Critical path

The actual critical path is:

1. acceptance matrix
2. PDF SDK decision
3. canonical document schema
4. parser + normalized artifacts
5. reading-order engine
6. deterministic remediation
7. structural write-back
8. internal validation anchors
9. review workflow
10. scale and acceptance benchmarks

Anything that delays steps 2 through 7 delays the whole project.

## 6. What should not happen

- building the review UI before the canonical model is stable
- integrating LLM suggestions before deterministic remediation exists
- claiming throughput before lane routing and benchmark definitions are locked
- depending on PAC alone as the validator
- finalizing the data model after starting reviewer workflows

## 7. Team allocation

### Core engineering ownership

- PDF core owner: parser, schema, structural write-back
- platform owner: API, orchestration, storage, auth
- document intelligence owner: OCR, layout, reading order
- remediation owner: deterministic rules, provenance, AI contracts
- validation owner: rule catalog, reporting, acceptance harness
- frontend owner: review UI
- operations owner: deployment, observability, security
- accessibility QA owner: corpus truth set, human review policy, acceptance testing

## 8. Execution cadence

Recommended operating rhythm:

- weekly architecture review for canonical model and rule taxonomy
- twice-weekly corpus and benchmark review
- per-milestone acceptance gates, not only feature demos
- regression benchmark run before closing every milestone

## 9. Immediate implementation package

The first concrete package to produce should be:

- acceptance matrix
- corpus manifest template
- PDF SDK bakeoff rubric
- canonical document schema draft
- service boundary ADRs

That package is the minimum viable start for engineering.

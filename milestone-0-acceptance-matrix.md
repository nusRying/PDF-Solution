# Milestone 0 Acceptance Matrix

## Purpose

This document converts the platform strategy into measurable acceptance criteria. It exists to remove ambiguity from the three contractual targets:

- auto-fix rate >= 95%
- throughput >= 30 pages/second
- PAC pass rate >= 98%

No implementation milestone should be accepted against these targets until the matrix below is agreed.

## 1. Scope of acceptance

### In scope for v1

- PDF ingestion via REST API
- CLI batch processing
- at least one cloud connector
- scanned, digital-born, and hybrid PDFs
- OCR adapter framework
- canonical document model
- deterministic remediation pipeline
- AI-assisted suggestion pipeline with review controls
- validation engine with Matterhorn/WCAG mappings
- EARL-style machine-readable reporting
- audit trail and reviewer workflow
- Docker and Kubernetes deployment artifacts

### Explicitly out of scope unless added by change control

- unsupported proprietary encrypted PDFs that cannot be legally or technically rewritten
- CAD/engineering drawings with non-document semantics
- full semantic interpretation of advanced math/chem notation
- preservation of digital signatures across structural rewrite
- handwritten document accessibility remediation
- arbitrary embedded multimedia accessibility repair

## 2. Compliance profiles

### Profile A: Section 508 mode

- baseline reporting aligned to Revised 508 treatment of electronic content
- WCAG mappings shown where applicable
- PDF/UA findings still emitted when technically relevant

### Profile B: ADA Title II / WCAG 2.1 AA mode

- reporting aligned to WCAG 2.1 AA for covered digital content
- document findings mapped to relevant WCAG criteria
- PDF/UA findings emitted as supporting technical evidence

### Profile C: PDF/UA mode

- primary output target is accessible tagged PDF conforming to the selected PDF/UA interpretation
- Matterhorn rule coverage required

### Acceptance note

The exact standards profile active during formal acceptance must be named in the test report. Mixed references without a declared profile are invalid.

## 3. Benchmark corpus definition

Acceptance must be run on a named benchmark corpus with fixed membership and versioning.

### Corpus requirements

- minimum 250 documents
- minimum 10,000 pages total
- fixed version identifier
- immutable checksums for all source documents
- labeled per document and per page where needed

### Required corpus composition

- 25% tagged digital-born, low complexity
- 20% untagged digital-born, standard business docs
- 20% scanned image-only PDFs
- 10% hybrid PDFs with OCR text layers
- 10% table-heavy PDFs
- 5% form-heavy PDFs
- 5% multilingual or RTL PDFs
- 5% footnotes, sidebars, or complex layouts

### Required corpus labels

- language/script
- page count
- source type: digital-born, scanned, hybrid
- complexity lane
- presence of tables
- presence of forms
- presence of figures
- expected manual-review class
- expected validator outcome

## 4. Hardware profile for performance acceptance

Throughput claims are invalid without hardware definition.

### Required declaration

- CPU model and core count
- RAM size
- storage class
- GPU model if used
- node count
- worker concurrency settings
- OCR provider mode: local or cloud
- LLM mode: disabled, private endpoint, or cloud

### Default performance lane reporting

- fast lane
- standard lane
- heavy lane
- manual lane
- blended corpus throughput

Acceptance must report all five. The blended number alone is insufficient.

## 5. Auto-fix rate definition

### Proposed definition

Auto-fix rate is the percentage of eligible accessibility defects in the benchmark corpus that are correctly remediated without human reviewer intervention.

### Required exclusions

Do not count toward auto-fix denominator:

- defects explicitly classified as human-judgment-required by the agreed rule catalog
- out-of-scope constructs
- documents rejected before processing for policy or technical reasons

### Required scoring method

- numerator: eligible defects correctly fixed automatically
- denominator: eligible defects identified in corpus truth set
- score reported overall and by defect family

### Required defect families

- missing/invalid tagging
- heading structure
- list semantics
- table structure
- figure/alt text
- metadata and language
- annotations/forms
- reading order

Acceptance target:

- overall auto-fix rate >= 95%
- no critical defect family below 85% without written exception

## 6. PAC pass rate definition

### Proposed definition

PAC pass rate is the percentage of benchmark documents that achieve the agreed PAC outcome after remediation.

### Required declaration

- PAC product and exact version
- command or invocation method
- enabled/disabled AI-assisted checks
- fail threshold definition
- handling for warnings vs failures

### Required reporting

- document-level pass rate
- page-weighted pass rate if applicable
- top fail reasons by frequency
- fail reasons by corpus lane

Acceptance target:

- document-level PAC pass rate >= 98%

## 7. Throughput definition

### Proposed definition

Throughput is measured as successfully completed pages per second from job acceptance into processing to final artifact generation, excluding queue wait time but including all enabled remediation and validation stages.

### Required declarations

- whether OCR is local or cloud
- whether LLM-assisted suggestions are enabled
- whether reviewer workflow is bypassed for benchmark runs
- warm-cache vs cold-cache conditions
- batch size and concurrency

Acceptance target:

- blended corpus throughput >= 30 pages/second on the agreed hardware profile

Additional requirement:

- report 95th percentile document latency by lane

## 8. Rule coverage acceptance

The platform must maintain a rule catalog with stable IDs.

### For every Matterhorn-related condition in scope, the catalog must define:

- internal rule ID
- mapped Matterhorn condition/checkpoint
- mapped WCAG criterion if applicable
- execution mode:
  - automated
  - automated with reviewer confirmation
  - manual review required
- severity
- remediation guidance

### Acceptance target

- 100% of agreed rule set represented in the catalog
- 0 silent omissions

## 9. Output artifact acceptance

For every completed document, the system must emit:

- remediated PDF
- validation report
- machine-readable report artifact
- audit log
- job metadata record

For review-required documents, the system must also emit:

- unresolved finding list
- reviewer decision trail
- rerun validation outcome after review

## 10. Audit and provenance acceptance

Every remediation action must record:

- source document ID
- page or structural location
- rule or model that produced the action
- input evidence reference
- before state
- after state
- confidence score if inferred
- reviewer override if applicable
- timestamp

Acceptance target:

- 100% of nontrivial remediation actions traceable through audit logs

## 11. Review workflow acceptance

The review system must support:

- triage queue
- page preview
- reading-order inspection
- tag-tree inspection
- alt-text editing
- approval/rejection of suggestions
- save/revalidate loop
- complete reviewer audit trail

Acceptance target:

- benchmark review-required documents can be completed inside the platform without external editing tools

## 12. Reliability acceptance

### Required nonfunctional criteria

- idempotent job replay
- retry policy for transient worker failures
- resumable processing after worker crash
- artifact persistence across restarts
- partial-failure reporting without silent data loss

### Acceptance target

- no unrecoverable data loss in fault-injection tests for agreed failure scenarios

## 13. Security and deployment acceptance

### Required controls

- authentication and authorization baseline
- tenant isolation
- encryption at rest and in transit
- secrets management
- retention and purge policy support
- configurable no-LLM mode

### Deployment artifacts required

- Dockerfiles
- Kubernetes manifests or Helm charts
- environment variable contract
- operational runbook
- observability dashboard definitions or documented metrics

## 14. Sign-off checklist

Before Milestone 1 begins, all items below must be explicitly agreed:

- [ ] Compliance profile for acceptance
- [ ] Corpus membership and version
- [ ] Hardware profile
- [ ] OCR mode for benchmarking
- [ ] LLM mode for benchmarking
- [ ] PAC version and settings
- [ ] Auto-fix denominator definition
- [ ] Lane definitions
- [ ] Out-of-scope exclusions
- [ ] Review-required rule classes
- [ ] Required deployment mode: SaaS, VPC, on-prem

## 15. Decision log

- Pending: whether v1 targets PDF/UA-1 only, or a broader PDF/UA compatibility posture
- Pending: whether PAC AI-assisted checks are enabled in formal acceptance
- Pending: whether forms and multilingual RTL are hard requirements for the first acceptance gate

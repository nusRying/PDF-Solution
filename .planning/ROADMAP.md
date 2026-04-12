# Project Roadmap

## Phases

- [x] **Phase 1: Foundation & Skill Architecture** - Platform skeleton, Skill Registry core, and Compliance Profile mapping.
- [ ] **Phase 2: Parsing & Layout Foundation** - Canonical document model, PDF parser internals, and OCR/Layout intelligence.
- [ ] **Phase 3: Deterministic Remediation** - Registration of core remediation skills and standards-grade PDF writer path.
- [ ] **Phase 4: Validation Engine** - Matterhorn and WCAG validation skills, rule catalog, and EARL reporting.
- [ ] **Phase 5: Review Dashboard & AI Assist** - Human-in-the-loop review UI and AI-assisted remediation suggestions.
- [ ] **Phase 6: Hardening & Performance** - Scalability, observability, deployment artifacts, and contractual benchmark runs.

## Phase Details

### Phase 1: Foundation & Skill Architecture
**Goal**: Establish the processing pipeline and the rule-driven architecture infrastructure.
**Depends on**: Nothing
**Requirements**: INGEST-01, INGEST-02, INGEST-03, SKILL-01, SKILL-02, OPS-01, OPS-03
**Success Criteria** (what must be TRUE):
  1. A document can be ingested via API/CLI and tracked through a job lifecycle.
  2. The Skill Registry can register and retrieve remediation/validation skills.
  3. A ComplianceProfile can selectively activate skills from the registry.
  4. Observability baseline (logs/metrics) is active for the pipeline stages.
**Plans**: 3 plans
- [x] 01-foundation-skill-architecture-01-PLAN.md — Core Skill Architecture & Registry
- [ ] 01-foundation-skill-architecture-02-PLAN.md — Initial Skills & Profile Mapping
- [ ] 01-foundation-skill-architecture-03-PLAN.md — Pipeline Integration & CLI Skeleton

### Phase 2: Parsing & Layout Foundation
**Goal**: Convert complex PDFs into a normalized canonical representation with layout awareness.
**Depends on**: Phase 1
**Requirements**: CORE-01, CORE-02, CORE-03, OCR-01, OCR-02, OCR-03
**Success Criteria** (what must be TRUE):
  1. Selected PDF SDK is integrated and can extract low-level structure (tags, MCIDs).
  2. PDFs (digital and scanned) are converted into a stable Canonical Document Model.
  3. OCR and Layout engines correctly identify tables, figures, and reading-order blocks.
**Plans**: 3 plans
- [x] 02-parsing-layout-foundation-01-PLAN.md — Model & Parser Enhancement
- [ ] 02-parsing-layout-foundation-02-PLAN.md — Reading Order & Canonicalization
- [ ] 02-parsing-layout-foundation-03-PLAN.md — Layout Validation Skills

### Phase 3: Deterministic Remediation
**Goal**: Apply high-confidence structural repairs and generate accessible PDF output.
**Depends on**: Phase 2
**Requirements**: CORE-04, REMED-01, SKILL-03
**Success Criteria** (what must be TRUE):
  1. Procedural rules for tagging and metadata are successfully migrated to the Skill Registry.
  2. The system can generate a remediated PDF with valid structure trees and role maps.
  3. Every remediation action records its Skill ID and provenance in the audit log.
**Plans**: 3 plans
- [ ] 03-deterministic-remediation-01-PLAN.md — Structural Remediation Skills
- [ ] 03-deterministic-remediation-02-PLAN.md — Content & Metadata Remediation Skills
- [ ] 03-deterministic-remediation-03-PLAN.md — PDF Writer & Integration

### Phase 4: Validation Engine
**Goal**: Provide standards-compliant validation reports mapped to Matterhorn and WCAG.
**Depends on**: Phase 3
**Requirements**: VALID-01, VALID-02, VALID-03, VALID-04
**Success Criteria** (what must be TRUE):
  1. Validation skills are executed based on the active ComplianceProfile.
  2. Findings are correctly mapped to Matterhorn checkpoints and WCAG criteria.
  3. The system emits machine-readable reports (EARL/JSON) for every job.
**Plans**: 3 plans
- [ ] 04-validation-engine-01-PLAN.md — Validation Foundation & Rule Catalog
- [ ] 04-validation-engine-02-PLAN.md — Matterhorn Protocol Coverage
- [ ] 04-validation-engine-03-PLAN.md — Machine-Readable Reporting & External Tools

### Phase 5: Review Dashboard & AI Assist
**Goal**: Enable human-in-the-loop resolution for ambiguous accessibility issues.
**Depends on**: Phase 4
**Requirements**: REVIEW-01, REVIEW-02, REVIEW-03, REMED-02
**Success Criteria** (what must be TRUE):
  1. Reviewers can triage documents and inspect tag trees/reading order.
  2. AI-assisted skills provide alt-text and heading suggestions for approval.
  3. Human decisions are captured and reflected in the final remediated output.
**Plans**: TBD
**UI hint**: yes

### Phase 6: Hardening & Performance
**Goal**: Meet contractual performance and scalability requirements for production.
**Depends on**: Phase 5
**Requirements**: OPS-02, OPS-04
**Success Criteria** (what must be TRUE):
  1. System achieves >= 30 pages/sec throughput on the benchmark corpus.
  2. Deployment is fully automated via Docker and Kubernetes (Helm).
  3. 95% auto-fix rate and 98% PAC pass rate targets are verified on the gold corpus.
**Plans**: TBD

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Skill Architecture | 1/3 | In Progress | - |
| 2. Parsing & Layout Foundation | 1/3 | In Progress | - |
| 3. Deterministic Remediation | 0/3 | Not started | - |
| 4. Validation Engine | 0/3 | Not started | - |
| 5. Review Dashboard & AI Assist | 0/1 | Not started | - |
| 6. Hardening & Performance | 0/1 | Not started | - |

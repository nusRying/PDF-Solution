# Project Roadmap

## Phases

- [x] **Phase 1: Foundation & Skill Architecture** - Platform skeleton, Skill Registry core, and Compliance Profile mapping.
- [x] **Phase 2: Parsing & Layout Foundation** - Canonical document model, PDF parser internals, and OCR/Layout intelligence.
- [x] **Phase 3: Deterministic Remediation** - Registration of core remediation skills and standards-grade PDF writer path.
- [x] **Phase 4: Validation Engine** - Matterhorn and WCAG validation skills, rule catalog, and EARL reporting.
- [x] **Phase 5: Review Dashboard & AI Assist** - Human-in-the-loop review API and AI-assisted remediation suggestions.
- [x] **Phase 6: Operations & Hardening** - Dockerization, production-ready queue, cloud storage, and performance benchmarks.
- [x] **Phase 7: Structural Tagging & PDF/UA Write-back** - Advanced structural tagging engine and PDF/UA-1 compliant output delivery.
- [ ] **Phase 8: Advanced Semantic Structures (Tables & Forms)** - Complex grid detection, header mapping, and AcroForm extraction/tagging.

## Implementation Details

### Phase 1: Foundation & Skill Architecture ✅
**Accomplishments**: 
- Implemented `SkillRegistry` for modular rule execution.
- Defined `ComplianceProfile` for Section 508, ADA, and PDF/UA mapping.
- Established asynchronous job pipeline with stage-based tracking.

### Phase 2: Parsing & Layout Foundation ✅
**Accomplishments**:
- Enhanced parser to extract font metadata (size, flags) for structural heuristics.
- Implemented `ReadingOrderEngine` for column-aware logical sorting.
- Automatic role inference engine for bootstrap semantic detection.

### Phase 3: Deterministic Remediation ✅
**Accomplishments**:
- Created skills for Heading Normalization, List Repair, and Metadata repair.
- Automated classification of artifacts (headers/footers).
- Integrated `RemediationArtifact` audit log.

### Phase 4: Validation Engine ✅
**Accomplishments**:
- Rule Catalog mapped to Matterhorn Protocol and WCAG 2.1.
- Generation of machine-readable **EARL 1.0** reports.
- Structural anchors (block IDs and bboxes) included in all findings.

### Phase 5: Review Dashboard & AI Assist ✅
**Accomplishments**:
- `AIAssistService` interface for vision-LLM integration (initial logic mocked).
- Full REST API for manual overrides (`/review/actions`).
- Human decisions correctly persisted and prioritized in remediation flow.

### Phase 6: Operations & Hardening ✅
**Accomplishments**:
- Multi-stage `Dockerfile` and `docker-compose.yml` for full stack orchestration.
- Abstract `BaseFileStore` supporting both Local and S3 (MinIO) backends.
- High-reliability retry logic for file operations.
- Throughput benchmarking tool provided in `scripts/benchmark.py`.

### Phase 7: Structural Tagging & PDF/UA Write-back ✅
**Accomplishments**:
- Custom `TaggingEngine` building valid `/StructTreeRoot` and `/ParentTree`.
- Precise content stream marking using `BDC/EMC` operators and MCIDs.
- Compliance with PDF/UA-1 via `/MarkInfo`, `/Lang`, and XMP metadata injection.

### Phase 8: Advanced Semantic Structures (Tables & Forms) 🚧
**Goal**: Implement comprehensive table and form detection and remediation.
**Requirements**: TBL-01, TBL-02, TBL-03, FRM-01, FRM-02, TAG-01, TAG-02
**Plans**: 3 plans
- [ ] 08-01-PLAN.md — Table & Form Models and Detection Services
- [ ] 08-02-PLAN.md — Table & Form Remediation Skills
- [ ] 08-03-PLAN.md — Advanced Tagging & Verification

---

## Progress Table

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Skill Architecture | 3/3 | Complete | 2026-04-12 |
| 2. Parsing & Layout Foundation | 3/3 | Complete | 2026-04-13 |
| 3. Deterministic Remediation | 3/3 | Complete | 2026-04-13 |
| 4. Validation Engine | 3/3 | Complete | 2026-04-13 |
| 5. Review Dashboard & AI Assist | 3/3 | Complete | 2026-04-13 |
| 6. Operations & Hardening | 3/3 | Complete | 2026-04-13 |
| 7. Structural Tagging & PDF/UA Write-back | 3/3 | Complete | 2026-04-13 |
| 8. Advanced Semantic Structures (Tables & Forms) | 0/3 | In Progress | - |

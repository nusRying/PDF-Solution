# Requirements

## V1 Scope

### Ingestion (INGEST)
| ID | Requirement | Status |
|----|-------------|--------|
| INGEST-01 | REST API for PDF upload and job management | Pending |
| INGEST-02 | CLI for batch processing | Pending |
| INGEST-03 | Cloud connectors (S3/SharePoint/GDrive) | Pending |

### Core Document Model (CORE)
| ID | Requirement | Status |
|----|-------------|--------|
| CORE-01 | Commercial-grade PDF SDK selection and integration | Pending |
| CORE-02 | Canonical Document Model implementation | Pending |
| CORE-03 | PDF Parser for low-level internals (structure tree, role maps) | Pending |
| CORE-04 | PDF Writer for standards-grade output delivery | Pending |

### OCR & Layout (OCR)
| ID | Requirement | Status |
|----|-------------|--------|
| OCR-01 | OCR Adapter framework (Tesseract + Cloud adapters) | Pending |
| OCR-02 | Layout intelligence (block extraction, table/figure detection) | Pending |
| OCR-03 | Reading-order reconstruction graph | Pending |

### Skill Registry & Architecture (SKILL)
| ID | Requirement | Status |
|----|-------------|--------|
| SKILL-01 | Centralized Skill Registry for remediation and validation rules | Pending |
| SKILL-02 | Profile-Rule Mapping (ComplianceProfile drives skill selection) | Pending |
| SKILL-03 | Traceable provenance for every skill execution | Pending |

### Remediation (REMED)
| ID | Requirement | Status |
|----|-------------|--------|
| REMED-01 | Deterministic remediation skills (tagging, metadata, lists, tables) | Pending |
| REMED-02 | AI-assisted suggestion skills (alt text, heading disambiguation) | Pending |

### Validation (VALID)
| ID | Requirement | Status |
|----|-------------|--------|
| VALID-01 | Validation engine based on Skill Registry | Pending |
| VALID-02 | Matterhorn Protocol coverage (all 136 checks mapped) | Pending |
| VALID-03 | WCAG 2.1 AA and Section 508 reporting | Pending |
| VALID-04 | Machine-readable report artifacts (EARL, JSON) | Pending |

### Review Dashboard (REVIEW)
| ID | Requirement | Status |
|----|-------------|--------|
| REVIEW-01 | Review dashboard for human-in-the-loop triage | Pending |
| REVIEW-02 | Tag tree viewer and reading-order overlay | Pending |
| REVIEW-03 | Approve/reject/edit flow for AI suggestions | Pending |

### Operations & Performance (OPS)
| ID | Requirement | Status |
|----|-------------|--------|
| OPS-01 | Job orchestrator with profile-based routing | Pending |
| OPS-02 | Docker and Kubernetes deployment artifacts | Pending |
| OPS-03 | Observability (logs, traces, metrics) | Pending |
| OPS-04 | Performance target: >= 30 pages/sec throughput | Pending |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INGEST-01 | Phase 1 | Pending |
| INGEST-02 | Phase 1 | Pending |
| INGEST-03 | Phase 1 | Pending |
| CORE-01 | Phase 2 | Pending |
| CORE-02 | Phase 2 | Pending |
| CORE-03 | Phase 2 | Pending |
| CORE-04 | Phase 3 | Pending |
| OCR-01 | Phase 2 | Pending |
| OCR-02 | Phase 2 | Pending |
| OCR-03 | Phase 2 | Pending |
| SKILL-01 | Phase 1 | Pending |
| SKILL-02 | Phase 1 | Pending |
| SKILL-03 | Phase 3 | Pending |
| REMED-01 | Phase 3 | Pending |
| REMED-02 | Phase 5 | Pending |
| VALID-01 | Phase 4 | Pending |
| VALID-02 | Phase 4 | Pending |
| VALID-03 | Phase 4 | Pending |
| VALID-04 | Phase 4 | Pending |
| REVIEW-01 | Phase 5 | Pending |
| REVIEW-02 | Phase 5 | Pending |
| REVIEW-03 | Phase 5 | Pending |
| OPS-01 | Phase 1 | Pending |
| OPS-02 | Phase 6 | Pending |
| OPS-03 | Phase 1 | Pending |
| OPS-04 | Phase 6 | Pending |

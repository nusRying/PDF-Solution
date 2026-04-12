# Phase 06 Context: Operations & Hardening

## Vision
Deploy a production-grade, secure, and performant platform. This phase focuses on moving from a development/proof-of-concept state to a scalable, secure, and observable production environment.

## Requirements Addressed
- **OPS-02**: Dockerization (FastAPI + Tesseract + Pikepdf)
- **OPS-04**: Performance target: >= 30 pages/sec throughput
- **OPS-05**: Production-ready Job Queue (Celery/Redis)
- **OPS-06**: Cloud storage connectors (S3/Azure Blob)
- **OPS-07**: Comprehensive performance benchmarking
- **OPS-08**: Final security hardening (API keys, CORS, rate limiting)

## User Decisions (D-01 to D-05)
- **D-01: Dockerization**: Use a multi-stage `Dockerfile` to keep image size small. Include system-level dependencies: `tesseract-ocr`, `libpoppler-cpp-dev`, `python3-tk`, `libgl1`.
- **D-02: Production Queue**: Replace the internal `Thread` based queue with `Celery` using `Redis` as the broker and result backend.
- **D-03: Cloud Storage**: Implement an `S3FileStore` using `boto3` that adheres to the same interface as the local `FileStore`.
- **D-04: Security**: Implement API key authentication via a custom FastAPI dependency. Configure CORS for a specified list of allowed origins.
- **D-05: Benchmarking**: Create a script in `scripts/benchmark.py` that can process a directory of PDFs and report pages/second.

## Implementation Details
- The existing `FileStore` should be refactored into a `BaseFileStore` (abstract base class) or an interface to support both `LocalFileStore` and `S3FileStore`.
- Celery workers will run the `process_ingest_job` function.
- API keys will be stored in environment variables (for now) or a simple config file.

## Success Criteria
- [ ] Platform can be started using `docker-compose up`.
- [ ] Jobs are processed by Celery workers, observable via Redis.
- [ ] Files can be stored and retrieved from S3 (or MinIO for local testing).
- [ ] API endpoints are protected by API keys.
- [ ] Benchmarking script provides accurate throughput metrics.

# PDF Accessibility Platform

Initial bootstrap for the PDF accessibility remediation platform.

## Current scope

- FastAPI service skeleton
- centralized settings
- runtime readiness checks for Tesseract and qpdf
- project data directory bootstrap

## Revival environment

This repository is intended to run in the existing Conda env:

- `revival`

Install the package in editable mode:

```powershell
& "C:\Users\umair\miniconda3\Scripts\conda.exe" run -n revival python -m pip install -e .[dev]
```

Run the API:

```powershell
& "C:\Users\umair\miniconda3\Scripts\conda.exe" run -n revival uvicorn pdf_accessibility.main:app --host 127.0.0.1 --port 8000
```

Useful endpoints:

- `/`
- `/healthz`
- `/readyz`
- `/api/v1/documents` (POST PDF upload)
- `/api/v1/jobs/{job_id}`
- `/api/v1/jobs/{job_id}/metrics`
- `/api/v1/metrics/lanes`
- `/api/v1/documents/{document_id}/parser-output`
- `/api/v1/documents/{document_id}/preflight-output`
- `/api/v1/documents/{document_id}/ocr-output`
- `/api/v1/documents/{document_id}/canonical-output`
- `/api/v1/documents/{document_id}/remediated-canonical-output`
- `/api/v1/documents/{document_id}/remediation-output`
- `/api/v1/documents/{document_id}/validation-output`
- `/api/v1/jobs/{job_id}/retry` (POST)

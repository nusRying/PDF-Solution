# Deployment Instructions: PDF Accessibility Platform

This document provides instructions for deploying and running the PDF Accessibility Remediation Platform in various environments.

---

## 1. Prerequisites

### Local Development (Conda)
- **Conda** (Miniconda or Anaconda)
- **Tesseract OCR 5.x** (installed and in PATH)
- **Poppler / QPDF** (for PDF manipulation)
- **Redis** (running locally for the job queue)

### Containerized Deployment (Docker)
- **Docker** and **Docker Compose** (V2 recommended)
- **API Keys** for OpenAI or Anthropic (optional, for real AI assist)

---

## 2. Fast Track: Docker Compose (Recommended)

The easiest way to run the full stack (API + Worker + UI + Storage + Redis) is using Docker Compose.

### Step 1: Configure Environment
Copy `.env.example` to `.env` and fill in your AI provider keys if desired.

```bash
# Example .env
OPENAI_API_KEY=sk-...
AI_PROVIDER=openai
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### Step 2: Build and Start
```bash
docker-compose up --build
```

- **API**: [http://localhost:8000](http://localhost:8000)
- **Review Dashboard (UI)**: [http://localhost:3000](http://localhost:3000)
- **MinIO (S3 Console)**: [http://localhost:9001](http://localhost:9001) (User: admin / Pass: password)

---

## 3. Local Development (Conda)

If you prefer running directly on your machine:

### Step 1: Setup Environment
```bash
# Using the existing 'revival' environment
conda activate revival

# Install dependencies
pip install -e .[dev]
```

### Step 2: Start the Services
You will need three terminal windows:

**Terminal 1: FastAPI Server**
```bash
$env:PYTHONPATH = "src"
python -m pdf_accessibility.main
```

**Terminal 2: Celery Worker** (requires Redis running)
```bash
$env:PYTHONPATH = "src"
celery -A pdf_accessibility.core.celery worker --loglevel=info
```

**Terminal 3: Next.js Frontend**
```bash
cd ui
npm install
npm run dev
```

---

## 4. Configuration Reference

All settings can be overridden via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | PDF Accessibility Platform | Name of the service |
| `AI_PROVIDER` | `mock` | `openai`, `anthropic`, or `mock` |
| `OPENAI_API_KEY` | `None` | Required if provider is `openai` |
| `STORAGE_BACKEND` | `local` | `local` or `s3` |
| `REDIS_URL` | `redis://localhost:6379/0` | Broker for Celery and cache |
| `QUEUE_BACKEND` | `threaded` | Use `celery` for production, `threaded` for simple local dev |

---

## 5. Verification & Testing

### Run Automated Tests
```bash
$env:PYTHONPATH = "src;."
python -m pytest tests/
```

### Run Throughput Benchmark
To verify the system can handle the target of 30 pages/sec:
```bash
python scripts/benchmark.py --pdf path/to/large_sample.pdf --iters 5
```

---

## 6. Enterprise Hardening (Production)

For production deployments (AWS/GCP/Azure):
1. **Infrastructure**: Deploy the `api` and `worker` containers to a Kubernetes cluster.
2. **Auto-scaling**: Use Horizontal Pod Autoscaling (HPA) for the `worker` pods based on Celery queue depth.
3. **Storage**: Switch `STORAGE_BACKEND` to `s3` and provide real S3 bucket credentials.
4. **Security**: Ensure the API is behind a Load Balancer with TLS/SSL and configure `CORS_ORIGINS` in settings.

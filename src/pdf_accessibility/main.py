from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from pdf_accessibility.api.routes.documents import router as documents_router
from pdf_accessibility.api.routes.health import router as health_router
from pdf_accessibility.api.routes.jobs import router as jobs_router
from pdf_accessibility.api.routes.metrics import router as metrics_router
from pdf_accessibility.core.logging import configure_logging
from pdf_accessibility.core.settings import get_settings
from pdf_accessibility.services.job_queue import JobQueueService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    settings.ensure_directories()
    job_queue = JobQueueService(
        settings=settings,
        worker_count=settings.ingest_worker_count,
        poll_timeout_seconds=settings.ingest_queue_poll_seconds,
    )
    job_queue.start()
    app.state.job_queue = job_queue

    try:
        yield
    finally:
        job_queue.stop()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(health_router)
    app.include_router(documents_router, prefix=settings.api_prefix)
    app.include_router(jobs_router, prefix=settings.api_prefix)
    app.include_router(metrics_router, prefix=settings.api_prefix)
    return app


app = create_app()


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "pdf_accessibility.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )

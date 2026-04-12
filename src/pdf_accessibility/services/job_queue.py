from __future__ import annotations

import logging
from queue import Empty, Queue
from threading import Event, Thread

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.services.ingestion import process_ingest_job

logger = logging.getLogger(__name__)


class JobQueueService:
    def __init__(
        self,
        settings: Settings,
        worker_count: int = 1,
        poll_timeout_seconds: float = 0.5,
    ) -> None:
        self._settings = settings
        self._worker_count = max(1, worker_count)
        self._poll_timeout_seconds = max(0.1, poll_timeout_seconds)
        self._queue: Queue[str | None] = Queue()
        self._stop_event = Event()
        self._workers: list[Thread] = []
        self._started = False

    @property
    def started(self) -> bool:
        return self._started

    def start(self) -> None:
        if self._started:
            return

        self._stop_event.clear()
        self._workers = []
        for index in range(self._worker_count):
            worker = Thread(
                target=self._worker_loop,
                name=f"ingest-worker-{index + 1}",
                daemon=True,
            )
            worker.start()
            self._workers.append(worker)
        self._started = True

    def stop(self) -> None:
        if not self._started:
            return

        self._stop_event.set()
        for _ in self._workers:
            self._queue.put(None)

        for worker in self._workers:
            worker.join(timeout=5.0)

        self._workers = []
        self._started = False

    def enqueue(self, job_id: str) -> None:
        self._queue.put(job_id)

    def _worker_loop(self) -> None:
        while True:
            if self._stop_event.is_set() and self._queue.empty():
                return

            try:
                job_id = self._queue.get(timeout=self._poll_timeout_seconds)
            except Empty:
                continue

            try:
                if job_id is None:
                    return
                process_ingest_job(job_id=job_id, settings=self._settings)
            except Exception:
                logger.exception("Background ingest job failed", extra={"job_id": job_id})
            finally:
                self._queue.task_done()

from __future__ import annotations

import logging
from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)

# Metrics for Skill Execution
SKILL_EXECUTION_TOTAL = Counter(
    "skill_execution_total",
    "Total number of skill executions",
    ["skill_id", "outcome"],
)

SKILL_EXECUTION_DURATION_SECONDS = Histogram(
    "skill_execution_duration_seconds",
    "Duration of skill execution in seconds",
    ["skill_id"],
)


def record_skill_execution(skill_id: str, duration: float, success: bool) -> None:
    """Helper to record skill execution metrics."""
    outcome = "success" if success else "failure"
    SKILL_EXECUTION_TOTAL.labels(skill_id=skill_id, outcome=outcome).inc()
    SKILL_EXECUTION_DURATION_SECONDS.labels(skill_id=skill_id).observe(duration)
    
    logger.debug(f"Recorded metrics for {skill_id}: {outcome}, {duration:.4f}s")

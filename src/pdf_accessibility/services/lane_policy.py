from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from pdf_accessibility.models.preflight import PreflightArtifact, ProcessingLane


class OCRMode(str, Enum):
    skip = "skip"
    selective = "selective"


class LaneExecutionPolicy(BaseModel):
    lane: ProcessingLane
    name: str
    ocr_mode: OCRMode
    manual_review_required: bool = False
    notes: list[str] = Field(default_factory=list)


def resolve_lane_execution_policy(preflight_artifact: PreflightArtifact) -> LaneExecutionPolicy:
    lane = preflight_artifact.lane

    if lane == ProcessingLane.fast:
        return LaneExecutionPolicy(
            lane=lane,
            name="fast-native",
            ocr_mode=OCRMode.skip,
            notes=["OCR skipped for fast lane to maximize throughput."],
        )

    if lane == ProcessingLane.standard:
        return LaneExecutionPolicy(
            lane=lane,
            name="standard-selective-ocr",
            ocr_mode=OCRMode.selective,
            notes=["OCR applied only to pages without native text."],
        )

    if lane == ProcessingLane.heavy:
        return LaneExecutionPolicy(
            lane=lane,
            name="heavy-quality",
            ocr_mode=OCRMode.selective,
            notes=["Quality-first path with selective OCR and full remediation."],
        )

    return LaneExecutionPolicy(
        lane=lane,
        name="manual-review-priority",
        ocr_mode=OCRMode.selective,
        manual_review_required=True,
        notes=[
            "Manual lane engaged due to uncertain classification or unsupported complexity.",
        ],
    )

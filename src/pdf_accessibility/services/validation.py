from __future__ import annotations

from pdf_accessibility.models.compliance import ComplianceProfile, ComplianceStandard
from pdf_accessibility.models.documents import DocumentSourceType, ParserArtifact
from pdf_accessibility.models.ocr import OCRArtifact
from pdf_accessibility.models.preflight import PreflightArtifact, ProcessingLane
from pdf_accessibility.models.validation import (
    StandardMapping,
    ValidationArtifact,
    ValidationFinding,
    ValidationSeverity,
    ValidationStatus,
)


def run_initial_validation(
    parser_artifact: ParserArtifact,
    ocr_artifact: OCRArtifact | None,
    canonical_document: CanonicalDocument,
    preflight_artifact: PreflightArtifact | None = None,
    manual_review_required: bool = False,
    profile: ComplianceProfile = ComplianceProfile.profile_b,
) -> ValidationArtifact:
    findings: list[ValidationFinding] = []
    ocr_page_lookup = {
        page.page_number: page for page in (ocr_artifact.pages if ocr_artifact else [])
    }

    if parser_artifact.source_type in {DocumentSourceType.scanned, DocumentSourceType.image_only}:
        findings.append(
            ValidationFinding(
                rule_id="DOC-001",
                severity=ValidationSeverity.info,
                message="Document is image-based and depends on OCR-derived text.",
                source="classifier",
                standards=[
                    StandardMapping(
                        standard=ComplianceStandard.pdf_ua_1,
                        rule_id="Matterhorn 01",
                        criterion="Real content must be tagged.",
                    )
                ],
            )
        )

    if preflight_artifact is not None:
        findings.append(
            ValidationFinding(
                rule_id="LANE-000",
                severity=ValidationSeverity.info,
                message=f"Preflight routed document to '{preflight_artifact.lane.value}' lane.",
                source="preflight",
            )
        )
        if preflight_artifact.lane == ProcessingLane.manual or manual_review_required:
            findings.append(
                ValidationFinding(
                    rule_id="LANE-001",
                    severity=ValidationSeverity.warning,
                    message="Manual review is required for this document lane.",
                    source="preflight",
                )
            )

    for page in canonical_document.pages:
        if page.block_count == 0:
            findings.append(
                ValidationFinding(
                    rule_id="CANON-001",
                    severity=ValidationSeverity.error,
                    message="Page has no canonical text blocks.",
                    page_number=page.page_number,
                    source="canonical",
                    standards=[
                        StandardMapping(
                            standard=ComplianceStandard.wcag_2_1_aa,
                            rule_id="1.1.1",
                            criterion="Non-text Content",
                        )
                    ],
                )
            )

        if page.used_ocr:
            findings.append(
                ValidationFinding(
                    rule_id="OCR-002",
                    severity=ValidationSeverity.warning,
                    message="Page content was derived from OCR and should be reviewed.",
                    page_number=page.page_number,
                    source="ocr",
                )
            )

        ocr_page = ocr_page_lookup.get(page.page_number)
        if ocr_page and ocr_page.error:
            findings.append(
                ValidationFinding(
                    rule_id="OCR-001",
                    severity=ValidationSeverity.error,
                    message=ocr_page.error,
                    page_number=page.page_number,
                    source="ocr",
                )
            )

    error_count = sum(1 for finding in findings if finding.severity == ValidationSeverity.error)
    warning_count = sum(1 for finding in findings if finding.severity == ValidationSeverity.warning)

    if error_count:
        status = ValidationStatus.failed
    elif warning_count:
        status = ValidationStatus.needs_review
    else:
        status = ValidationStatus.passed

    return ValidationArtifact(
        document_id=canonical_document.document_id,
        profile=profile,
        status=status,
        finding_count=len(findings),
        error_count=error_count,
        warning_count=warning_count,
        findings=findings,
    )

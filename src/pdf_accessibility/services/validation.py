from __future__ import annotations

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.compliance import ComplianceProfile, get_profile_definition
from pdf_accessibility.models.documents import ParserArtifact
from pdf_accessibility.models.ocr import OCRArtifact
from pdf_accessibility.models.preflight import PreflightArtifact, ProcessingLane
from pdf_accessibility.models.validation import (
    ValidationArtifact,
    ValidationFinding,
    ValidationSeverity,
    ValidationStatus,
)
from pdf_accessibility.skills.registry import get_registry
from pdf_accessibility.skills.validation.image_only import ImageOnlyValidationSkill
from pdf_accessibility.skills.validation.layout import HeadingStructureSkill, ReadingOrderJumpSkill
from pdf_accessibility.skills.validation.missing_blocks import MissingBlocksValidationSkill
from pdf_accessibility.skills.validation.ocr_usage import OCRUsageValidationSkill
from pdf_accessibility.skills.validation.structural import (
    HeadingHierarchySkill,
    FirstHeadingSkill,
    TableTHSkill,
)
from pdf_accessibility.skills.validation.content import FigureAltSkill
from pdf_accessibility.skills.validation.metadata import (
    DocumentLanguageValidationSkill,
    DocumentTitleValidationSkill,
)
from pdf_accessibility.skills.validation.document import (
    MarkInfoSkill,
    StructTreeSkill,
    PDFUAIdentifierSkill,
)
from pdf_accessibility.skills.validation.tables import TableStructureSkill
from pdf_accessibility.skills.validation.forms import FormFieldValidationSkill

# Initialize Registry
_registry = get_registry()
_registry.register_validation(ImageOnlyValidationSkill())
_registry.register_validation(MissingBlocksValidationSkill())
_registry.register_validation(OCRUsageValidationSkill())
_registry.register_validation(ReadingOrderJumpSkill())
_registry.register_validation(HeadingStructureSkill())
_registry.register_validation(HeadingHierarchySkill())
_registry.register_validation(FirstHeadingSkill())
_registry.register_validation(TableTHSkill())
_registry.register_validation(FigureAltSkill())
_registry.register_validation(DocumentLanguageValidationSkill())
_registry.register_validation(DocumentTitleValidationSkill())
_registry.register_validation(MarkInfoSkill())
_registry.register_validation(StructTreeSkill())
_registry.register_validation(PDFUAIdentifierSkill())
_registry.register_validation(TableStructureSkill())
_registry.register_validation(FormFieldValidationSkill())


def run_validation_pipeline(
    document: CanonicalDocument,
    settings: Settings,
    profile: ComplianceProfile = ComplianceProfile.profile_b,
    preflight_artifact: PreflightArtifact | None = None,
    manual_review_required: bool = False,
) -> ValidationArtifact:
    findings: list[ValidationFinding] = []
    
    # Run dynamic skills from profile
    profile_def = get_profile_definition(profile)
    registry = get_registry()
    
    for skill_id in profile_def.validation_skill_ids:
        skill = registry.get_validation(skill_id)
        if skill:
            findings.extend(skill.validate(document, settings))

    # Add pipeline-specific ambient findings
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

    error_count = sum(1 for finding in findings if finding.severity == ValidationSeverity.error)
    warning_count = sum(1 for finding in findings if finding.severity == ValidationSeverity.warning)

    if error_count:
        status = ValidationStatus.failed
    elif warning_count:
        status = ValidationStatus.needs_review
    else:
        status = ValidationStatus.passed

    return ValidationArtifact(
        document_id=document.document_id,
        profile=profile,
        status=status,
        finding_count=len(findings),
        error_count=error_count,
        warning_count=warning_count,
        findings=findings,
    )


def run_initial_validation(
    parser_artifact: ParserArtifact,
    ocr_artifact: OCRArtifact | None,
    canonical_document: CanonicalDocument,
    preflight_artifact: PreflightArtifact | None = None,
    manual_review_required: bool = False,
    profile: ComplianceProfile = ComplianceProfile.profile_b,
) -> ValidationArtifact:
    """Legacy wrapper for run_validation_pipeline."""
    settings = Settings()
    return run_validation_pipeline(
        document=canonical_document,
        settings=settings,
        profile=profile,
        preflight_artifact=preflight_artifact,
        manual_review_required=manual_review_required,
    )

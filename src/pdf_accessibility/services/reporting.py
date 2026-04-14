from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from pdf_accessibility.models.documents import utc_now
from pdf_accessibility.models.validation import (
    ValidationArtifact,
    ValidationFinding,
    ValidationSeverity,
    ValidationStatus,
)


class EARLReportGenerator:
    """
    Generates machine-readable accessibility reports in EARL (Evaluation Report Language) 1.0 format.
    Output is a JSON-LD structure.
    """

    def generate_report(self, validation_artifact: ValidationArtifact) -> str:
        """
        Converts a ValidationArtifact into an EARL JSON-LD report string.
        """
        report = self.generate_earl(validation_artifact)
        return json.dumps(report, indent=2)

    def generate_earl(self, validation_artifact: ValidationArtifact) -> dict[str, Any]:
        """
        Converts a ValidationArtifact into an EARL JSON-LD report dictionary.
        """
        return {
            "@context": "https://www.w3.org/WAI/ER/EARL/n3",
            "@type": "earl:Assertion",
            "assertedBy": "pdf-accessibility-platform",
            "subject": {
                "@type": "earl:TestSubject",
                "document_id": validation_artifact.document_id,
            },
            "test": {
                "@type": "earl:TestCase",
                "rule_catalog_version": validation_artifact.rule_catalog_version,
            },
            "result": {
                "@type": "earl:TestResult",
                "outcome": self._map_status_to_outcome(validation_artifact.status),
                "date": validation_artifact.generated_at.isoformat(),
            },
            "findings": [self._map_finding(f) for f in validation_artifact.findings],
        }

    def _map_status_to_outcome(self, status: ValidationStatus) -> str:
        mapping = {
            ValidationStatus.passed: "earl:passed",
            ValidationStatus.failed: "earl:failed",
            ValidationStatus.needs_review: "earl:cantTell",
        }
        return mapping.get(status, "earl:untested")

    def _map_finding(self, finding: ValidationFinding) -> dict[str, Any]:
        outcome = "earl:failed"
        if finding.severity == ValidationSeverity.warning:
            outcome = "earl:cantTell"
        elif finding.severity == ValidationSeverity.info:
            outcome = "earl:untested"

        earl_finding = {
            "@type": "earl:Assertion",
            "test": {
                "@type": "earl:TestCase",
                "rule_id": finding.rule_id,
                "message": finding.message,
            },
            "result": {
                "@type": "earl:TestResult",
                "outcome": outcome,
            },
        }
        if finding.page_number:
            earl_finding["subject"] = {"page_number": finding.page_number}
        if finding.block_id:
            earl_finding["subject"] = earl_finding.get("subject", {})
            earl_finding["subject"]["block_id"] = finding.block_id

        if finding.standards:
            earl_finding["test"]["standards"] = [
                {"standard": s.standard, "rule_id": s.rule_id} for s in finding.standards
            ]
            
        return earl_finding

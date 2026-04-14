import json
from datetime import datetime
from pdf_accessibility.models.validation import (
    ValidationArtifact,
    ValidationFinding,
    ValidationSeverity,
    ValidationStatus,
)
from pdf_accessibility.services.reporting import EARLReportGenerator

def test_generate_earl_report():
    # Arrange
    generator = EARLReportGenerator()
    findings = [
        ValidationFinding(
            rule_id="MATTERHORN_01_01",
            severity=ValidationSeverity.error,
            message="Missing title",
            source="document_metadata",
            standards=[]
        ),
        ValidationFinding(
            rule_id="MATTERHORN_02_01",
            severity=ValidationSeverity.warning,
            message="Possible reading order issue",
            page_number=1,
            block_id="b1",
            source="layout_engine",
            standards=[]
        )
    ]
    artifact = ValidationArtifact(
        document_id="doc_123",
        status=ValidationStatus.failed,
        finding_count=2,
        error_count=1,
        warning_count=1,
        findings=findings,
        generated_at=datetime(2023, 1, 1, 12, 0, 0)
    )

    # Act
    report_json = generator.generate_report(artifact)
    report = json.loads(report_json)

    # Assert
    assert report["@context"] == "https://www.w3.org/WAI/ER/EARL/n3"
    assert report["@type"] == "earl:Assertion"
    assert report["subject"]["document_id"] == "doc_123"
    assert report["result"]["outcome"] == "earl:failed"
    assert report["result"]["date"] == "2023-01-01T12:00:00"
    
    assert len(report["findings"]) == 2
    
    # Check first finding
    f1 = report["findings"][0]
    assert f1["test"]["rule_id"] == "MATTERHORN_01_01"
    assert f1["result"]["outcome"] == "earl:failed"
    
    # Check second finding
    f2 = report["findings"][1]
    assert f2["test"]["rule_id"] == "MATTERHORN_02_01"
    assert f2["result"]["outcome"] == "earl:cantTell"
    assert f2["subject"]["page_number"] == 1
    assert f2["subject"]["block_id"] == "b1"

def test_map_status_to_outcome_passed():
    generator = EARLReportGenerator()
    assert generator._map_status_to_outcome(ValidationStatus.passed) == "earl:passed"

def test_map_status_to_outcome_needs_review():
    generator = EARLReportGenerator()
    assert generator._map_status_to_outcome(ValidationStatus.needs_review) == "earl:cantTell"

import pytest
from pdf_accessibility.services.external_validators import PACIntegrationService
from pdf_accessibility.models.validation import ValidationStatus, ValidationSeverity

def test_pac_integration_mock_run():
    service = PACIntegrationService()
    # Mock run on a document
    result = service.run_pac_validation("doc_123.pdf", mock=True)
    
    assert result["status"] in ["passed", "failed"]
    assert "findings" in result
    assert result["tool"] == "PAC"

def test_pac_to_internal_mapping():
    service = PACIntegrationService()
    # Mock PAC finding (using a hypothetical structure for now)
    pac_finding = {
        "rule_id": "1.3.1.1", # PAC code
        "status": "failed",
        "message": "Alternative text missing",
        "page": 1
    }
    
    internal_finding = service.map_pac_finding_to_internal(pac_finding)
    
    # Assuming PAC 1.3.1.1 maps to Matterhorn 01-001 or similar
    assert internal_finding.rule_id is not None
    assert internal_finding.severity == ValidationSeverity.error
    assert internal_finding.page_number == 1

from __future__ import annotations

from typing import Any, Dict, List

from pdf_accessibility.models.validation import (
    ValidationFinding,
    ValidationSeverity,
    ValidationStatus,
)


class PACIntegrationService:
    """
    Service to integrate results from the PDF Accessibility Checker (PAC) tool.
    Currently supports mock execution and basic finding mapping.
    """

    # Mapping PAC rule codes to Matterhorn rule IDs where possible
    PAC_TO_MATTERHORN = {
        "1.3.1.1": "MATTERHORN_01_001",
        "1.3.1.2": "MATTERHORN_01_002",
        "1.3.1.3": "MATTERHORN_01_003",
        "1.3.1.4": "MATTERHORN_01_004",
        "1.3.1.5": "MATTERHORN_01_005",
    }

    def run_pac_validation(self, file_path: str, mock: bool = True) -> Dict[str, Any]:
        """
        Runs PAC validation on the given file.
        In mock mode, returns a dummy result.
        In live mode, it would call the PAC executable/API.
        """
        if mock:
            return {
                "tool": "PAC",
                "status": "failed",
                "findings": [
                    {
                        "rule_id": "1.3.1.1",
                        "status": "failed",
                        "message": "Alternative text missing",
                        "page": 1,
                    }
                ],
            }
        
        # Real integration would go here (e.g. subprocess call to PAC CLI)
        raise NotImplementedError("Real PAC integration not yet implemented")

    def map_pac_finding_to_internal(self, pac_finding: Dict[str, Any]) -> ValidationFinding:
        """
        Maps a PAC finding dictionary to an internal ValidationFinding object.
        """
        pac_rule_id = pac_finding.get("rule_id", "Unknown")
        internal_rule_id = self.PAC_TO_MATTERHORN.get(pac_rule_id, f"PAC_{pac_rule_id}")
        
        severity = ValidationSeverity.error
        if pac_finding.get("status") == "warning":
            severity = ValidationSeverity.warning
        
        return ValidationFinding(
            rule_id=internal_rule_id,
            severity=severity,
            message=pac_finding.get("message", "No message provided"),
            page_number=pac_finding.get("page"),
            source="PAC",
            standards=[]
        )

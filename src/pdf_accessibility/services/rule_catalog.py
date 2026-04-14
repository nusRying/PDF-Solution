from __future__ import annotations

from pydantic import BaseModel, Field
from pdf_accessibility.models.validation import ValidationSeverity
from pdf_accessibility.models.compliance import ComplianceStandard

class RuleInfo(BaseModel):
    rule_id: str
    name: str
    description: str
    severity: ValidationSeverity
    matterhorn_mapping: str | None = None
    wcag_mapping: str | None = None

class RuleCatalog:
    def __init__(self) -> None:
        self._rules: dict[str, RuleInfo] = {
            "VALID-DOC-001": RuleInfo(
                rule_id="VALID-DOC-001",
                name="Image-only Document Check",
                description="Checks if the document is scanned or image-only and depends on OCR.",
                severity=ValidationSeverity.info,
                matterhorn_mapping="01-001",
                wcag_mapping="1.1.1",
            ),
            "VALID-CANON-001": RuleInfo(
                rule_id="VALID-CANON-001",
                name="Missing Canonical Blocks Check",
                description="Validates that each page in the canonical document has at least one text block.",
                severity=ValidationSeverity.error,
                wcag_mapping="1.1.1",
            ),
            "VALID-OCR-002": RuleInfo(
                rule_id="VALID-OCR-002",
                name="OCR Usage Check",
                description="Flags pages where content was derived from OCR, indicating a need for human review.",
                severity=ValidationSeverity.warning,
            ),
            "VALID-LAYOUT-001": RuleInfo(
                rule_id="VALID-LAYOUT-001",
                name="Reading Order Jump Check",
                description="Detects illogical reading order jumps across the page.",
                severity=ValidationSeverity.warning,
                matterhorn_mapping="01-006",
                wcag_mapping="1.3.2",
            ),
            "VALID-LAYOUT-002": RuleInfo(
                rule_id="VALID-LAYOUT-002",
                name="Heading Structure Check",
                description="Checks if the document has at least one heading.",
                severity=ValidationSeverity.warning,
                matterhorn_mapping="07-001",
                wcag_mapping="1.3.1",
            ),
            "VALID-HEAD-001": RuleInfo(
                rule_id="VALID-HEAD-001",
                name="Heading Level Continuity",
                description="Ensures heading levels follow a logical hierarchy (e.g., no H1 to H3 jump).",
                severity=ValidationSeverity.error,
                matterhorn_mapping="07-002",
                wcag_mapping="1.3.1",
            ),
            "VALID-META-001": RuleInfo(
                rule_id="VALID-META-001",
                name="Document Title Presence",
                description="Checks if the document has a non-empty title in metadata.",
                severity=ValidationSeverity.error,
                matterhorn_mapping="06-002",
                wcag_mapping="2.4.2",
            ),
            "VALID-FIG-001": RuleInfo(
                rule_id="VALID-FIG-001",
                name="Figure Alt-Text Check",
                description="Validates that all figures have descriptive alternative text.",
                severity=ValidationSeverity.error,
                matterhorn_mapping="14-001",
                wcag_mapping="1.1.1",
            ),
        }

    def get_rule_info(self, rule_id: str) -> RuleInfo | None:
        return self._rules.get(rule_id)

    def get_all_rules(self) -> list[RuleInfo]:
        return list(self._rules.values())

_catalog = RuleCatalog()

def get_rule_catalog() -> RuleCatalog:
    return _catalog

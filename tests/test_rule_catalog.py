from pdf_accessibility.services.rule_catalog import get_rule_catalog, RuleInfo
from pdf_accessibility.models.validation import ValidationSeverity

def test_rule_catalog_initialization():
    catalog = get_rule_catalog()
    assert catalog is not None
    
    rules = catalog.get_all_rules()
    assert len(rules) >= 5  # Success criteria says at least 5
    
    # Check for specific rules mentioned in implementation
    rule_ids = [r.rule_id for r in rules]
    assert "VALID-DOC-001" in rule_ids
    assert "VALID-LAYOUT-001" in rule_ids
    assert "VALID-HEAD-001" in rule_ids
    assert "VALID-META-001" in rule_ids
    assert "VALID-FIG-001" in rule_ids

def test_rule_info_mapping_fields():
    catalog = get_rule_catalog()
    rule = catalog.get_rule_info("VALID-HEAD-001")
    
    assert rule is not None
    assert rule.matterhorn_mapping == "07-002"
    assert rule.wcag_mapping == "1.3.1"
    assert rule.severity == ValidationSeverity.error

def test_rule_catalog_get_rule_info():
    catalog = get_rule_catalog()
    rule = catalog.get_rule_info("NON-EXISTENT")
    assert rule is None
    
    rule = catalog.get_rule_info("VALID-FIG-001")
    assert rule.rule_id == "VALID-FIG-001"
    assert rule.matterhorn_mapping == "14-001"
    assert rule.wcag_mapping == "1.1.1"

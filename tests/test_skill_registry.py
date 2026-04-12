from __future__ import annotations

import pytest

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument
from pdf_accessibility.models.remediation import RemediationAction
from pdf_accessibility.skills.base import RemediationSkill, SkillCategory
from pdf_accessibility.skills.registry import SkillRegistry


class MockRemediationSkill(RemediationSkill):
    @property
    def skill_id(self) -> str:
        return "MOCK-REMED-001"

    @property
    def name(self) -> str:
        return "Mock Remediation"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Mock description"

    @property
    def category(self) -> SkillCategory:
        return SkillCategory.metadata

    def remediate(self, canonical_doc: CanonicalDocument, settings: Settings) -> list[RemediationAction]:
        return []


def test_registry_registration():
    registry = SkillRegistry()
    skill = MockRemediationSkill()
    registry.register_skill(skill)
    
    assert registry.get_skill("MOCK-REMED-001") == skill
    assert registry.get_remediation("MOCK-REMED-001") == skill
    assert skill in registry.get_all_remediation()
    assert skill in registry.get_remediation_by_category("metadata")


def test_registry_get_skills_by_ids():
    registry = SkillRegistry()
    skill1 = MockRemediationSkill()
    
    class AnotherMockSkill(MockRemediationSkill):
        @property
        def skill_id(self) -> str:
            return "MOCK-REMED-002"

    skill2 = AnotherMockSkill()
    registry.register_skill(skill1)
    registry.register_skill(skill2)

    skills = registry.get_skills_by_ids(["MOCK-REMED-001", "MOCK-REMED-002", "MISSING"])
    assert len(skills) == 2
    assert skill1 in skills
    assert skill2 in skills


def test_registry_missing_skill():
    registry = SkillRegistry()
    assert registry.get_skill("NON-EXISTENT") is None
    assert registry.get_skills_by_ids(["NON-EXISTENT"]) == []


def test_registry_singleton():
    from pdf_accessibility.skills.registry import get_registry
    registry1 = get_registry()
    registry2 = get_registry()
    assert registry1 is registry2

from __future__ import annotations

import logging
from typing import TypeVar

from pdf_accessibility.skills.base import BaseSkill, RemediationSkill, ValidationSkill

T = TypeVar("T", bound=BaseSkill)

logger = logging.getLogger(__name__)


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, BaseSkill] = {}

    def register_skill(self, skill: BaseSkill) -> None:
        if skill.skill_id in self._skills:
            logger.warning(f"Skill {skill.skill_id} already registered. Overwriting.")
        self._skills[skill.skill_id] = skill
        logger.debug(f"Registered skill: {skill.skill_id} ({skill.name})")

    def get_skill(self, skill_id: str) -> BaseSkill | None:
        return self._skills.get(skill_id)

    def get_skills_by_ids(self, skill_ids: list[str]) -> list[BaseSkill]:
        return [self._skills[sid] for sid in skill_ids if sid in self._skills]

    # Legacy compatibility or specific helpers if needed
    def register_remediation(self, skill: RemediationSkill) -> None:
        self.register_skill(skill)

    def register_validation(self, skill: ValidationSkill) -> None:
        self.register_skill(skill)

    def get_remediation(self, skill_id: str) -> RemediationSkill | None:
        skill = self.get_skill(skill_id)
        if isinstance(skill, RemediationSkill):
            return skill
        return None

    def get_validation(self, skill_id: str) -> ValidationSkill | None:
        skill = self.get_skill(skill_id)
        if isinstance(skill, ValidationSkill):
            return skill
        return None

    def get_all_remediation(self) -> list[RemediationSkill]:
        return [s for s in self._skills.values() if isinstance(s, RemediationSkill)]

    def get_all_validation(self) -> list[ValidationSkill]:
        return [s for s in self._skills.values() if isinstance(s, ValidationSkill)]

    def get_remediation_by_category(self, category: str) -> list[RemediationSkill]:
        return [
            s
            for s in self._skills.values()
            if isinstance(s, RemediationSkill) and s.category.value == category
        ]

    def get_validation_by_category(self, category: str) -> list[ValidationSkill]:
        return [
            s
            for s in self._skills.values()
            if isinstance(s, ValidationSkill) and s.category.value == category
        ]


# Global Registry Singleton
_registry = SkillRegistry()


def get_registry() -> SkillRegistry:
    return _registry

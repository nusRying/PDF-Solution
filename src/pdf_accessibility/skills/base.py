from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel, Field

from pdf_accessibility.core.settings import Settings
from pdf_accessibility.models.canonical import CanonicalDocument, CanonicalPage
from pdf_accessibility.models.compliance import ComplianceStandard
from pdf_accessibility.models.remediation import RemediationAction
from pdf_accessibility.models.validation import ValidationFinding


class SkillCategory(str, Enum):
    tagging = "tagging"
    headings = "headings"
    lists = "lists"
    tables = "tables"
    figures = "figures"
    forms = "forms"
    metadata = "metadata"
    ocr = "ocr"
    reading_order = "reading-order"
    structural_fix = "structural-fix"


class BaseSkill(ABC):
    @property
    @abstractmethod
    def skill_id(self) -> str:
        """Unique identifier for the skill (e.g., 'REMED-TEXT-001')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the skill."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the skill (e.g., '1.0.0')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description of what the skill does."""
        pass

    @property
    @abstractmethod
    def category(self) -> SkillCategory:
        """Category for grouping skills."""
        pass

    @property
    def standards(self) -> list[ComplianceStandard]:
        """Standards this skill maps to."""
        return []

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.skill_id} name={self.name}>"


class RemediationSkill(BaseSkill, ABC):
    @abstractmethod
    def remediate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[RemediationAction]:
        """Execute the remediation skill on the document."""
        pass


class ValidationSkill(BaseSkill, ABC):
    @abstractmethod
    def validate(
        self,
        canonical_doc: CanonicalDocument,
        settings: Settings,
    ) -> list[ValidationFinding]:
        """Execute the validation skill on the document."""
        pass

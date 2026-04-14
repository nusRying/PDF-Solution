from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ComplianceStandard(str, Enum):
    section_508 = "Section 508"
    ada_title_ii = "ADA Title II"
    wcag_2_1_aa = "WCAG 2.1 AA"
    pdf_ua_1 = "PDF/UA-1"
    matterhorn_1_02 = "Matterhorn 1.02"


class ComplianceProfile(str, Enum):
    profile_a = "Profile A: Section 508"
    profile_b = "Profile B: ADA Title II / WCAG 2.1 AA"
    profile_c = "Profile C: PDF/UA"


class ProfileDefinition(BaseModel):
    profile: ComplianceProfile
    name: str
    primary_standards: list[ComplianceStandard]
    secondary_standards: list[ComplianceStandard] = Field(default_factory=list)
    description: str
    remediation_skill_ids: list[str] = Field(default_factory=list)
    validation_skill_ids: list[str] = Field(default_factory=list)
    require_matterhorn: bool = False
    require_wcag_mapping: bool = False


PROFILE_DEFINITIONS = {
    ComplianceProfile.profile_a: ProfileDefinition(
        profile=ComplianceProfile.profile_a,
        name="Section 508 Mode",
        primary_standards=[ComplianceStandard.section_508],
        secondary_standards=[ComplianceStandard.wcag_2_1_aa, ComplianceStandard.pdf_ua_1],
        description="Baseline reporting aligned to Revised 508 treatment of electronic content.",
        remediation_skill_ids=[
            "REMED-TEXT-001",
            "REMED-OCR-010",
            "REMED-HEAD-001",
            "REMED-LIST-001",
            "REMED-META-001",
            "REMED-ARTI-001",
        ],
        validation_skill_ids=[
            "VALID-DOC-001",
            "VALID-CANON-001",
            "VALID-OCR-002",
            "VALID-LAYOUT-001",
            "VALID-LAYOUT-002",
            "VALID-HEAD-001",
            "VALID-META-001",
            "VALID-FIG-001",
        ],
        require_wcag_mapping=True,
    ),
    ComplianceProfile.profile_b: ProfileDefinition(
        profile=ComplianceProfile.profile_b,
        name="ADA Title II / WCAG 2.1 AA Mode",
        primary_standards=[ComplianceStandard.ada_title_ii, ComplianceStandard.wcag_2_1_aa],
        secondary_standards=[ComplianceStandard.pdf_ua_1],
        description="Reporting aligned to WCAG 2.1 AA for covered digital content.",
        remediation_skill_ids=[
            "REMED-TEXT-001",
            "REMED-OCR-010",
            "REMED-HEAD-001",
            "REMED-LIST-001",
            "REMED-META-001",
            "REMED-ARTI-001",
        ],
        validation_skill_ids=[
            "VALID-DOC-001",
            "VALID-CANON-001",
            "VALID-OCR-002",
            "VALID-LAYOUT-001",
            "VALID-LAYOUT-002",
            "VALID-HEAD-001",
            "VALID-META-001",
            "VALID-FIG-001",
        ],
        require_wcag_mapping=True,
    ),
    ComplianceProfile.profile_c: ProfileDefinition(
        profile=ComplianceProfile.profile_c,
        name="PDF/UA Mode",
        primary_standards=[ComplianceStandard.pdf_ua_1, ComplianceStandard.matterhorn_1_02],
        description="Primary output target is accessible tagged PDF conforming to PDF/UA-1.",
        remediation_skill_ids=[
            "REMED-TEXT-001",
            "REMED-OCR-010",
            "REMED-HEAD-001",
            "REMED-LIST-001",
            "REMED-META-001",
            "REMED-ARTI-001",
        ],
        validation_skill_ids=[
            "VALID-DOC-001",
            "VALID-CANON-001",
            "VALID-OCR-002",
            "VALID-LAYOUT-001",
            "VALID-LAYOUT-002",
            "VALID-HEAD-001",
            "VALID-META-001",
            "VALID-FIG-001",
        ],
        require_matterhorn=True,
    ),
}


def get_profile_definition(profile: ComplianceProfile) -> ProfileDefinition:
    return PROFILE_DEFINITIONS[profile]

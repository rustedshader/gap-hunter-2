"""
Pydantic schemas for the Policy Revision Agent (Phase 3).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class SectionRevision(BaseModel):
    """LLM output for revising or creating a single policy section."""

    action: Literal["modify", "new_section"] = Field(
        description="Whether this modifies an existing section or creates a new one.",
    )
    section_title: str = Field(
        description="Title of the section (existing title for modify, new title for new_section).",
    )
    revised_content: str = Field(
        description=(
            "Full section content. For 'modify': the original text followed by "
            "the new content appended. For 'new_section': the complete new section text."
        ),
    )
    subcategory_id: str = Field(
        description="NIST subcategory ID this revision addresses, e.g. 'GV.OC-03'.",
    )
    changes_summary: str = Field(
        description="1-2 sentence description of what was added or created.",
    )


class RevisionValidationResult(BaseModel):
    """Validation result for a single section revision."""

    is_acceptable: bool = Field(
        description="True if the revision is acceptable. False if there are issues.",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Specific problems found. Empty if is_acceptable is True.",
    )

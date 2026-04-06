"""
Pydantic schemas for the Improvement Roadmap Agent.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RoadmapActionItem(BaseModel):
    """A single action item in the improvement roadmap."""

    title: str = Field(
        description="Short action title, e.g. 'Implement MFA for remote access'",
    )
    nist_ids: list[str] = Field(
        description=(
            "NIST subcategory IDs this action addresses, e.g. ['PR.AA-03']. "
            "Use real NIST IDs only (format: XX.YY-NN). "
            "For policy document creation actions with no specific gap, use an empty list []."
        ),
    )
    description: str = Field(
        description="Detailed description of what must be done (2-4 sentences).",
    )
    responsible: str = Field(
        description="Role or department responsible, e.g. 'IT Security Team'.",
    )
    effort: Literal["Low", "Medium", "High"] = Field(
        description="Estimated effort level.",
    )
    success_criteria: str = Field(
        description="Measurable outcome that proves this action is complete.",
    )
    dependencies: str = Field(
        description="What must happen before this action, or 'None'.",
    )


class RoadmapTier(BaseModel):
    """A priority tier containing multiple action items."""

    tier_name: str = Field(
        description="Tier label, e.g. 'Immediate (0-30 days)'",
    )
    timeframe: str = Field(
        description="Timeframe for this tier, e.g. '0-30 days'",
    )
    rationale: str = Field(
        description="Why these items are in this tier (1-2 sentences).",
    )
    action_items: list[RoadmapActionItem] = Field(
        description="Action items in this tier, ordered by priority.",
    )


class ImprovementRoadmap(BaseModel):
    """Complete improvement roadmap across all priority tiers."""

    executive_summary: str = Field(
        description=(
            "5-7 sentence overview of the organization's current posture, "
            "the key priorities, and the expected outcome of following this roadmap."
        ),
    )
    tiers: list[RoadmapTier] = Field(
        description=(
            "Priority tiers ordered: Immediate, Short-term, Medium-term, Long-term. "
            "Every in-scope gap must appear in at least one tier."
        ),
    )
    missing_policy_documents: list[str] = Field(
        description=(
            "Deduplicated list of CIS MS-ISAC policy templates needed, "
            "ordered by number of subcategories they cover (most impactful first)."
        ),
    )


class RoadmapValidationResult(BaseModel):
    """Validation result for the improvement roadmap."""

    is_acceptable: bool = Field(
        description="True if the roadmap is acceptable. False if there are issues.",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Specific problems found. Empty if is_acceptable is True.",
    )

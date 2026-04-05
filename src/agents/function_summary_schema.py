"""
Pydantic schemas for NIST function-level gap report summarization
and validation.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class FunctionGapSummary(BaseModel):
    """Structured executive summary of a single NIST function's gap analysis."""

    function_name: str = Field(
        description="NIST CSF function name, e.g. 'Govern'",
    )
    executive_summary: str = Field(
        description=(
            "A 3-5 sentence executive-level summary of the gap analysis "
            "findings for this function. Include the overall maturity, "
            "highlight whether the policy adequately covers this function, "
            "and note the most critical gaps."
        ),
    )
    maturity_rating: str = Field(
        description=(
            "Overall maturity rating for this function (e.g. "
            "'Fully Implemented', 'Substantially Implemented', "
            "'Partially Implemented', 'Not Started', "
            "or 'N/A — No subcategories in scope')."
        ),
    )
    total_subcategories: int = Field(
        description="Total number of subcategories for this function.",
    )
    in_scope_count: int = Field(
        description="Number of subcategories that are in scope for this policy.",
    )
    addressed_count: int = Field(
        description="Number of in-scope subcategories fully addressed.",
    )
    partially_addressed_count: int = Field(
        description="Number of in-scope subcategories partially addressed.",
    )
    not_addressed_count: int = Field(
        description="Number of in-scope subcategories not addressed.",
    )
    out_of_scope_count: int = Field(
        description="Number of subcategories out of scope for this policy.",
    )
    critical_gaps: list[str] = Field(
        description=(
            "Top 3-5 most critical gaps, each as a concise sentence. "
            "Focus on 'Not Addressed' subcategories first, then "
            "'Partially Addressed'. Include the subcategory ID."
        ),
    )
    key_recommendations: list[str] = Field(
        description=(
            "Top 3-5 actionable recommendations to close the most "
            "important gaps. Each should be specific and reference "
            "what needs to be added to the policy."
        ),
    )
    required_policy_documents: list[str] = Field(
        description=(
            "List of missing CIS MS-ISAC policy template documents "
            "that would be needed to cover out-of-scope subcategories. "
            "Empty list if all are covered."
        ),
    )


class SummaryValidationResult(BaseModel):
    """Result of validating a function gap summary against the source report."""

    is_acceptable: bool = Field(
        description=(
            "True if the summary is accurate, complete, and high-quality. "
            "False if there are issues that require regeneration."
        ),
    )
    issues: list[str] = Field(
        default_factory=list,
        description=(
            "List of specific problems found. Empty if is_acceptable is True. "
            "Each issue should clearly state what is wrong and what the "
            "correct value or content should be."
        ),
    )


class MasterGapSummary(BaseModel):
    """Unified executive summary across all 6 NIST CSF functions."""

    executive_summary: str = Field(
        description=(
            "A 5-7 sentence executive-level summary of the overall gap "
            "analysis across all NIST CSF functions. Cover the overall "
            "maturity, highlight the strongest and weakest functions, "
            "and note the most critical cross-cutting findings."
        ),
    )
    overall_maturity: str = Field(
        description=(
            "Aggregated overall maturity rating across all functions "
            "(e.g. 'Not Started', 'Partially Implemented', etc.)."
        ),
    )
    total_subcategories: int = Field(
        description="Total subcategories across all 6 functions.",
    )
    total_in_scope: int = Field(
        description="Total in-scope subcategories across all functions.",
    )
    total_addressed: int = Field(
        description="Total fully addressed subcategories across all functions.",
    )
    total_partially_addressed: int = Field(
        description="Total partially addressed subcategories across all functions.",
    )
    total_not_addressed: int = Field(
        description="Total not-addressed subcategories across all functions.",
    )
    total_out_of_scope: int = Field(
        description="Total out-of-scope subcategories across all functions.",
    )
    strongest_function: str = Field(
        description=(
            "Name of the NIST function with the best coverage "
            "(highest ratio of addressed subcategories). "
            "'N/A' if no function has any addressed subcategories."
        ),
    )
    weakest_function: str = Field(
        description=(
            "Name of the NIST function with the worst coverage "
            "(most not-addressed in-scope subcategories)."
        ),
    )
    top_critical_gaps: list[str] = Field(
        description=(
            "Top 5 most critical gaps across ALL functions, each as a "
            "concise sentence including the subcategory ID and function name."
        ),
    )
    top_recommendations: list[str] = Field(
        description=(
            "Top 5 actionable recommendations across ALL functions, "
            "prioritized by impact. Each should be specific."
        ),
    )
    missing_policy_documents: list[str] = Field(
        description=(
            "Deduplicated list of missing CIS MS-ISAC policy template "
            "documents needed across all functions."
        ),
    )
    remediation_priorities: list[str] = Field(
        description=(
            "3-5 prioritized remediation action items ordered by urgency "
            "and impact. E.g. 'Immediate (0-30 days): ...', "
            "'Short-term (30-90 days): ...'."
        ),
    )

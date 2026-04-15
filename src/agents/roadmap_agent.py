"""
Improvement Roadmap Agent — multi-agent pipeline that produces a prioritized
remediation roadmap from gap analysis results.

Pipeline:
  1. Planner: categorize gaps into priority tiers with action items
  2. Detailer: enrich action items with specifics, success criteria, dependencies
  3. Validator: code checks (all gaps covered, real IDs) + LLM checks (specificity)
  4. Orchestrator: planner → validate → detailer → validate → output
"""

from __future__ import annotations

import logging

from llm import create_llm
from agents.nist_gap_agents import SubcategoryAssessment
from agents.function_summary_schema import FunctionGapSummary
from agents.text_summarizer import summarize_lossless
from agents.roadmap_schema import (
    ImprovementRoadmap,
    RoadmapValidationResult,
)
from prompts.roadmap_prompt import (
    ROADMAP_PLANNER_SYSTEM,
    ROADMAP_DETAILER_SYSTEM,
    ROADMAP_VALIDATOR_SYSTEM,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
LLM_INVOKE_RETRIES = 3


def _invoke_with_retries(structured_llm, messages, retries=LLM_INVOKE_RETRIES):
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return structured_llm.invoke(messages)
        except Exception as exc:
            last_exc = exc
            if attempt < retries:
                logger.warning(
                    "    LLM invoke attempt %d/%d failed: %s — retrying",
                    attempt,
                    retries,
                    exc,
                )
            else:
                logger.error(
                    "    LLM invoke failed after %d attempts: %s", retries, exc
                )
    raise last_exc


# ---------------------------------------------------------------------------
# Data formatting helpers
# ---------------------------------------------------------------------------


def _format_gaps_for_prompt(
    all_assessments: dict[str, list[SubcategoryAssessment]],
) -> tuple[str, set[str]]:
    """Format actionable gaps into a text block for the planner prompt.

    Returns (formatted_text, set_of_valid_ids).
    """
    parts: list[str] = []
    valid_ids: set[str] = set()

    for function_name, assessments in all_assessments.items():
        actionable = [
            a
            for a in assessments
            if a.status in ("Not Addressed", "Partially Addressed")
        ]
        if not actionable:
            continue

        parts.append(f"### {function_name} Function\n")
        for a in actionable:
            valid_ids.add(a.subcategory_id)
            # Summarize the recommendation inline — it can be 500+ chars and
            # cutting it mid-sentence risks losing specific remediation steps.
            from agents.text_summarizer import summarize_lossless

            rec_compressed = summarize_lossless(
                a.recommendation,
                context_hint=f"NIST {a.subcategory_id} remediation recommendation for roadmap",
                threshold=2_000,
            )
            parts.append(
                f"- **{a.subcategory_id}** [{a.status}]: {a.gap}\n"
                f"  Recommendation: {rec_compressed}"
            )
        parts.append("")

    return "\n".join(parts), valid_ids


def _format_summaries_for_prompt(
    all_summaries: dict[str, FunctionGapSummary],
) -> str:
    """Format per-function summaries for context."""
    parts: list[str] = []
    for name, s in all_summaries.items():
        if s.in_scope_count == 0:
            continue
        parts.append(
            f"- **{name}**: {s.maturity_rating} — "
            f"{s.in_scope_count} in scope, {s.not_addressed_count} not addressed, "
            f"{s.partially_addressed_count} partially addressed"
        )
    return "\n".join(parts)


def _collect_missing_docs(
    all_summaries: dict[str, FunctionGapSummary],
) -> list[str]:
    """Deduplicated missing policy documents across all functions."""
    docs: set[str] = set()
    for s in all_summaries.values():
        docs.update(s.required_policy_documents)
    return sorted(docs)


# ---------------------------------------------------------------------------
# Agent 1: Planner
# ---------------------------------------------------------------------------


def run_roadmap_planner(
    all_assessments: dict[str, list[SubcategoryAssessment]],
    all_summaries: dict[str, FunctionGapSummary],
    prior_issues: list[str] | None = None,
) -> ImprovementRoadmap:
    """Generate a tiered improvement roadmap from gap analysis results."""
    llm = create_llm()
    structured_llm = llm.with_structured_output(ImprovementRoadmap)

    gaps_text, _ = _format_gaps_for_prompt(all_assessments)
    summaries_text = _format_summaries_for_prompt(all_summaries)
    missing_docs = _collect_missing_docs(all_summaries)
    docs_text = "\n".join(f"- {d}" for d in missing_docs)

    # Compress gaps_text — it can grow to 3K+ chars with many gaps.
    # The gap IDs are critical so summarize_lossless will retry until they survive.
    gaps_input = summarize_lossless(
        gaps_text,
        context_hint="NIST CSF in-scope gaps with recommendations for roadmap planning",
        threshold=4_000,
    )

    prompt = f"""Create a prioritized improvement roadmap from these NIST CSF gap analysis results.

## Per-Function Maturity

{summaries_text}

## All In-Scope Gaps (must ALL appear in the roadmap)

{gaps_input}

## Missing Policy Documents (for Medium/Long-term tiers)

{docs_text}

## Instructions

Assign EVERY gap above to a tier. Create 3-4 tiers (Immediate, Short-term,
Medium-term, and optionally Long-term). Each action item needs: title, NIST IDs,
description, responsible party, effort, success criteria, and dependencies.
"""

    if prior_issues:
        issues_text = "\n".join(f"  - {issue}" for issue in prior_issues)
        prompt += f"""
## IMPORTANT — Fix These Issues From Previous Attempt
{issues_text}
"""

    logger.info("  Roadmap Planner: Generating tiered roadmap")
    logger.debug("  Planner prompt (%d chars):\n%s", len(prompt), prompt)

    result = _invoke_with_retries(
        structured_llm,
        [
            {"role": "system", "content": ROADMAP_PLANNER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )

    # Code-set the missing docs list (same principle as master summary)
    result.missing_policy_documents = missing_docs

    logger.info(
        "  Roadmap Planner: Generated %d tiers with %d total action items",
        len(result.tiers),
        sum(len(t.action_items) for t in result.tiers),
    )
    return result


# ---------------------------------------------------------------------------
# Agent 2: Detailer
# ---------------------------------------------------------------------------


def run_roadmap_detailer(
    roadmap: ImprovementRoadmap,
    all_assessments: dict[str, list[SubcategoryAssessment]],
    prior_issues: list[str] | None = None,
) -> ImprovementRoadmap:
    """Enrich roadmap action items with detailed specifics."""
    llm = create_llm()
    structured_llm = llm.with_structured_output(ImprovementRoadmap)

    # Format the draft roadmap as text
    roadmap_text_parts: list[str] = []
    for tier in roadmap.tiers:
        roadmap_text_parts.append(f"### {tier.tier_name}")
        for item in tier.action_items:
            roadmap_text_parts.append(
                f"- **{item.title}** (NIST: {', '.join(item.nist_ids)})\n"
                f"  Description: {item.description}\n"
                f"  Responsible: {item.responsible}\n"
                f"  Effort: {item.effort}\n"
                f"  Success Criteria: {item.success_criteria}\n"
                f"  Dependencies: {item.dependencies}"
            )
        roadmap_text_parts.append("")
    roadmap_text = "\n".join(roadmap_text_parts)

    # Get detailed gap context for enrichment
    gaps_text, _ = _format_gaps_for_prompt(all_assessments)

    # Compress both inputs before injecting — roadmap_text can exceed 3K chars
    # for a 12-item roadmap, and gaps_text adds another 2K.
    roadmap_input = summarize_lossless(
        roadmap_text,
        context_hint="improvement roadmap draft with tiers, action items, and NIST IDs",
        threshold=4_000,
    )
    gaps_input = summarize_lossless(
        gaps_text,
        context_hint="NIST CSF in-scope gaps with recommendations for detailing context",
        threshold=4_000,
    )

    prompt = f"""Enrich this improvement roadmap with more detailed, actionable content.

## Draft Roadmap to Enrich

{roadmap_input}

## Original Gap Details (for context)

{gaps_input}

## Instructions

Keep all tier assignments and NIST IDs exactly as they are. Enrich each action item with:
- More specific step-by-step descriptions
- Concrete, measurable success criteria (auditable outcomes)
- Realistic dependencies between items
- Appropriate effort estimates

Return the complete roadmap with all tiers and enriched action items.
"""

    if prior_issues:
        issues_text = "\n".join(f"  - {issue}" for issue in prior_issues)
        prompt += f"""
## IMPORTANT — Fix These Issues From Previous Attempt
{issues_text}
"""

    logger.info("  Roadmap Detailer: Enriching action items")
    logger.debug("  Detailer prompt (%d chars):\n%s", len(prompt), prompt)

    result = _invoke_with_retries(
        structured_llm,
        [
            {"role": "system", "content": ROADMAP_DETAILER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )

    # Preserve code-set fields
    result.missing_policy_documents = roadmap.missing_policy_documents

    logger.info("  Roadmap Detailer: Enriched %d tiers", len(result.tiers))
    return result


# ---------------------------------------------------------------------------
# Validator (code + LLM)
# ---------------------------------------------------------------------------


def validate_roadmap(
    roadmap: ImprovementRoadmap,
    all_assessments: dict[str, list[SubcategoryAssessment]],
) -> RoadmapValidationResult:
    """Validate the roadmap: code checks first, then LLM quality check."""

    # Collect all valid gap IDs
    expected_ids: set[str] = set()
    for assessments in all_assessments.values():
        for a in assessments:
            if a.status in ("Not Addressed", "Partially Addressed"):
                expected_ids.add(a.subcategory_id)

    # Collect all IDs referenced in the roadmap
    roadmap_ids: set[str] = set()
    for tier in roadmap.tiers:
        for item in tier.action_items:
            roadmap_ids.update(item.nist_ids)

    code_issues: list[str] = []

    # Check: every gap ID appears in the roadmap.
    # Enforce 90% coverage — missing gaps are a hard failure, not just a warning.
    missing_ids = expected_ids - roadmap_ids
    coverage = (
        len(expected_ids - missing_ids) / len(expected_ids) if expected_ids else 1.0
    )
    if missing_ids and coverage < 0.9:
        code_issues.append(
            f"{len(missing_ids)} gap IDs not in roadmap (coverage {coverage:.0%} < 90%): "
            f"{', '.join(sorted(missing_ids))}. "
            f"Every gap must be assigned to a tier."
        )
    elif missing_ids:
        # Between 90-100% — log a warning but don't block
        logger.warning(
            "  Roadmap: %d gap IDs not explicitly in roadmap: %s",
            len(missing_ids),
            ", ".join(sorted(missing_ids)),
        )

    # Check: no fabricated NIST IDs.
    # A fabricated ID is one that appears in the roadmap but is NOT in the
    # known assessment set. We check set membership only — no regex needed
    # because the valid set is the authoritative ground truth.
    all_valid_ids: set[str] = set()
    for assessments in all_assessments.values():
        for a in assessments:
            all_valid_ids.add(a.subcategory_id)

    fabricated = {rid for rid in roadmap_ids if rid not in all_valid_ids}
    if fabricated:
        code_issues.append(
            f"Fabricated NIST IDs in roadmap: {', '.join(sorted(fabricated))}. "
            f"Valid IDs are: {', '.join(sorted(expected_ids))}"
        )

    # Check: at least 2 tiers
    if len(roadmap.tiers) < 2:
        code_issues.append(f"Only {len(roadmap.tiers)} tier(s) — need at least 2.")

    # Check: at least 1 action item total
    total_items = sum(len(t.action_items) for t in roadmap.tiers)
    if total_items == 0:
        code_issues.append("No action items in roadmap.")

    if code_issues:
        logger.warning(
            "  Roadmap Validator: REJECTED by code — %d issues", len(code_issues)
        )
        for issue in code_issues:
            logger.warning("    - %s", issue)
        return RoadmapValidationResult(is_acceptable=False, issues=code_issues)

    logger.info(
        "  Roadmap Validator: code checks passed ✓ (%d gaps covered, %d items)",
        len(roadmap_ids & expected_ids),
        total_items,
    )

    # LLM quality check
    llm = create_llm()
    structured_llm = llm.with_structured_output(RoadmapValidationResult)

    # Summarize the roadmap for the LLM (keep it short)
    summary_parts: list[str] = []
    for tier in roadmap.tiers:
        for item in tier.action_items:
            summary_parts.append(
                f"- [{tier.tier_name}] {item.title}: {item.success_criteria}"
            )
    summary_text = "\n".join(summary_parts)

    prompt = f"""Check this improvement roadmap for quality.

## Action Items and Success Criteria

{summary_text}

## Instructions
1. Check if text is coherent and free of garbled content.
2. Check if any action item is vague platitude with no concrete steps.
3. Check if any success criteria is unmeasurable.
If no errors found, set is_acceptable=true with empty issues list.
"""

    logger.info("  Roadmap Validator: LLM checking quality")

    try:
        result = _invoke_with_retries(
            structured_llm,
            [
                {"role": "system", "content": ROADMAP_VALIDATOR_SYSTEM},
                {"role": "user", "content": prompt},
            ],
        )
        if result.is_acceptable:
            logger.info("  Roadmap Validator: ACCEPTED ✓")
        else:
            logger.warning(
                "  Roadmap Validator: REJECTED — %d issues", len(result.issues)
            )
            for issue in result.issues:
                logger.warning("    - %s", issue)
        return result
    except Exception as exc:
        logger.warning("  Roadmap Validator failed: %s — accepting", exc)
        return RoadmapValidationResult(is_acceptable=True, issues=[])


# ---------------------------------------------------------------------------
# Orchestrator: Planner → Validate → Detailer → Validate
# ---------------------------------------------------------------------------


def run_roadmap_with_validation(
    all_assessments: dict[str, list[SubcategoryAssessment]],
    all_summaries: dict[str, FunctionGapSummary],
) -> ImprovementRoadmap:
    """
    Generate a validated improvement roadmap.

    Two-stage pipeline:
      Stage 1: Planner generates tier structure → validate → retry
      Stage 2: Detailer enriches action items → validate → retry
    """
    logger.info("=" * 40)
    logger.info("Generating Improvement Roadmap (multi-agent pipeline)")
    logger.info("=" * 40)

    # Stage 1: Plan the tiers
    logger.info("  Stage 1: Roadmap Planner")
    roadmap = run_roadmap_planner(all_assessments, all_summaries)

    for attempt in range(1, MAX_RETRIES + 1):
        validation = validate_roadmap(roadmap, all_assessments)
        if validation.is_acceptable:
            logger.info("  Planner output accepted on attempt %d ✓", attempt)
            break
        logger.warning(
            "  Planner output rejected (attempt %d/%d) — regenerating",
            attempt,
            MAX_RETRIES,
        )
        roadmap = run_roadmap_planner(
            all_assessments,
            all_summaries,
            prior_issues=validation.issues,
        )
    else:
        logger.warning("  Planner: max retries reached — using last generated")

    # Stage 2: Detail the action items
    logger.info("  Stage 2: Roadmap Detailer")
    detailed = run_roadmap_detailer(roadmap, all_assessments)

    for attempt in range(1, MAX_RETRIES + 1):
        validation = validate_roadmap(detailed, all_assessments)
        if validation.is_acceptable:
            logger.info("  Detailer output accepted on attempt %d ✓", attempt)
            return detailed
        logger.warning(
            "  Detailer output rejected (attempt %d/%d) — regenerating",
            attempt,
            MAX_RETRIES,
        )
        detailed = run_roadmap_detailer(
            roadmap,
            all_assessments,
            prior_issues=validation.issues,
        )

    logger.warning("  Detailer: max retries reached — using last generated")
    return detailed


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------


def render_improvement_roadmap(roadmap: ImprovementRoadmap) -> str:
    """Render an ImprovementRoadmap into a clean markdown document."""
    lines: list[str] = []

    lines.append("# NIST CSF Improvement Roadmap")
    lines.append("*(Aligned with CIS MS-ISAC NIST CSF Policy Template Guide 2024)*\n")

    lines.append("## Executive Summary\n")
    lines.append(roadmap.executive_summary)
    lines.append("")

    for tier in roadmap.tiers:
        lines.append(f"## {tier.tier_name}\n")
        lines.append(f"*{tier.rationale}*\n")

        for i, item in enumerate(tier.action_items, 1):
            nist_refs = ", ".join(item.nist_ids)
            lines.append(
                f"### {tier.tier_name.split('(')[0].strip()} — {i}. {item.title}\n"
            )
            lines.append(f"- **NIST Reference**: {nist_refs}")
            lines.append(f"- **Description**: {item.description}")
            lines.append(f"- **Responsible**: {item.responsible}")
            lines.append(f"- **Effort**: {item.effort}")
            lines.append(f"- **Success Criteria**: {item.success_criteria}")
            lines.append(f"- **Dependencies**: {item.dependencies}")
            lines.append("")

    if roadmap.missing_policy_documents:
        lines.append("## Missing Policy Documents\n")
        lines.append(
            "The following CIS MS-ISAC policy templates are needed for full "
            "NIST CSF coverage. Develop these in Medium-term and Long-term phases:\n"
        )
        for i, doc in enumerate(roadmap.missing_policy_documents, 1):
            lines.append(f"{i}. {doc}")
        lines.append("")

    return "\n".join(lines)

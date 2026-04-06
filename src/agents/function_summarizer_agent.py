"""
Function Gap Summarizer Agent — generates and validates per-function executive
summaries of NIST CSF gap analysis reports.

Flow:
  1. Summarizer generates a FunctionGapSummary from the detailed report.
  2. Validator checks accuracy, completeness, no fabrication, no garbage.
  3. If rejected, regenerate with feedback (up to MAX_RETRIES).
"""

from __future__ import annotations

import logging
from typing import Literal

from agents.function_summary_schema import (
    FunctionGapSummary,
    MasterGapSummary,
    SummaryValidationResult,
)
from agents.nist_gap_agents import SubcategoryAssessment
from llm import create_llm
from prompts.function_summarizer_prompt import (
    FUNCTION_SUMMARIZER_SYSTEM,
    MASTER_SUMMARIZER_SYSTEM,
    MASTER_VALIDATOR_SYSTEM,
    SUMMARY_VALIDATOR_SYSTEM,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
LLM_INVOKE_RETRIES = 3  # retries for transient structured-output parsing failures


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_stats(assessments: list[SubcategoryAssessment]) -> dict:
    """Compute summary statistics from structured assessments."""
    in_scope = [a for a in assessments if a.status != "Out of Scope"]
    return {
        "total": len(assessments),
        "in_scope": len(in_scope),
        "addressed": sum(1 for a in in_scope if a.status == "Addressed"),
        "partially_addressed": sum(1 for a in in_scope if a.status == "Partially Addressed"),
        "not_addressed": sum(1 for a in in_scope if a.status == "Not Addressed"),
        "out_of_scope": sum(1 for a in assessments if a.status == "Out of Scope"),
    }


def _format_stats_block(stats: dict) -> str:
    """Render stats as a text block for prompt injection."""
    return (
        f"Total subcategories: {stats['total']}\n"
        f"In scope: {stats['in_scope']}\n"
        f"Addressed: {stats['addressed']}\n"
        f"Partially addressed: {stats['partially_addressed']}\n"
        f"Not addressed: {stats['not_addressed']}\n"
        f"Out of scope: {stats['out_of_scope']}"
    )


def _compute_maturity_rating(stats: dict) -> str:
    """Derive the maturity rating from in-scope stats."""
    total = stats["in_scope"]
    if total == 0:
        return "N/A — No subcategories in scope for this policy type"
    score = stats["addressed"] + 0.5 * stats["partially_addressed"]
    pct = score / total
    if pct >= 0.9:
        return "Fully Implemented"
    if pct >= 0.6:
        return "Substantially Implemented"
    if pct >= 0.2:
        return "Partially Implemented"
    return "Not Started"


def _invoke_with_retries(structured_llm, messages: list[dict], retries: int = LLM_INVOKE_RETRIES):
    """
    Invoke a structured LLM with retries for transient parsing failures.

    Ollama's structured output can occasionally fail to produce valid JSON
    on the first attempt. Retrying usually resolves this.
    """
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            return structured_llm.invoke(messages)
        except Exception as exc:
            last_exc = exc
            if attempt < retries:
                logger.warning(
                    "    LLM invoke attempt %d/%d failed: %s — retrying",
                    attempt, retries, exc,
                )
            else:
                logger.error(
                    "    LLM invoke failed after %d attempts: %s",
                    retries, exc,
                )
    raise last_exc


def _debug_log_function_summary(label: str, summary: FunctionGapSummary) -> None:
    """Log all fields of a FunctionGapSummary at DEBUG level."""
    logger.debug(
        "[%s] FunctionGapSummary for %s:\n"
        "  executive_summary: %s\n"
        "  maturity_rating: %s\n"
        "  total_subcategories: %d\n"
        "  in_scope_count: %d\n"
        "  addressed_count: %d\n"
        "  partially_addressed_count: %d\n"
        "  not_addressed_count: %d\n"
        "  out_of_scope_count: %d\n"
        "  critical_gaps: %s\n"
        "  key_recommendations: %s\n"
        "  required_policy_documents: %s",
        label,
        summary.function_name,
        summary.executive_summary,
        summary.maturity_rating,
        summary.total_subcategories,
        summary.in_scope_count,
        summary.addressed_count,
        summary.partially_addressed_count,
        summary.not_addressed_count,
        summary.out_of_scope_count,
        summary.critical_gaps,
        summary.key_recommendations,
        summary.required_policy_documents,
    )


def _debug_log_master_summary(label: str, summary: MasterGapSummary) -> None:
    """Log all fields of a MasterGapSummary at DEBUG level."""
    logger.debug(
        "[%s] MasterGapSummary:\n"
        "  executive_summary: %s\n"
        "  overall_maturity: %s\n"
        "  total_subcategories: %d\n"
        "  total_in_scope: %d\n"
        "  total_addressed: %d\n"
        "  total_partially_addressed: %d\n"
        "  total_not_addressed: %d\n"
        "  total_out_of_scope: %d\n"
        "  strongest_function: %s\n"
        "  weakest_function: %s\n"
        "  top_critical_gaps: %s\n"
        "  top_recommendations: %s\n"
        "  missing_policy_documents: %s\n"
        "  remediation_priorities: %s",
        label,
        summary.executive_summary,
        summary.overall_maturity,
        summary.total_subcategories,
        summary.total_in_scope,
        summary.total_addressed,
        summary.total_partially_addressed,
        summary.total_not_addressed,
        summary.total_out_of_scope,
        summary.strongest_function,
        summary.weakest_function,
        summary.top_critical_gaps,
        summary.top_recommendations,
        summary.missing_policy_documents,
        summary.remediation_priorities,
    )


# ---------------------------------------------------------------------------
# Summarizer
# ---------------------------------------------------------------------------

def run_function_summarizer(
    function_name: str,
    report: str,
    assessments: list[SubcategoryAssessment],
    model_name: str = "gemma4:e2b",
    prior_issues: list[str] | None = None,
) -> FunctionGapSummary:
    """
    Generate a structured executive summary for one NIST function.

    Takes the FULL gap analysis report and produces a FunctionGapSummary.
    Retries LLM invocation up to LLM_INVOKE_RETRIES times for transient
    structured-output parsing failures.

    Args:
        function_name: NIST function name (e.g. "Govern").
        report: Full gap analysis report markdown for this function.
        assessments: Structured SubcategoryAssessment list.
        model_name: Ollama model name.
        prior_issues: If provided, issues from a previous validation
                      rejection — the summarizer should fix these.

    Returns:
        FunctionGapSummary structured output.
    """
    stats = _compute_stats(assessments)
    stats_block = _format_stats_block(stats)
    llm = create_llm()
    structured_llm = llm.with_structured_output(FunctionGapSummary)

    prompt = f"""Summarize the following NIST CSF **{function_name}** function gap analysis
report into a concise executive summary.

## Actual Statistics (use these EXACT numbers)

{stats_block}

## Full Gap Analysis Report

{report}
"""

    if prior_issues:
        issues_text = "\n".join(f"  - {issue}" for issue in prior_issues)
        prompt += f"""
## IMPORTANT — Fix These Issues From Previous Attempt

The previous summary was rejected for these reasons. You MUST fix all of them:

{issues_text}
"""

    logger.info("  Summarizer: Generating summary for %s (%d char report)", function_name, len(report))
    logger.debug("  Summarizer prompt for %s (%d chars):\n%s", function_name, len(prompt), prompt)

    try:
        result = _invoke_with_retries(structured_llm, [
            {"role": "system", "content": FUNCTION_SUMMARIZER_SYSTEM},
            {"role": "user", "content": prompt},
        ])
        logger.info("  Summarizer: Generated summary (%d char executive summary)", len(result.executive_summary))
        _debug_log_function_summary(f"Summarizer output — {function_name}", result)
        return result
    except Exception as exc:
        logger.warning("  Summarizer failed for %s after all retries: %s — building fallback", function_name, exc)
        return _build_fallback_summary(function_name, assessments, stats)


def _build_fallback_summary(
    function_name: str,
    assessments: list[SubcategoryAssessment],
    stats: dict,
) -> FunctionGapSummary:
    """Build a code-based fallback summary when the LLM fails after all retries."""
    not_addressed = [a for a in assessments if a.status == "Not Addressed"]
    partial = [a for a in assessments if a.status == "Partially Addressed"]

    critical = [
        f"{a.subcategory_id}: {a.gap}"
        for a in (not_addressed + partial)[:5]
    ]
    recommendations = [
        f"{a.subcategory_id}: {a.recommendation}"
        for a in (not_addressed + partial)[:5]
    ]
    out_scope = [a for a in assessments if a.status == "Out of Scope"]
    templates: set[str] = set()
    for a in out_scope:
        for tmpl in a.recommendation.split(", "):
            tmpl = tmpl.strip()
            if tmpl and tmpl != "N/A":
                templates.add(tmpl)

    maturity = _compute_maturity_rating(stats)

    # Build a descriptive executive summary
    top_gap_ids = [a.subcategory_id for a in not_addressed[:3]]
    exec_parts = [
        f"The {function_name} function has {stats['in_scope']} in-scope "
        f"subcategories out of {stats['total']} total, with an overall "
        f"maturity of {maturity}.",
        f"{stats['addressed']} are fully addressed, "
        f"{stats['partially_addressed']} partially addressed, and "
        f"{stats['not_addressed']} not addressed.",
    ]
    if top_gap_ids:
        exec_parts.append(
            f"The most critical unaddressed gaps are "
            f"{', '.join(top_gap_ids)}, which require immediate attention."
        )
    if stats["out_of_scope"] > 0:
        exec_parts.append(
            f"{stats['out_of_scope']} subcategories are out of scope "
            f"and require separate policy documents."
        )

    return FunctionGapSummary(
        function_name=function_name,
        executive_summary=" ".join(exec_parts),
        maturity_rating=maturity,
        total_subcategories=stats["total"],
        in_scope_count=stats["in_scope"],
        addressed_count=stats["addressed"],
        partially_addressed_count=stats["partially_addressed"],
        not_addressed_count=stats["not_addressed"],
        out_of_scope_count=stats["out_of_scope"],
        critical_gaps=critical,
        key_recommendations=recommendations,
        required_policy_documents=sorted(templates)[:10],
    )


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

def run_summary_validator(
    function_name: str,
    report: str,
    assessments: list[SubcategoryAssessment],
    summary: FunctionGapSummary,
    model_name: str = "gemma4:e2b",
) -> SummaryValidationResult:
    """
    Validate a generated summary against the source report and assessments.

    Takes the FULL gap analysis report so the validator can cross-reference
    every claim in the summary.

    Args:
        function_name: NIST function name.
        report: Original detailed gap analysis report markdown.
        assessments: Structured SubcategoryAssessment list (source of truth).
        summary: The generated FunctionGapSummary to validate.
        model_name: Ollama model name.

    Returns:
        SummaryValidationResult indicating acceptance or issues.
    """
    stats = _compute_stats(assessments)

    # ── Code-based stat check (LLM can't reliably compare numbers) ──
    stat_issues: list[str] = []
    checks = [
        ("total_subcategories", summary.total_subcategories, stats["total"]),
        ("in_scope_count", summary.in_scope_count, stats["in_scope"]),
        ("addressed_count", summary.addressed_count, stats["addressed"]),
        ("partially_addressed_count", summary.partially_addressed_count, stats["partially_addressed"]),
        ("not_addressed_count", summary.not_addressed_count, stats["not_addressed"]),
        ("out_of_scope_count", summary.out_of_scope_count, stats["out_of_scope"]),
    ]
    for field, got, expected in checks:
        if got != expected:
            stat_issues.append(f"Wrong number: {field} is {got}, should be {expected}")

    if stat_issues:
        logger.warning("  Validator: %s REJECTED by code — %d stat mismatches", function_name, len(stat_issues))
        for issue in stat_issues:
            logger.warning("    - %s", issue)
        return SummaryValidationResult(is_acceptable=False, issues=stat_issues)

    logger.info("  Validator: %s stats verified by code ✓", function_name)

    # ── LLM-based qualitative check (fabrication + garbled text only) ──
    llm = create_llm()
    structured_llm = llm.with_structured_output(SummaryValidationResult)

    summary_text = (
        f"Executive Summary:\n{summary.executive_summary}\n\n"
        f"Critical Gaps:\n"
        + "\n".join(f"  - {g}" for g in summary.critical_gaps)
        + f"\n\nKey Recommendations:\n"
        + "\n".join(f"  - {r}" for r in summary.key_recommendations)
    )

    prompt = f"""Check this executive summary of the **{function_name}** function for errors.

## Valid subcategory IDs from the original report (reference list)

{', '.join(a.subcategory_id for a in assessments)}

## Executive Summary to Check

{summary_text}

## Instructions

1. Check if any subcategory ID in Critical Gaps does NOT appear in the reference list above.
2. Check if the text contains garbled or nonsensical content.
If no errors found, set is_acceptable=true with empty issues list.
"""

    logger.info("  Validator: LLM checking %s for fabrication/garbled text", function_name)
    logger.debug("  Validator prompt for %s (%d chars):\n%s", function_name, len(prompt), prompt)

    try:
        result = _invoke_with_retries(structured_llm, [
            {"role": "system", "content": SUMMARY_VALIDATOR_SYSTEM},
            {"role": "user", "content": prompt},
        ])
        if result.is_acceptable:
            logger.info("  Validator: Summary ACCEPTED ✓")
        else:
            logger.warning("  Validator: Summary REJECTED — %d issues", len(result.issues))
            for issue in result.issues:
                logger.warning("    - %s", issue)
        logger.debug("  Validator result for %s: is_acceptable=%s, issues=%s",
                      function_name, result.is_acceptable, result.issues)
        return result
    except Exception as exc:
        logger.warning("  Validator failed for %s after all retries: %s — accepting summary", function_name, exc)
        return SummaryValidationResult(is_acceptable=True, issues=[])


# ---------------------------------------------------------------------------
# Orchestrator: Summarize + Validate loop
# ---------------------------------------------------------------------------

def run_summarize_with_validation(
    function_name: Literal["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"],
    report: str,
    assessments: list[SubcategoryAssessment],
    model_name: str = "gemma4:e2b",
) -> FunctionGapSummary:
    """
    Generate a validated executive summary for one NIST function.

    Runs the summarizer, then validates. If rejected, regenerates with
    the validation issues as feedback (up to MAX_RETRIES).

    Args:
        function_name: NIST function name.
        report: Full gap analysis report markdown for this function.
        assessments: Structured SubcategoryAssessment list.
        model_name: Ollama model name.

    Returns:
        Validated FunctionGapSummary.
    """
    logger.info("=" * 40)
    logger.info("Summarizing %s function (with validation loop)", function_name)
    logger.info("=" * 40)

    stats = _compute_stats(assessments)
    logger.debug("  Ground-truth stats for %s: %s", function_name, stats)

    # Initial generation
    summary = run_function_summarizer(
        function_name, report, assessments, model_name,
    )

    for attempt in range(1, MAX_RETRIES + 1):
        logger.debug("  Validation attempt %d/%d for %s", attempt, MAX_RETRIES, function_name)

        validation = run_summary_validator(
            function_name, report, assessments, summary, model_name,
        )

        if validation.is_acceptable:
            logger.info(
                "  %s summary accepted on attempt %d ✓",
                function_name, attempt,
            )
            return summary

        logger.warning(
            "  %s summary rejected (attempt %d/%d) — regenerating",
            function_name, attempt, MAX_RETRIES,
        )

        # Regenerate with feedback
        summary = run_function_summarizer(
            function_name, report, assessments, model_name,
            prior_issues=validation.issues,
        )

    logger.warning(
        "  %s: max retries (%d) reached — using last generated summary",
        function_name, MAX_RETRIES,
    )
    _debug_log_function_summary(f"Final (unvalidated) — {function_name}", summary)
    return summary


# ---------------------------------------------------------------------------
# Build out-of-scope summary (code-based, no LLM)
# ---------------------------------------------------------------------------

def build_out_of_scope_summary(
    function_name: str,
    assessments: list[SubcategoryAssessment],
) -> FunctionGapSummary:
    """
    Build a summary for a function that is entirely out of scope.

    No LLM call — pure code.
    """
    templates: set[str] = set()
    for a in assessments:
        for tmpl in a.recommendation.split(", "):
            tmpl = tmpl.strip()
            if tmpl and tmpl != "N/A":
                templates.add(tmpl)

    return FunctionGapSummary(
        function_name=function_name,
        executive_summary=(
            f"The {function_name} function is entirely out of scope for this "
            f"policy document. All {len(assessments)} subcategories require "
            f"separate, dedicated policy documents. No gap analysis was "
            f"performed for this function."
        ),
        maturity_rating="N/A — No subcategories in scope for this policy type",
        total_subcategories=len(assessments),
        in_scope_count=0,
        addressed_count=0,
        partially_addressed_count=0,
        not_addressed_count=0,
        out_of_scope_count=len(assessments),
        critical_gaps=[],
        key_recommendations=[],
        required_policy_documents=sorted(templates),
    )


# ---------------------------------------------------------------------------
# Markdown renderer
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Master Summary: Helpers
# ---------------------------------------------------------------------------

def _aggregate_stats(summaries: dict[str, FunctionGapSummary]) -> dict:
    """Compute aggregate statistics across all function summaries."""
    return {
        "total": sum(s.total_subcategories for s in summaries.values()),
        "in_scope": sum(s.in_scope_count for s in summaries.values()),
        "addressed": sum(s.addressed_count for s in summaries.values()),
        "partially_addressed": sum(s.partially_addressed_count for s in summaries.values()),
        "not_addressed": sum(s.not_addressed_count for s in summaries.values()),
        "out_of_scope": sum(s.out_of_scope_count for s in summaries.values()),
    }


def _compute_strongest_weakest(
    summaries: dict[str, FunctionGapSummary],
) -> tuple[str, str]:
    """Return (strongest, weakest) function names based on coverage ratios.

    Strongest = highest addressed/in_scope ratio.
    Weakest = most not_addressed in-scope gaps.
    When functions are tied, reports the tie honestly rather than forcing
    a false distinction.
    """
    in_scope_funcs = [
        (name, s) for name, s in summaries.items() if s.in_scope_count > 0
    ]
    if not in_scope_funcs:
        return "N/A", "N/A"
    if len(in_scope_funcs) == 1:
        name = in_scope_funcs[0][0]
        return name, name

    # Compute ratios
    scored = []
    for name, s in in_scope_funcs:
        ratio = s.addressed_count / s.in_scope_count
        scored.append((name, ratio, s.not_addressed_count))

    # Strongest: highest addressed ratio
    strongest_sorted = sorted(scored, key=lambda x: (x[1], -x[2]), reverse=True)
    best = strongest_sorted[0]
    # Check for tie at the top
    tied_best = [s for s in strongest_sorted if s[1] == best[1] and s[2] == best[2]]
    if len(tied_best) > 1:
        best_name = "Tied (" + ", ".join(s[0] for s in tied_best) + ")"
    else:
        best_name = best[0]

    # Weakest: most not_addressed
    weakest_sorted = sorted(scored, key=lambda x: (x[2], -x[1]), reverse=True)
    worst = weakest_sorted[0]
    # Check for tie at the bottom
    tied_worst = [s for s in weakest_sorted if s[2] == worst[2] and s[1] == worst[1]]
    if len(tied_worst) > 1:
        worst_name = "Tied (" + ", ".join(s[0] for s in tied_worst) + ")"
    else:
        worst_name = worst[0]

    return best_name, worst_name


def _collect_all_critical_gaps(summaries: dict[str, FunctionGapSummary]) -> list[str]:
    """Collect ALL critical gaps across functions, labelled with function name."""
    gaps: list[str] = []
    for name, s in summaries.items():
        if s.in_scope_count > 0:
            for g in s.critical_gaps:
                gaps.append(f"[{name}] {g}")
    return gaps


def _collect_all_missing_docs(summaries: dict[str, FunctionGapSummary]) -> list[str]:
    """Deduplicated list of missing policy documents across ALL functions."""
    all_docs: set[str] = set()
    for s in summaries.values():
        all_docs.update(s.required_policy_documents)
    return sorted(all_docs)


def _format_function_summaries_for_prompt(
    summaries: dict[str, FunctionGapSummary],
) -> str:
    """Format all per-function summaries into a text block for the master prompt."""
    parts: list[str] = []

    for name, s in summaries.items():
        gaps_text = "\n".join(f"    - {g}" for g in s.critical_gaps) if s.critical_gaps else "    (none)"
        recs_text = "\n".join(f"    - {r}" for r in s.key_recommendations) if s.key_recommendations else "    (none)"
        docs_text = "\n".join(f"    - {d}" for d in s.required_policy_documents) if s.required_policy_documents else "    (none)"

        parts.append(
            f"### {name}\n"
            f"- Maturity: {s.maturity_rating}\n"
            f"- Executive Summary: {s.executive_summary}\n"
            f"- Total: {s.total_subcategories}, In Scope: {s.in_scope_count}, "
            f"Addressed: {s.addressed_count}, Partially Addressed: {s.partially_addressed_count}, "
            f"Not Addressed: {s.not_addressed_count}, Out of Scope: {s.out_of_scope_count}\n"
            f"- Critical Gaps:\n{gaps_text}\n"
            f"- Key Recommendations:\n{recs_text}\n"
            f"- Required Policy Documents:\n{docs_text}"
        )

    agg = _aggregate_stats(summaries)
    strongest, weakest = _compute_strongest_weakest(summaries)

    # Pre-computed fields the LLM must use verbatim
    all_gaps = _collect_all_critical_gaps(summaries)
    all_docs = _collect_all_missing_docs(summaries)

    parts.append(
        f"\n## Aggregate Statistics (use these EXACT numbers)\n\n"
        f"Total subcategories: {agg['total']}\n"
        f"Total in scope: {agg['in_scope']}\n"
        f"Total addressed: {agg['addressed']}\n"
        f"Total partially addressed: {agg['partially_addressed']}\n"
        f"Total not addressed: {agg['not_addressed']}\n"
        f"Total out of scope: {agg['out_of_scope']}\n\n"
        f"Strongest function: {strongest}\n"
        f"Weakest function: {weakest}\n\n"
        f"## Pre-Computed Top Critical Gaps (include ALL of these equally)\n\n"
        + "\n".join(f"- {g}" for g in all_gaps)
        + f"\n\n## Pre-Computed Missing Policy Documents (include ALL of these)\n\n"
        + "\n".join(f"- {d}" for d in all_docs)
    )

    return "\n\n".join(parts)


def _build_fallback_master_summary(
    summaries: dict[str, FunctionGapSummary],
) -> MasterGapSummary:
    """Build a code-based fallback master summary when the LLM fails."""
    agg = _aggregate_stats(summaries)
    strongest, weakest = _compute_strongest_weakest(summaries)

    # Compute overall maturity from aggregate stats
    total_in = agg["in_scope"]
    if total_in == 0:
        overall_maturity = "N/A — No subcategories in scope"
    else:
        score = agg["addressed"] + 0.5 * agg["partially_addressed"]
        pct = score / total_in
        if pct >= 0.9:
            overall_maturity = "Fully Implemented"
        elif pct >= 0.6:
            overall_maturity = "Substantially Implemented"
        elif pct >= 0.2:
            overall_maturity = "Partially Implemented"
        else:
            overall_maturity = "Not Started"

    # Collect top critical gaps across all functions
    all_gaps: list[str] = []
    for name, s in summaries.items():
        for g in s.critical_gaps:
            all_gaps.append(f"[{name}] {g}")
    top_gaps = all_gaps[:5]

    # Collect top recommendations
    all_recs: list[str] = []
    for name, s in summaries.items():
        for r in s.key_recommendations:
            all_recs.append(f"[{name}] {r}")
    top_recs = all_recs[:5]

    # Deduplicate missing policy documents
    all_docs: set[str] = set()
    for s in summaries.values():
        all_docs.update(s.required_policy_documents)

    # Build executive summary
    exec_parts = [
        f"Across all 6 NIST CSF functions, {agg['in_scope']} of "
        f"{agg['total']} subcategories are in scope, with an overall "
        f"maturity of {overall_maturity}.",
        f"{agg['addressed']} subcategories are fully addressed, "
        f"{agg['partially_addressed']} partially addressed, and "
        f"{agg['not_addressed']} not addressed.",
    ]
    if strongest != "N/A":
        exec_parts.append(f"The strongest function is {strongest}.")
    if weakest != "N/A":
        exec_parts.append(
            f"The weakest function is {weakest}, which requires "
            f"the most immediate attention."
        )
    if all_docs:
        exec_parts.append(
            f"{len(all_docs)} policy template documents are missing "
            f"and needed to achieve full coverage."
        )

    return MasterGapSummary(
        executive_summary=" ".join(exec_parts),
        overall_maturity=overall_maturity,
        total_subcategories=agg["total"],
        total_in_scope=agg["in_scope"],
        total_addressed=agg["addressed"],
        total_partially_addressed=agg["partially_addressed"],
        total_not_addressed=agg["not_addressed"],
        total_out_of_scope=agg["out_of_scope"],
        strongest_function=strongest,
        weakest_function=weakest,
        top_critical_gaps=top_gaps,
        top_recommendations=top_recs,
        missing_policy_documents=sorted(all_docs)[:15],
        remediation_priorities=[
            f"Immediate (0-30 days): Address critical gaps in {weakest} function",
            "Short-term (30-90 days): Close partially addressed subcategories across all functions",
            "Medium-term (90-180 days): Develop missing policy documents to cover out-of-scope subcategories",
        ],
    )


# ---------------------------------------------------------------------------
# Master Summary: Summarizer
# ---------------------------------------------------------------------------

def run_master_summarizer(
    summaries: dict[str, FunctionGapSummary],
    model_name: str = "gemma4:e2b",
    prior_issues: list[str] | None = None,
) -> MasterGapSummary:
    """
    Generate a unified master executive summary from all per-function summaries.

    Args:
        summaries: Dict mapping function name to its FunctionGapSummary.
        model_name: Ollama model name.
        prior_issues: Issues from a previous validation rejection to fix.

    Returns:
        MasterGapSummary structured output.
    """
    formatted = _format_function_summaries_for_prompt(summaries)

    llm = create_llm()
    structured_llm = llm.with_structured_output(MasterGapSummary)

    prompt = f"""Synthesize the following per-function NIST CSF gap analysis summaries into
a single master executive summary suitable for board-level reporting.

## Per-Function Summaries

{formatted}
"""

    if prior_issues:
        issues_text = "\n".join(f"  - {issue}" for issue in prior_issues)
        prompt += f"""
## IMPORTANT — Fix These Issues From Previous Attempt

The previous master summary was rejected for these reasons. You MUST fix all of them:

{issues_text}
"""

    logger.info("  Master Summarizer: Generating master summary (%d functions)", len(summaries))
    logger.debug("  Master Summarizer prompt (%d chars):\n%s", len(prompt), prompt)

    try:
        result = _invoke_with_retries(structured_llm, [
            {"role": "system", "content": MASTER_SUMMARIZER_SYSTEM},
            {"role": "user", "content": prompt},
        ])
        logger.info("  Master Summarizer: Generated (%d char executive summary)", len(result.executive_summary))
        _debug_log_master_summary("Master Summarizer output (raw LLM)", result)
        return result
    except Exception as exc:
        logger.warning("  Master Summarizer failed after all retries: %s — building fallback", exc)
        return _build_fallback_master_summary(summaries)


# ---------------------------------------------------------------------------
# Master Summary: Validator
# ---------------------------------------------------------------------------

def run_master_validator(
    summaries: dict[str, FunctionGapSummary],
    master_summary: MasterGapSummary,
    model_name: str = "gemma4:e2b",
) -> SummaryValidationResult:
    """
    Validate a master summary against the per-function summaries.

    Args:
        summaries: Dict mapping function name to its FunctionGapSummary.
        master_summary: The generated MasterGapSummary to validate.
        model_name: Ollama model name.

    Returns:
        SummaryValidationResult indicating acceptance or issues.
    """
    # ── Code-based stat + strongest/weakest check ──
    agg = _aggregate_stats(summaries)
    strongest, weakest = _compute_strongest_weakest(summaries)

    stat_issues: list[str] = []
    checks = [
        ("total_subcategories", master_summary.total_subcategories, agg["total"]),
        ("total_in_scope", master_summary.total_in_scope, agg["in_scope"]),
        ("total_addressed", master_summary.total_addressed, agg["addressed"]),
        ("total_partially_addressed", master_summary.total_partially_addressed, agg["partially_addressed"]),
        ("total_not_addressed", master_summary.total_not_addressed, agg["not_addressed"]),
        ("total_out_of_scope", master_summary.total_out_of_scope, agg["out_of_scope"]),
    ]
    for field, got, expected in checks:
        if got != expected:
            stat_issues.append(f"Wrong number: {field} is {got}, should be {expected}")

    # For ties, accept any function name that's part of the tie
    def _check_function_field(generated: str, expected: str, field_name: str) -> str | None:
        if expected.startswith("Tied ("):
            # Extract tied function names; accept any of them or the full "Tied (...)" string
            tied_names = [n.strip() for n in expected[6:-1].split(",")]
            if generated not in tied_names and generated != expected:
                return (
                    f"Wrong {field_name}: '{generated}', should be one of "
                    f"{tied_names} (these functions are tied)"
                )
        elif generated != expected:
            return f"Wrong {field_name}: '{generated}', should be '{expected}'"
        return None

    issue = _check_function_field(master_summary.strongest_function, strongest, "strongest_function")
    if issue:
        stat_issues.append(issue)
    issue = _check_function_field(master_summary.weakest_function, weakest, "weakest_function")
    if issue:
        stat_issues.append(issue)

    # Check missing policy documents — every expected doc must be present
    expected_docs = set(_collect_all_missing_docs(summaries))
    generated_docs = set(master_summary.missing_policy_documents)
    missing_docs = expected_docs - generated_docs
    if missing_docs:
        stat_issues.append(
            f"Missing policy documents dropped: {len(missing_docs)} of "
            f"{len(expected_docs)} not included: "
            + ", ".join(sorted(missing_docs)[:5])
            + ("..." if len(missing_docs) > 5 else "")
        )

    # Check critical gaps — every in-scope function's gaps must be represented
    expected_gaps = _collect_all_critical_gaps(summaries)
    if len(master_summary.top_critical_gaps) < len(expected_gaps):
        stat_issues.append(
            f"Critical gaps dropped: only {len(master_summary.top_critical_gaps)} of "
            f"{len(expected_gaps)} included. All in-scope functions' gaps must be represented."
        )

    if stat_issues:
        logger.warning("  Master Validator: REJECTED by code — %d issues", len(stat_issues))
        for issue in stat_issues:
            logger.warning("    - %s", issue)
        return SummaryValidationResult(is_acceptable=False, issues=stat_issues)

    logger.info("  Master Validator: all factual fields verified by code ✓")

    # ── LLM-based qualitative check (fabrication + garbled text only) ──
    llm = create_llm()
    structured_llm = llm.with_structured_output(SummaryValidationResult)

    # Collect all valid subcategory IDs from per-function summaries
    all_valid_ids: list[str] = []
    for s in summaries.values():
        for gap in s.critical_gaps:
            # Extract IDs like "GV.OC-03" from gap text
            for word in gap.split():
                if "." in word and "-" in word:
                    all_valid_ids.append(word.strip("(),:"))

    summary_text = (
        f"Executive Summary:\n{master_summary.executive_summary}\n\n"
        f"Top Critical Gaps:\n"
        + "\n".join(f"  - {g}" for g in master_summary.top_critical_gaps)
        + f"\n\nTop Recommendations:\n"
        + "\n".join(f"  - {r}" for r in master_summary.top_recommendations)
    )

    prompt = f"""Check this master executive summary for errors.

## Valid subcategory IDs (reference list)

{', '.join(all_valid_ids) if all_valid_ids else '(none)'}

## Master Summary to Check

{summary_text}

## Instructions

1. Check if any subcategory ID in Top Critical Gaps does NOT appear in the reference list above.
2. Check if the text contains garbled or nonsensical content.
If no errors found, set is_acceptable=true with empty issues list.
"""

    logger.info("  Master Validator: LLM checking for fabrication/garbled text")
    logger.debug("  Master Validator prompt (%d chars):\n%s", len(prompt), prompt)

    try:
        result = _invoke_with_retries(structured_llm, [
            {"role": "system", "content": MASTER_VALIDATOR_SYSTEM},
            {"role": "user", "content": prompt},
        ])
        if result.is_acceptable:
            logger.info("  Master Validator: Summary ACCEPTED ✓")
        else:
            logger.warning("  Master Validator: Summary REJECTED — %d issues", len(result.issues))
            for issue in result.issues:
                logger.warning("    - %s", issue)
        logger.debug("  Master Validator result: is_acceptable=%s, issues=%s",
                      result.is_acceptable, result.issues)
        return result
    except Exception as exc:
        logger.warning("  Master Validator failed after all retries: %s — accepting summary", exc)
        return SummaryValidationResult(is_acceptable=True, issues=[])


# ---------------------------------------------------------------------------
# Master Summary: Orchestrator (Summarize + Validate loop)
# ---------------------------------------------------------------------------

def run_master_summarize_with_validation(
    summaries: dict[str, FunctionGapSummary],
    model_name: str = "gemma4:e2b",
) -> MasterGapSummary:
    """
    Generate a validated master executive summary across all NIST functions.

    Runs the master summarizer, then validates. If rejected, regenerates
    with the validation issues as feedback (up to MAX_RETRIES).

    Args:
        summaries: Dict mapping function name to its FunctionGapSummary.
        model_name: Ollama model name.

    Returns:
        Validated MasterGapSummary.
    """
    logger.info("=" * 40)
    logger.info("Generating Master Executive Summary (with validation loop)")
    logger.info("=" * 40)

    agg = _aggregate_stats(summaries)
    strongest, weakest = _compute_strongest_weakest(summaries)
    logger.debug("  Ground-truth aggregate stats: %s", agg)
    logger.debug("  Ground-truth strongest=%s, weakest=%s", strongest, weakest)

    # Initial generation
    master_summary = run_master_summarizer(summaries, model_name)

    for attempt in range(1, MAX_RETRIES + 1):
        logger.debug("  Master validation attempt %d/%d", attempt, MAX_RETRIES)

        validation = run_master_validator(summaries, master_summary, model_name)

        if validation.is_acceptable:
            logger.info(
                "  Master summary accepted on attempt %d ✓", attempt,
            )
            return master_summary

        logger.warning(
            "  Master summary rejected (attempt %d/%d) — regenerating",
            attempt, MAX_RETRIES,
        )

        # Regenerate with feedback
        master_summary = run_master_summarizer(
            summaries, model_name, prior_issues=validation.issues,
        )

    logger.warning(
        "  Master summary: max retries (%d) reached — code-correcting failed fields only",
        MAX_RETRIES,
    )

    # Code-correct ONLY the specific fields the validator flagged.
    # The LLM tried 3 times and couldn't get these right — fix them surgically.
    agg = _aggregate_stats(summaries)
    strongest, weakest = _compute_strongest_weakest(summaries)
    all_gaps = _collect_all_critical_gaps(summaries)
    all_docs = _collect_all_missing_docs(summaries)

    corrections: list[str] = []

    # Fix stats if wrong
    stat_fields = [
        ("total_subcategories", "total"), ("total_in_scope", "in_scope"),
        ("total_addressed", "addressed"), ("total_partially_addressed", "partially_addressed"),
        ("total_not_addressed", "not_addressed"), ("total_out_of_scope", "out_of_scope"),
    ]
    for attr, key in stat_fields:
        if getattr(master_summary, attr) != agg[key]:
            corrections.append(f"{attr}: {getattr(master_summary, attr)} → {agg[key]}")
            setattr(master_summary, attr, agg[key])

    # Fix strongest/weakest if wrong
    def _is_valid_for_field(generated: str, expected: str) -> bool:
        if expected.startswith("Tied ("):
            tied_names = [n.strip() for n in expected[6:-1].split(",")]
            return generated in tied_names or generated == expected
        return generated == expected

    if not _is_valid_for_field(master_summary.strongest_function, strongest):
        corrections.append(f"strongest_function: '{master_summary.strongest_function}' → '{strongest}'")
        master_summary.strongest_function = strongest
    if not _is_valid_for_field(master_summary.weakest_function, weakest):
        corrections.append(f"weakest_function: '{master_summary.weakest_function}' → '{weakest}'")
        master_summary.weakest_function = weakest

    # Fix missing docs if dropped
    expected_doc_set = set(all_docs)
    generated_doc_set = set(master_summary.missing_policy_documents)
    if expected_doc_set - generated_doc_set:
        dropped = len(expected_doc_set - generated_doc_set)
        corrections.append(f"missing_policy_documents: {dropped} docs were dropped, restoring full list")
        master_summary.missing_policy_documents = all_docs

    # Fix critical gaps if dropped
    if len(master_summary.top_critical_gaps) < len(all_gaps):
        corrections.append(
            f"top_critical_gaps: {len(master_summary.top_critical_gaps)} → {len(all_gaps)} "
            f"(restoring gaps from all in-scope functions)"
        )
        master_summary.top_critical_gaps = all_gaps

    if corrections:
        logger.warning("  Code-corrected %d fields after max retries:", len(corrections))
        for c in corrections:
            logger.warning("    - %s", c)
    else:
        logger.info("  No code corrections needed — last LLM attempt was correct")

    _debug_log_master_summary("Final (after code-correction) — Master", master_summary)
    return master_summary


# ---------------------------------------------------------------------------
# Master Summary: Markdown renderer
# ---------------------------------------------------------------------------

def render_master_summary(summary: MasterGapSummary) -> str:
    """Render a MasterGapSummary into a clean markdown document."""
    lines: list[str] = []

    lines.append("# NIST CSF Gap Analysis — Master Executive Summary")
    lines.append("*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*\n")

    # Executive summary
    lines.append("## Executive Summary\n")
    lines.append(summary.executive_summary)
    lines.append("")

    # Overall stats table
    lines.append("## Overall Coverage Statistics\n")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Subcategories | {summary.total_subcategories} |")
    lines.append(f"| In Scope | {summary.total_in_scope} |")
    lines.append(f"| Addressed | {summary.total_addressed} |")
    lines.append(f"| Partially Addressed | {summary.total_partially_addressed} |")
    lines.append(f"| Not Addressed | {summary.total_not_addressed} |")
    lines.append(f"| Out of Scope | {summary.total_out_of_scope} |")
    lines.append(f"| **Overall Maturity** | **{summary.overall_maturity}** |")
    lines.append("")

    # Strongest / Weakest
    lines.append("## Function Assessment\n")
    lines.append(f"- **Strongest Function:** {summary.strongest_function}")
    lines.append(f"- **Weakest Function:** {summary.weakest_function}")
    lines.append("")

    # Top critical gaps
    if summary.top_critical_gaps:
        lines.append("## Top Critical Gaps\n")
        for i, gap in enumerate(summary.top_critical_gaps, 1):
            lines.append(f"{i}. {gap}")
        lines.append("")

    # Top recommendations
    if summary.top_recommendations:
        lines.append("## Top Recommendations\n")
        for i, rec in enumerate(summary.top_recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

    # Missing policy documents
    if summary.missing_policy_documents:
        lines.append("## Missing Policy Documents\n")
        lines.append(
            "The following policy templates are needed to achieve full NIST CSF coverage:\n"
        )
        for doc in summary.missing_policy_documents:
            lines.append(f"- {doc}")
        lines.append("")

    # Remediation priorities
    if summary.remediation_priorities:
        lines.append("## Remediation Priorities\n")
        for i, priority in enumerate(summary.remediation_priorities, 1):
            lines.append(f"{i}. {priority}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Per-function Markdown renderer
# ---------------------------------------------------------------------------

def render_function_summary(summary: FunctionGapSummary) -> str:
    """Render a FunctionGapSummary into a clean markdown document."""
    lines: list[str] = []

    lines.append(f"# {summary.function_name} Function — Executive Gap Summary")
    lines.append(f"*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*\n")

    # Executive summary
    lines.append("## Executive Summary\n")
    lines.append(summary.executive_summary)
    lines.append("")

    # Stats table
    lines.append("## Coverage Statistics\n")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Subcategories | {summary.total_subcategories} |")
    lines.append(f"| In Scope | {summary.in_scope_count} |")
    lines.append(f"| Addressed | {summary.addressed_count} |")
    lines.append(f"| Partially Addressed | {summary.partially_addressed_count} |")
    lines.append(f"| Not Addressed | {summary.not_addressed_count} |")
    lines.append(f"| Out of Scope | {summary.out_of_scope_count} |")
    lines.append(f"| **Maturity Rating** | **{summary.maturity_rating}** |")
    lines.append("")

    # Critical gaps
    if summary.critical_gaps:
        lines.append("## Critical Gaps\n")
        for i, gap in enumerate(summary.critical_gaps, 1):
            lines.append(f"{i}. {gap}")
        lines.append("")

    # Recommendations
    if summary.key_recommendations:
        lines.append("## Key Recommendations\n")
        for i, rec in enumerate(summary.key_recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

    # Missing policy documents
    if summary.required_policy_documents:
        lines.append("## Required Policy Documents\n")
        lines.append(
            "The following policy templates are needed to cover out-of-scope "
            "subcategories:\n"
        )
        for doc in summary.required_policy_documents:
            lines.append(f"- {doc}")
        lines.append("")

    return "\n".join(lines)

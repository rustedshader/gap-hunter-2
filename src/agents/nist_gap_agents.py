"""
NIST CSF Gap Analysis Agents — scope-first, per-subcategory structured output.

Flow per function:
  1. Scope Classifier — one LLM call to classify all subcategories as
     "in-scope" or "out-of-scope" relative to the customer's policy topic.
  2. Per-subcategory assessment — only for in-scope subcategories.
  3. Out-of-scope subcategories tagged automatically (no LLM call).

This dramatically reduces LLM calls (typically ~20-30 instead of 106) while
producing correct "Out of Scope" annotations that feed the roadmap.
"""

from __future__ import annotations

import logging
from typing import Literal

from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from agents.gap_analysis_tools import (
    get_function_subcategories,
    get_framework_excerpt,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ScopeClassification(BaseModel):
    """Result of classifying which subcategories are within the policy's scope."""

    in_scope_ids: list[str] = Field(
        description=(
            "List of NIST subcategory IDs (e.g. ['GV.OC-01', 'GV.RM-02']) that "
            "the customer's policy document is intended to cover, even if it "
            "covers them poorly. Only include IDs whose TOPIC is relevant to "
            "this policy's subject matter."
        ),
    )


class SubcategoryAssessment(BaseModel):
    """Assessment of a single NIST CSF subcategory against a customer policy."""

    subcategory_id: str = Field(
        description="NIST subcategory ID, e.g. GV.OC-01",
    )
    title: str = Field(
        description="Short human-readable title of the requirement",
    )
    status: Literal[
        "Addressed", "Partially Addressed", "Not Addressed", "Out of Scope"
    ] = Field(
        description="Whether the customer policy addresses this requirement",
    )
    evidence: str = Field(
        description=(
            "Direct quote from the customer policy that demonstrates coverage, "
            "or 'None found' if the policy does not address this requirement"
        ),
    )
    gap: str = Field(
        description=(
            "Specific requirement or language that is missing or incomplete, "
            "or 'None - fully addressed' if the policy fully covers this"
        ),
    )
    recommendation: str = Field(
        description=(
            "Specific, actionable step the organization should take to close "
            "this gap, referencing the CIS MS-ISAC template guidance"
        ),
    )


# ---------------------------------------------------------------------------
# Scope classifier
# ---------------------------------------------------------------------------

def _build_scope_prompt(policy_content: str, subcategories: list[dict]) -> str:
    """Build prompt for the scope classification agent."""

    sub_list = "\n".join(
        f"- **{s['id']}**: {s['description'][:150]}"
        for s in subcategories
    )

    return f"""You are a cybersecurity policy analyst. Your task is to determine which
NIST CSF subcategories are WITHIN THE SCOPE of the customer's policy document below.

A subcategory is "in scope" if the policy's SUBJECT MATTER is intended to cover
that topic — even if the policy covers it poorly or incompletely. A subcategory is
"out of scope" if it belongs to a completely different policy domain.

For example:
- A "Risk Management Policy" → in scope: risk assessment, risk appetite, risk treatment
- A "Risk Management Policy" → out of scope: access control, incident response, encryption

## Customer Policy Document

{policy_content}

## Subcategories to Classify

{sub_list}

## Instructions
Return ONLY the IDs of subcategories that are within scope of this policy's subject
matter. Do NOT include subcategories that require a completely different policy document.
"""


def _classify_scope(
    policy_content: str,
    subcategories: list[dict],
    llm: ChatOllama,
) -> set[str]:
    """
    Classify which subcategories are in-scope for the given policy.

    Args:
        policy_content: Customer policy text.
        subcategories: List of subcategory dicts for one NIST function.
        llm: ChatOllama instance.

    Returns:
        Set of subcategory IDs that are in-scope.
    """
    structured_llm = llm.with_structured_output(ScopeClassification)
    prompt = _build_scope_prompt(policy_content, subcategories)

    try:
        result = structured_llm.invoke(prompt)
        in_scope = set(result.in_scope_ids)
        logger.info(
            "    Scope classification: %d/%d in-scope",
            len(in_scope),
            len(subcategories),
        )
        return in_scope
    except Exception as exc:
        # On failure, treat ALL as in-scope (safe fallback — just slower)
        logger.warning("    Scope classification failed (%s), treating all as in-scope", exc)
        return {s["id"] for s in subcategories}


# ---------------------------------------------------------------------------
# Per-subcategory assessment prompt
# ---------------------------------------------------------------------------

def _build_subcategory_prompt(
    policy_content: str,
    sub: dict,
    framework_excerpt: str,
) -> str:
    """Build a small, focused prompt for assessing ONE subcategory."""

    questions_block = "\n".join(f"  - {q}" for q in sub.get("questions", []))
    policies_str = ", ".join(sub.get("policies", [])) or "N/A"

    return f"""You are a cybersecurity compliance analyst assessing a customer's security
policy against a specific NIST CSF subcategory from the CIS MS-ISAC NIST
Cybersecurity Framework Policy Template Guide (2024).

## Customer Policy Document

{policy_content}

## NIST Subcategory to Assess: {sub["id"]}
**Category**: {sub["category"]}
**Requirement**: {sub["description"]}
**Implementation Guidance**: {sub["guidance"]}
**Key Questions**:
{questions_block}
**Required Policy Templates**: {policies_str}

## Reference: What a Compliant Policy Should Include
(From CIS MS-ISAC policy templates: {policies_str})

{framework_excerpt}

## Your Task
Compare the customer policy against this ONE subcategory requirement and the
reference template above.
- If the customer policy addresses this requirement, quote the exact relevant
  text from the customer policy as evidence.
- If partially addressed, explain what is present and what is still missing.
- If not addressed at all, state clearly what is missing and recommend specific
  language or sections to add based on the reference template.
"""


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def _compute_maturity(assessments: list[SubcategoryAssessment]) -> str:
    """Derive overall maturity from in-scope subcategory statuses only."""
    in_scope = [a for a in assessments if a.status != "Out of Scope"]
    total = len(in_scope)
    if total == 0:
        return "Not Started"

    score = sum(
        1.0 if a.status == "Addressed"
        else 0.5 if a.status == "Partially Addressed"
        else 0.0
        for a in in_scope
    )
    pct = score / total

    if pct >= 0.9:
        return "Fully Implemented"
    if pct >= 0.6:
        return "Substantially Implemented"
    if pct >= 0.2:
        return "Partially Implemented"
    return "Not Started"


def _assemble_function_report(
    function_name: str,
    assessments: list[SubcategoryAssessment],
) -> str:
    """Render subcategory assessments into the final markdown report."""

    in_scope = [a for a in assessments if a.status != "Out of Scope"]
    out_scope = [a for a in assessments if a.status == "Out of Scope"]

    addressed = sum(1 for a in in_scope if a.status == "Addressed")
    partial = sum(1 for a in in_scope if a.status == "Partially Addressed")
    not_addressed = sum(1 for a in in_scope if a.status == "Not Addressed")
    maturity = _compute_maturity(assessments)

    lines: list[str] = []
    lines.append(f"# {function_name} Function — Gap Analysis Report")
    lines.append(f"*(CIS MS-ISAC NIST CSF Policy Template Guide 2024)*\n")
    lines.append(f"**Total Subcategories**: {len(assessments)}")
    lines.append(f"**In Scope**: {len(in_scope)} | **Out of Scope**: {len(out_scope)}")
    lines.append(
        f"**Addressed**: {addressed} | **Partially Addressed**: {partial} "
        f"| **Not Addressed**: {not_addressed}"
    )
    lines.append(f"**Overall Maturity** (in-scope only): {maturity}\n")

    # --- In-scope assessments ---
    if in_scope:
        lines.append("---\n")
        lines.append("## In-Scope Subcategory Assessments\n")
        for a in in_scope:
            lines.append(f"### {a.subcategory_id} — {a.title}")
            lines.append(f"**Status**: {a.status}")
            lines.append(f"**Evidence from Policy**: {a.evidence}")
            lines.append(f"**Gap**: {a.gap}")
            lines.append(f"**Recommendation**: {a.recommendation}")
            lines.append("")

    # --- Out-of-scope summary ---
    if out_scope:
        lines.append("---\n")
        lines.append("## Out-of-Scope Subcategories\n")
        lines.append(
            "These subcategories require separate policy documents that are not "
            "covered by the input policy:\n"
        )
        lines.append("| Subcategory | Required Policy Template(s) |")
        lines.append("|-------------|---------------------------|")
        for a in out_scope:
            lines.append(f"| {a.subcategory_id} | {a.recommendation} |")
        lines.append("")

    # --- Maturity summary ---
    lines.append("---\n")
    lines.append(f"## {function_name} Function — Overall Maturity Assessment")
    lines.append(f"**Rating**: {maturity}")
    lines.append(
        f"**Justification**: Of {len(in_scope)} in-scope subcategories, "
        f"{addressed} fully addressed, {partial} partially addressed, "
        f"{not_addressed} not addressed. "
        f"{len(out_scope)} subcategories are out of scope for this policy."
    )

    # Top priority gaps (in-scope only)
    priority_gaps = [a for a in in_scope if a.status == "Not Addressed"]
    if len(priority_gaps) < 3:
        priority_gaps += [a for a in in_scope if a.status == "Partially Addressed"]
    priority_gaps = priority_gaps[:3]

    if priority_gaps:
        lines.append("**Top Priority Gaps**:")
        for i, g in enumerate(priority_gaps, 1):
            lines.append(f"{i}. **{g.subcategory_id}** — {g.gap[:120]}")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main agent runner
# ---------------------------------------------------------------------------

def run_nist_gap_agent(
    function_name: Literal["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"],
    policy_content: str,
    model_name: str = "gemma4:e2b",
) -> tuple[str, list[SubcategoryAssessment]]:
    """
    Assess a NIST function's subcategories against the customer policy.

    1. Scope classifier (1 LLM call) — determines which subcategories are
       relevant to this policy's subject matter.
    2. Per-subcategory assessment (N LLM calls) — only for in-scope items.
    3. Out-of-scope items tagged automatically without LLM calls.

    Args:
        function_name: NIST function to analyze.
        policy_content: Full policy document text.
        model_name: Ollama model name.

    Returns:
        Tuple of (assembled markdown report, list of raw SubcategoryAssessment objects).
    """
    logger.info("Running NIST %s gap analysis agent", function_name)

    subcategories = get_function_subcategories(function_name)
    if not subcategories:
        msg = f"# {function_name} Gap Analysis\n\n*No subcategories found in config.*"
        logger.error(msg)
        return msg, []

    logger.info("  %d total subcategories for %s", len(subcategories), function_name)

    llm = ChatOllama(model=model_name, temperature=0)

    # Step 1: Scope classification
    logger.info("  Step 1: Classifying scope...")
    in_scope_ids = _classify_scope(policy_content, subcategories, llm)

    in_scope_subs = [s for s in subcategories if s["id"] in in_scope_ids]
    out_scope_subs = [s for s in subcategories if s["id"] not in in_scope_ids]

    logger.info(
        "  %d in-scope, %d out-of-scope → %d LLM calls saved",
        len(in_scope_subs),
        len(out_scope_subs),
        len(out_scope_subs),
    )

    # Step 2: Assess in-scope subcategories
    structured_llm = llm.with_structured_output(SubcategoryAssessment)
    assessments: list[SubcategoryAssessment] = []

    for i, sub in enumerate(in_scope_subs, 1):
        sub_id = sub["id"]
        logger.info("  [%d/%d] Assessing %s", i, len(in_scope_subs), sub_id)

        framework_excerpt = get_framework_excerpt(sub.get("policies", []))
        prompt = _build_subcategory_prompt(policy_content, sub, framework_excerpt)

        try:
            result = structured_llm.invoke(prompt)
            assessments.append(result)
            logger.info("    %s → %s", sub_id, result.status)
        except Exception as exc:
            logger.warning("    %s assessment failed: %s", sub_id, exc)
            assessments.append(
                SubcategoryAssessment(
                    subcategory_id=sub_id,
                    title=sub.get("category", sub_id),
                    status="Not Addressed",
                    evidence="None found",
                    gap="Assessment could not be completed — manual review required",
                    recommendation="Manual review required for this subcategory",
                )
            )

    # Step 3: Tag out-of-scope subcategories (no LLM call)
    for sub in out_scope_subs:
        policy_templates = ", ".join(sub.get("policies", [])) or "N/A"
        assessments.append(
            SubcategoryAssessment(
                subcategory_id=sub["id"],
                title=sub.get("category", sub["id"]),
                status="Out of Scope",
                evidence="N/A — subcategory is outside this policy's scope",
                gap=f"Requires dedicated policy: {policy_templates}",
                recommendation=policy_templates,
            )
        )

    # Sort: in-scope first (by ID), then out-of-scope
    assessments.sort(key=lambda a: (a.status == "Out of Scope", a.subcategory_id))

    report = _assemble_function_report(function_name, assessments)
    logger.info("  %s report assembled (%d chars)", function_name, len(report))
    return report, assessments


# ---------------------------------------------------------------------------
# Code-based consolidator (no LLM — pure aggregation)
# ---------------------------------------------------------------------------

NIST_FUNCTION_ORDER = ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]


def build_consolidated_report(
    all_assessments: dict[str, list[SubcategoryAssessment]],
) -> str:
    """
    Build the consolidated gap analysis report from structured assessment data.

    This is entirely code-based — no LLM call needed.  Aggregates counts,
    builds tables, identifies missing policy templates, and produces a
    prioritized roadmap.

    Args:
        all_assessments: Mapping of function name → list of SubcategoryAssessment.

    Returns:
        Consolidated markdown report.
    """
    logger.info("Building consolidated report (code-based)")

    # --- Aggregate per-function stats ---
    func_stats: dict[str, dict] = {}
    all_in_scope: list[tuple[str, SubcategoryAssessment]] = []  # (function, assessment)
    all_out_scope: list[tuple[str, SubcategoryAssessment]] = []

    for fn in NIST_FUNCTION_ORDER:
        assessments = all_assessments.get(fn, [])
        in_s = [a for a in assessments if a.status != "Out of Scope"]
        out_s = [a for a in assessments if a.status == "Out of Scope"]
        addr = sum(1 for a in in_s if a.status == "Addressed")
        part = sum(1 for a in in_s if a.status == "Partially Addressed")
        na = sum(1 for a in in_s if a.status == "Not Addressed")

        func_stats[fn] = {
            "total": len(assessments),
            "in_scope": len(in_s),
            "out_scope": len(out_s),
            "addressed": addr,
            "partial": part,
            "not_addressed": na,
            "maturity": _compute_maturity(assessments),
        }
        for a in in_s:
            all_in_scope.append((fn, a))
        for a in out_s:
            all_out_scope.append((fn, a))

    # Totals
    total_sub = sum(s["total"] for s in func_stats.values())
    total_in = sum(s["in_scope"] for s in func_stats.values())
    total_out = sum(s["out_scope"] for s in func_stats.values())
    total_addr = sum(s["addressed"] for s in func_stats.values())
    total_part = sum(s["partial"] for s in func_stats.values())
    total_na = sum(s["not_addressed"] for s in func_stats.values())

    # Overall maturity from all in-scope assessments
    flat_in_scope = [a for _, a in all_in_scope]
    overall_maturity = _compute_maturity(flat_in_scope) if flat_in_scope else "Not Started"

    lines: list[str] = []

    # ---- Section 1: Executive Summary ----
    lines.append("# NIST CSF Gap Analysis — Consolidated Report")
    lines.append("*(CIS MS-ISAC Policy Template Guide 2024 Alignment)*\n")
    lines.append("## 1. Executive Summary")
    lines.append(f"- **Overall Maturity** (in-scope only): {overall_maturity}")
    lines.append(f"- **Total Subcategories**: {total_sub} (In Scope: {total_in}, Out of Scope: {total_out})")
    lines.append(f"- **In-Scope Results**: Addressed: {total_addr} | Partially Addressed: {total_part} | Not Addressed: {total_na}")

    if total_na > 0:
        worst_fn = max(func_stats, key=lambda f: func_stats[f]["not_addressed"])
        lines.append(
            f"- **Critical Finding**: {total_na} in-scope subcategories are not addressed. "
            f"The {worst_fn} function has the most gaps ({func_stats[worst_fn]['not_addressed']} not addressed)."
        )
    else:
        lines.append("- **Critical Finding**: All in-scope subcategories have at least partial coverage.")
    lines.append("")

    # ---- Section 2: Maturity by Function ----
    lines.append("## 2. Maturity by Function")
    lines.append("| Function | Rating | In Scope | Addressed | Partial | Not Addressed | Out of Scope |")
    lines.append("|----------|--------|----------|-----------|---------|---------------|--------------|")
    for fn in NIST_FUNCTION_ORDER:
        s = func_stats[fn]
        lines.append(
            f"| {fn} | {s['maturity']} | {s['in_scope']} | "
            f"{s['addressed']} | {s['partial']} | {s['not_addressed']} | {s['out_scope']} |"
        )
    lines.append("")

    # ---- Section 3: In-Scope Gaps (Not Addressed) ----
    not_addressed_gaps = [(fn, a) for fn, a in all_in_scope if a.status == "Not Addressed"]
    lines.append("## 3. In-Scope Gaps (Not Addressed)")
    lines.append("These are gaps the current policy SHOULD cover but does not:\n")
    if not_addressed_gaps:
        lines.append("| Subcategory ID | Function | Gap | Recommended Action |")
        lines.append("|----------------|----------|-----|--------------------|")
        for fn, a in not_addressed_gaps:
            gap_short = a.gap[:100].replace("|", "/").replace("\n", " ")
            rec_short = a.recommendation[:100].replace("|", "/").replace("\n", " ")
            lines.append(f"| {a.subcategory_id} | {fn} | {gap_short} | {rec_short} |")
    else:
        lines.append("*No in-scope subcategories are fully unaddressed.*")
    lines.append("")

    # ---- Section 4: In-Scope Gaps (Partially Addressed) ----
    partial_gaps = [(fn, a) for fn, a in all_in_scope if a.status == "Partially Addressed"]
    lines.append("## 4. In-Scope Gaps (Partially Addressed)")
    if partial_gaps:
        lines.append("| Subcategory ID | Function | Gap | Recommended Action |")
        lines.append("|----------------|----------|-----|--------------------|")
        for fn, a in partial_gaps:
            gap_short = a.gap[:100].replace("|", "/").replace("\n", " ")
            rec_short = a.recommendation[:100].replace("|", "/").replace("\n", " ")
            lines.append(f"| {a.subcategory_id} | {fn} | {gap_short} | {rec_short} |")
    else:
        lines.append("*No partially addressed subcategories.*")
    lines.append("")

    # ---- Section 5: Missing Policy Documents ----
    # Group out-of-scope subcategories by their required policy template
    template_map: dict[str, list[str]] = {}
    for _, a in all_out_scope:
        # recommendation field holds the policy template names
        for tmpl in a.recommendation.split(", "):
            tmpl = tmpl.strip()
            if tmpl and tmpl != "N/A":
                template_map.setdefault(tmpl, []).append(a.subcategory_id)

    lines.append("## 5. Missing Policy Documents")
    lines.append("Out-of-scope subcategories grouped by the policy template needed:\n")
    if template_map:
        lines.append("| Missing Policy Template | Count | NIST Subcategories Covered |")
        lines.append("|-------------------------|-------|---------------------------|")
        for tmpl in sorted(template_map, key=lambda t: -len(template_map[t])):
            ids = template_map[tmpl]
            ids_str = ", ".join(sorted(set(ids)))
            lines.append(f"| {tmpl} | {len(set(ids))} | {ids_str} |")
    else:
        lines.append("*All required policy templates are covered by the input policy.*")
    lines.append("")

    # ---- Section 6: Prioritized Remediation Roadmap ----
    lines.append("## 6. Prioritized Remediation Roadmap\n")

    # Immediate: in-scope not-addressed
    immediate_ids = [a.subcategory_id for _, a in not_addressed_gaps[:10]]
    # Short-term: in-scope partially addressed
    short_ids = [a.subcategory_id for _, a in partial_gaps[:10]]
    # Medium-term: create missing policies
    medium_templates = sorted(template_map.keys())[:5]

    lines.append("| Priority | Action | Details |")
    lines.append("|----------|--------|---------|")
    if immediate_ids:
        lines.append(
            f"| **1 — Immediate (0–30 days)** | Address critical in-scope gaps | "
            f"{', '.join(immediate_ids)} |"
        )
    if short_ids:
        lines.append(
            f"| **2 — Short-term (30–90 days)** | Strengthen partially addressed areas | "
            f"{', '.join(short_ids)} |"
        )
    if medium_templates:
        lines.append(
            f"| **3 — Medium-term (90–180 days)** | Create missing policy documents | "
            f"{', '.join(medium_templates)} |"
        )
    lines.append("")

    logger.info("  Consolidated report built (%d lines)", len(lines))
    return "\n".join(lines)

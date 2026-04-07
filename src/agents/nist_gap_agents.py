"""
NIST CSF Gap Analysis Agents — Map-Reduce + scope-first architecture.

Flow per function:
  1. Scope Classifier — one LLM call to classify all subcategories as
     "in-scope" or "out-of-scope" relative to the customer's policy topic.
  2. Map phase — for each in-scope subcategory, scan each policy section
     with a small focused call (~1K chars) asking "does this section contain
     evidence for this subcategory?" Returns a short snippet or "not present".
     Sections are scanned sequentially (ChatLlamaCpp is not thread-safe).
  3. Reduce phase — for each in-scope subcategory, collect all evidence
     snippets from the Map phase and make ONE assessment call with only
     the relevant evidence (not the full policy document).
  4. Out-of-scope subcategories tagged automatically (no LLM call).

This cuts per-assessment prompt size from ~10K to ~1K chars and removes
the need to send the full policy document to every assessment call.
"""

from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field

from llm import create_llm

from agents.gap_analysis_tools import (
    get_function_subcategories,
    get_framework_excerpt,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class PolicyScopeClassification(BaseModel):
    """Determines which NIST CSF functions are relevant to a policy document."""

    relevant_functions: list[
        Literal["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]
    ] = Field(
        description=(
            "List of NIST CSF functions whose subject matter is relevant to "
            "this policy document. For example, a Risk Management Policy is "
            "relevant to Govern and Identify, but NOT to Protect, Detect, "
            "Respond, or Recover."
        ),
    )


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
# Policy-level function classifier (runs ONCE before everything)
# ---------------------------------------------------------------------------


def classify_policy_functions(
    policy_content: str,
    model_name: str = "gemma4:e2b",
) -> list[str]:
    """
    Determine which NIST CSF functions are relevant to this policy document.

    Runs ONE LLM call. Irrelevant functions are skipped entirely — all their
    subcategories are marked "Out of Scope" without any further LLM calls.

    Args:
        policy_content: Full customer policy text.
        model_name: Model name (kept for interface compat).

    Returns:
        List of relevant function names (e.g. ["Govern", "Identify"]).
    """
    logger.info("Classifying policy scope across NIST CSF functions...")

    llm = create_llm()
    structured_llm = llm.with_structured_output(PolicyScopeClassification)

    prompt = f"""You are a cybersecurity policy analyst. Given the customer's policy
document below, determine which NIST CSF functions are relevant to this policy's
subject matter.

The 6 NIST CSF functions are:
- **Govern**: Risk management strategy, governance, roles, policy, oversight, supply chain risk
- **Identify**: Asset management, risk assessment, improvement processes
- **Protect**: Access control, awareness training, data security, platform security, resilience
- **Detect**: Continuous monitoring, adverse event analysis, detection processes
- **Respond**: Incident management, analysis, mitigation, communication
- **Recover**: Recovery planning, improvements, recovery communication

A function is "relevant" if the policy's TOPIC overlaps with that function's domain
— even if coverage is weak. A function is NOT relevant if it belongs to a completely
different policy domain.

Examples:
- "Risk Management Policy" → Govern, Identify
- "Access Control Policy" → Protect, Govern
- "Incident Response Policy" → Respond, Recover, Detect
- "Information Security Policy" (broad) → Govern, Identify, Protect
- "Data Privacy and Security Policy" → Protect, Govern

## Customer Policy Document

{policy_content}

## Instructions
Return ONLY the function names that are relevant to this policy's subject matter.
"""

    try:
        result = structured_llm.invoke(prompt)
        relevant = result.relevant_functions
        logger.info(
            "  Policy scope: %d/6 functions relevant — %s",
            len(relevant),
            ", ".join(relevant),
        )
        return relevant
    except Exception as exc:
        logger.warning(
            "  Policy scope classification failed (%s), treating all as relevant", exc
        )
        return ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]


# ---------------------------------------------------------------------------
# Per-function subcategory scope classifier
# ---------------------------------------------------------------------------


def _build_scope_prompt(policy_content: str, subcategories: list[dict]) -> str:
    """Build prompt for the scope classification agent."""
    from agents.text_summarizer import summarize_lossless

    # Subcategory descriptions — use full text (they are short NIST config fields,
    # averaging 80-120 chars). No truncation needed.
    sub_list = "\n".join(f"- **{s['id']}**: {s['description']}" for s in subcategories)

    # Compress the policy content — the scope classifier only needs to understand
    # the policy's subject domain, not every specific requirement.
    policy_input = summarize_lossless(
        policy_content,
        context_hint="customer policy document being classified for NIST CSF scope",
        threshold=600,
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

{policy_input}

## Subcategories to Classify

{sub_list}

## Instructions
Return ONLY the IDs of subcategories that are within scope of this policy's subject
matter. Do NOT include subcategories that require a completely different policy document.
"""


def _classify_scope(
    policy_content: str,
    subcategories: list[dict],
    llm,
) -> set[str]:
    """
    Classify which subcategories are in-scope for the given policy.

    Args:
        policy_content: Customer policy text.
        subcategories: List of subcategory dicts for one NIST function.
        llm: LLM instance.

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
        logger.warning(
            "    Scope classification failed (%s), treating all as in-scope", exc
        )
        return {s["id"] for s in subcategories}


# ---------------------------------------------------------------------------
# Map-Reduce: Map phase schemas and helpers
# ---------------------------------------------------------------------------

# Sections shorter than this are skipped in the Map phase (headers / TOC).
_MIN_SECTION_CHARS = 80


class SectionEvidenceResult(BaseModel):
    """Map phase output — evidence found in ONE section for ONE subcategory."""

    has_evidence: bool = Field(
        description=(
            "True if this section contains text that is relevant to the "
            "subcategory requirement (even if only partially). False otherwise."
        ),
    )
    evidence_snippet: str = Field(
        description=(
            "A direct quote (max 200 chars) from the section that relates to "
            "the subcategory, or 'None found' if has_evidence is False."
        ),
    )


def _map_one_section(
    section_number: str,
    section_title: str,
    section_content: str,
    sub_id: str,
    sub_description: str,
) -> tuple[str, SectionEvidenceResult]:
    """
    Map step: check ONE section for evidence of ONE subcategory requirement.

    Args:
        section_number: Section identifier (e.g. '4').
        section_title: Section title for logging.
        section_content: Section text (already truncated by gap_analyzer).
        sub_id: NIST subcategory ID (e.g. 'PR.AA-03').
        sub_description: Short description of the subcategory requirement.

    Returns:
        Tuple of (section_number, SectionEvidenceResult).
    """
    llm = create_llm()
    structured_llm = llm.with_structured_output(SectionEvidenceResult)

    # Import here to avoid circular import at module level
    from agents.text_summarizer import summarize_lossless

    # Compress the section content before injecting — sections can be long
    # and the Map call only needs to know "is evidence for this subcategory present?"
    section_input = summarize_lossless(
        section_content,
        context_hint=f"policy section {section_number} '{section_title}' being scanned for {sub_id} evidence",
        threshold=600,
    )

    prompt = (
        f"Policy section {section_number} — {section_title}:\n\n"
        f"{section_input}\n\n"
        f"---\n\n"
        f"NIST subcategory {sub_id} requires:\n{sub_description}\n\n"
        f"Does this section contain any text relevant to this requirement? "
        f"If yes, quote the most relevant passage (max 200 chars). "
        f"If no, set has_evidence=false."
    )

    try:
        result = structured_llm.invoke(prompt)
        return section_number, result
    except Exception as exc:
        logger.warning(
            "    Map failed for section %s × %s: %s",
            section_number,
            sub_id,
            exc,
        )
        return section_number, SectionEvidenceResult(
            has_evidence=False,
            evidence_snippet="None found",
        )


def _map_sections_for_subcategory(
    policy_sections: list[dict],
    sub_id: str,
    sub_description: str,
) -> list[str]:
    """
    Run the Map phase for one subcategory across all policy sections sequentially.

    ChatLlamaCpp holds a single model instance and is not safe for concurrent
    inference from multiple threads. Sections are scanned one at a time.
    This is still faster than the old approach because each call is ~1K chars
    instead of ~10K (the full policy document).

    Args:
        policy_sections: List of section dicts with 'number', 'title', 'content'.
        sub_id: NIST subcategory ID.
        sub_description: Short subcategory requirement text.

    Returns:
        List of evidence snippets (non-empty strings from sections that matched).
    """
    meaningful_sections = [
        s
        for s in policy_sections
        if len((s.get("content") or "").strip()) >= _MIN_SECTION_CHARS
    ]

    if not meaningful_sections:
        return []

    evidence_snippets: list[str] = []

    for s in meaningful_sections:
        _, result = _map_one_section(
            s["number"],
            s.get("title", ""),
            s.get("content", ""),
            sub_id,
            sub_description,
        )
        if result.has_evidence and result.evidence_snippet.strip() not in (
            "",
            "None found",
        ):
            evidence_snippets.append(result.evidence_snippet)

    return evidence_snippets


# ---------------------------------------------------------------------------
# Map-Reduce: Reduce phase
# ---------------------------------------------------------------------------


def _reduce_to_assessment(
    sub: dict,
    evidence_snippets: list[str],
    framework_excerpt: str,
    structured_llm,
) -> SubcategoryAssessment:
    """
    Reduce step: assess ONE subcategory using only the collected evidence snippets.

    Replaces the old _build_subcategory_prompt which sent the full policy doc.
    The model now receives only the relevant snippets (~1K chars total) instead
    of the full document (~10K chars).

    Args:
        sub: Subcategory dict from NIST config.
        evidence_snippets: Relevant passages collected by the Map phase.
        framework_excerpt: Short reference framework excerpt (max 600 chars).
        structured_llm: Structured-output LLM instance.

    Returns:
        SubcategoryAssessment.
    """
    sub_id = sub["id"]
    questions_block = "\n".join(f"  - {q}" for q in sub.get("questions", []))
    policies_str = ", ".join(sub.get("policies", [])) or "N/A"

    if evidence_snippets:
        evidence_block = "\n\n".join(
            f"Snippet {i + 1}: {snip}" for i, snip in enumerate(evidence_snippets)
        )
        evidence_section = (
            f"## Relevant Evidence Found in Policy\n\n"
            f"The following passages were found across the policy sections:\n\n"
            f"{evidence_block}"
        )
    else:
        evidence_section = (
            "## Relevant Evidence Found in Policy\n\n"
            "No relevant passages were found in any policy section."
        )

    prompt = (
        f"You are a cybersecurity compliance analyst assessing a customer's security "
        f"policy against a specific NIST CSF subcategory.\n\n"
        f"{evidence_section}\n\n"
        f"## NIST Subcategory to Assess: {sub_id}\n"
        f"**Category**: {sub['category']}\n"
        f"**Requirement**: {sub['description']}\n"
        f"**Implementation Guidance**: {sub['guidance']}\n"
        f"**Key Questions**:\n{questions_block}\n"
        f"**Required Policy Templates**: {policies_str}\n\n"
        f"## Reference: What a Compliant Policy Should Include\n\n"
        f"{framework_excerpt}\n\n"
        f"## Your Task\n"
        f"Based on the evidence snippets above, assess whether the customer policy "
        f"addresses this subcategory requirement. "
        f"Quote only from the evidence snippets provided — do not invent policy text."
    )

    return structured_llm.invoke(prompt)


# ---------------------------------------------------------------------------
# Per-subcategory assessment prompt (kept for fallback only)
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
        return "N/A — No subcategories in scope for this policy type"

    score = sum(
        1.0
        if a.status == "Addressed"
        else 0.5
        if a.status == "Partially Addressed"
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
    function_name: Literal[
        "Govern", "Identify", "Protect", "Detect", "Respond", "Recover"
    ],
    policy_content: str,
    model_name: str = "gemma4:e2b",
    policy_sections: list[dict] | None = None,
) -> tuple[str, list[SubcategoryAssessment]]:
    """
    Assess a NIST function's subcategories against the customer policy.

    Map-Reduce architecture:
      1. Scope classifier (1 LLM call) — which subcategories are in-scope?
      2. Map phase — for each in-scope subcategory, scan sections in parallel
         to collect only the relevant evidence snippets.
      3. Reduce phase — for each subcategory, assess using only its evidence
         snippets (not the full policy document).
      4. Out-of-scope items tagged automatically (no LLM call).

    Args:
        function_name: NIST function to analyze.
        policy_content: Full policy document text (used for scope classification
                        and as fallback if policy_sections is None).
        model_name: Model name (kept for interface compatibility).
        policy_sections: Optional list of section dicts for the Map phase.
                         If None, Map phase sends the full policy_content as a
                         single section (same as the old behaviour).

    Returns:
        Tuple of (assembled markdown report, list of SubcategoryAssessment objects).
    """
    logger.info("Running NIST %s gap analysis agent (Map-Reduce)", function_name)

    subcategories = get_function_subcategories(function_name)
    if not subcategories:
        msg = f"# {function_name} Gap Analysis\n\n*No subcategories found in config.*"
        logger.error(msg)
        return msg, []

    logger.info("  %d total subcategories for %s", len(subcategories), function_name)

    llm = create_llm()

    # Step 1: Scope classification (unchanged)
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

    # Prepare sections for Map phase.
    # If the caller passed structured sections, use them.
    # Otherwise wrap the full content as one pseudo-section.
    if policy_sections:
        map_sections = policy_sections
    else:
        map_sections = [
            {"number": "1", "title": "Policy Document", "content": policy_content}
        ]

    # Step 2 + 3: Map-Reduce per in-scope subcategory
    structured_llm = llm.with_structured_output(SubcategoryAssessment)
    assessments: list[SubcategoryAssessment] = []

    for i, sub in enumerate(in_scope_subs, 1):
        sub_id = sub["id"]
        logger.info("  [%d/%d] Map-Reduce: %s", i, len(in_scope_subs), sub_id)

        # Map: collect evidence snippets across all sections (parallel)
        evidence_snippets = _map_sections_for_subcategory(
            map_sections,
            sub_id,
            sub["description"],
        )
        logger.info(
            "    Map: %d evidence snippets found for %s",
            len(evidence_snippets),
            sub_id,
        )

        # Reduce: assess using collected evidence only
        framework_excerpt = get_framework_excerpt(sub.get("policies", []))
        try:
            result = _reduce_to_assessment(
                sub, evidence_snippets, framework_excerpt, structured_llm
            )
            assessments.append(result)
            logger.info("    Reduce: %s → %s", sub_id, result.status)
        except Exception as exc:
            logger.warning(
                "    %s reduce assessment failed: %s — using fallback", sub_id, exc
            )
            # Fallback: attempt the old full-doc assessment
            try:
                prompt = _build_subcategory_prompt(
                    policy_content, sub, framework_excerpt
                )
                result = structured_llm.invoke(prompt)
                assessments.append(result)
                logger.info("    %s fallback assessment → %s", sub_id, result.status)
            except Exception as exc2:
                logger.warning("    %s fallback also failed: %s", sub_id, exc2)
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

    # Step 4: Tag out-of-scope subcategories (no LLM call)
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
    summaries: dict | None = None,
) -> str:
    """
    Build the consolidated gap analysis report from structured assessment data.

    This is entirely code-based — no LLM call needed.  Aggregates counts,
    builds tables, identifies missing policy templates, and produces a
    prioritized roadmap.

    Args:
        all_assessments: Mapping of function name → list of SubcategoryAssessment.
        summaries: Optional mapping of function name → FunctionGapSummary.

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
    overall_maturity = (
        _compute_maturity(flat_in_scope) if flat_in_scope else "Not Started"
    )

    lines: list[str] = []

    # ---- Section 1: Executive Summary ----
    lines.append("# NIST CSF Gap Analysis — Consolidated Report")
    lines.append("*(CIS MS-ISAC Policy Template Guide 2024 Alignment)*\n")
    lines.append("## 1. Executive Summary")
    lines.append(f"- **Overall Maturity** (in-scope only): {overall_maturity}")
    lines.append(
        f"- **Total Subcategories**: {total_sub} (In Scope: {total_in}, Out of Scope: {total_out})"
    )
    lines.append(
        f"- **In-Scope Results**: Addressed: {total_addr} | Partially Addressed: {total_part} | Not Addressed: {total_na}"
    )

    if total_na > 0:
        worst_fn = max(func_stats, key=lambda f: func_stats[f]["not_addressed"])
        lines.append(
            f"- **Critical Finding**: {total_na} in-scope subcategories are not addressed. "
            f"The {worst_fn} function has the most gaps ({func_stats[worst_fn]['not_addressed']} not addressed)."
        )
    else:
        lines.append(
            "- **Critical Finding**: All in-scope subcategories have at least partial coverage."
        )
    lines.append("")

    # ---- Section 1.5: Per-Function Executive Summaries ----
    if summaries:
        lines.append("## 1.5 Per-Function Executive Summaries\n")
        for fn in NIST_FUNCTION_ORDER:
            s = summaries.get(fn)
            if s is None:
                continue
            lines.append(f"### {fn}")
            lines.append(f"**Maturity**: {s.maturity_rating}\n")
            lines.append(s.executive_summary)
            lines.append("")
            if s.critical_gaps:
                lines.append("**Critical Gaps:**")
                for gap in s.critical_gaps[:3]:
                    lines.append(f"- {gap}")
                lines.append("")
        lines.append("")

    # ---- Section 2: Maturity by Function ----
    lines.append("## 2. Maturity by Function")
    lines.append(
        "| Function | Rating | In Scope | Addressed | Partial | Not Addressed | Out of Scope |"
    )
    lines.append(
        "|----------|--------|----------|-----------|---------|---------------|--------------|"
    )
    for fn in NIST_FUNCTION_ORDER:
        s = func_stats[fn]
        lines.append(
            f"| {fn} | {s['maturity']} | {s['in_scope']} | "
            f"{s['addressed']} | {s['partial']} | {s['not_addressed']} | {s['out_scope']} |"
        )
    lines.append("")

    # ---- Section 3: In-Scope Gaps (Not Addressed) ----
    not_addressed_gaps = [
        (fn, a) for fn, a in all_in_scope if a.status == "Not Addressed"
    ]
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
    partial_gaps = [
        (fn, a) for fn, a in all_in_scope if a.status == "Partially Addressed"
    ]
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

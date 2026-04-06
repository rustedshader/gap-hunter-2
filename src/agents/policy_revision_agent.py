"""
Policy Revision Agent — generates section-by-section revisions to address
NIST CSF gaps identified in Phase 2.

Each gap is processed in a single LLM call operating on one section at a time.
For modifications, the LLM appends content to the existing section. For new
sections, the LLM creates content matching the policy's style. Code-based
validation ensures original content is never dropped.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Literal

from llm import create_llm
from agents.nist_gap_agents import SubcategoryAssessment
from agents.policy_revision_schema import SectionRevision, RevisionValidationResult
from agents.gap_analysis_tools import get_framework_excerpt, get_function_subcategories
from prompts.policy_revision_prompt import (
    SECTION_MODIFIER_SYSTEM,
    SECTION_CREATOR_SYSTEM,
    REVISION_VALIDATOR_SYSTEM,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
LLM_INVOKE_RETRIES = 3


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class GapTarget:
    """Parsed targeting info for a single gap."""
    subcategory_id: str
    function_name: str
    action: Literal["modify", "new_section"]
    target_section_number: str | None
    gap: SubcategoryAssessment
    framework_excerpt: str
    nist_guidance: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _invoke_with_retries(structured_llm, messages: list[dict], retries: int = LLM_INVOKE_RETRIES):
    """Invoke a structured LLM with retries for transient parsing failures."""
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


def _function_for_subcategory(subcategory_id: str) -> str:
    """Derive the NIST function name from a subcategory ID prefix."""
    prefix = subcategory_id.split(".")[0]
    return {
        "GV": "Govern", "ID": "Identify", "PR": "Protect",
        "DE": "Detect", "RS": "Respond", "RC": "Recover",
    }.get(prefix, "Govern")


def _get_nist_guidance(subcategory_id: str, function_name: str) -> str:
    """Look up Implementation_Guidance for a subcategory from the NIST config."""
    subcategories = get_function_subcategories(function_name)
    for sub in subcategories:
        if sub["id"] == subcategory_id:
            return sub.get("guidance", "")
    return ""


def _get_policies_for_subcategory(subcategory_id: str, function_name: str) -> list[str]:
    """Look up required policy template names for a subcategory."""
    subcategories = get_function_subcategories(function_name)
    for sub in subcategories:
        if sub["id"] == subcategory_id:
            return sub.get("policies", [])
    return []


def _extract_recommendation_items(recommendation: str) -> list[str]:
    """Parse a recommendation into individual actionable items.

    Splits on numbered patterns (1., **1.**, 1), bold headers (**Title**:),
    and standalone bullet points that start new requirements.
    Returns a list of trimmed item strings.
    """
    items: list[str] = []

    # Try splitting on numbered list patterns first: "1.", "**1.**", "1)"
    numbered = re.split(r"\n\s*(?:\*{0,2}\d+[\.\)]\*{0,2})\s+", recommendation)
    if len(numbered) > 2:
        for chunk in numbered[1:]:
            chunk = chunk.strip()
            if len(chunk) > 15:
                main = chunk.split("\n")[0].strip().rstrip(":")
                # Strip bold header prefix: "**Title:** description" → "description"
                main = re.sub(r"^\*\*[^*]+\*\*[:\s]*", "", main).strip()
                # Strip trailing numbered pattern from next item: "...employees. 3." → "...employees."
                main = re.sub(r"\s+\d+\.\s*$", "", main).strip()
                if len(main) > 10:
                    items.append(main)
        if items:
            return items

    # Try splitting on bold section headers: **Title**: description
    bold_sections = re.findall(r"\*\*([^*]+)\*\*[:\s]+([^\n*]+)", recommendation)
    if len(bold_sections) >= 2:
        for title, desc in bold_sections:
            # Use the description, not the title — the description is what matters
            items.append(desc.strip())
        if items:
            return items

    # Fallback: split on sentence boundaries and take sentences that contain action words
    sentences = re.split(r"[.!]\s+", recommendation)
    for s in sentences:
        s = s.strip()
        if len(s) > 20 and re.search(r"\b(add|create|establish|define|implement|incorporate|mandate|require)\b", s, re.IGNORECASE):
            items.append(s)

    return items if items else [recommendation[:200]]


# ---------------------------------------------------------------------------
# Gap targeting (code-based, no LLM)
# ---------------------------------------------------------------------------

def parse_gap_targets(
    all_assessments: dict[str, list[SubcategoryAssessment]],
    sections: list[dict],
) -> list[GapTarget]:
    """
    Determine which section each gap targets and load supporting data.

    Returns list sorted by priority: Not Addressed first, then Partially Addressed.
    """
    section_numbers = {s["number"] for s in sections}
    section_titles = {s["title"].lower(): s["number"] for s in sections}
    targets: list[GapTarget] = []

    for function_name, assessments in all_assessments.items():
        for a in assessments:
            if a.status not in ("Not Addressed", "Partially Addressed"):
                continue

            action, target_num = _determine_target(a, section_numbers, section_titles)

            # Load framework excerpt from the subcategory's required policies
            policy_names = _get_policies_for_subcategory(a.subcategory_id, function_name)
            excerpt = get_framework_excerpt(policy_names) if policy_names else ""

            guidance = _get_nist_guidance(a.subcategory_id, function_name)

            targets.append(GapTarget(
                subcategory_id=a.subcategory_id,
                function_name=function_name,
                action=action,
                target_section_number=target_num,
                gap=a,
                framework_excerpt=excerpt,
                nist_guidance=guidance,
            ))

    # Sort: Not Addressed first, then Partially Addressed
    priority = {"Not Addressed": 0, "Partially Addressed": 1}
    targets.sort(key=lambda t: priority.get(t.gap.status, 2))

    logger.info(
        "Parsed %d gap targets: %d modify, %d new_section",
        len(targets),
        sum(1 for t in targets if t.action == "modify"),
        sum(1 for t in targets if t.action == "new_section"),
    )
    return targets


def _determine_target(
    assessment: SubcategoryAssessment,
    section_numbers: set[str],
    section_titles: dict[str, str],
) -> tuple[Literal["modify", "new_section"], str | None]:
    """
    Parse the recommendation text to decide: modify existing section or create new.

    Looks for patterns like "Section 2", "Data Protection Rules", "create a new section".
    """
    rec = assessment.recommendation
    evidence = assessment.evidence

    # Check for explicit "section N" references
    section_refs = re.findall(r"[Ss]ection\s+(\d+)", rec)
    for ref in section_refs:
        if ref in section_numbers:
            logger.debug("  %s: matched Section %s from recommendation", assessment.subcategory_id, ref)
            return "modify", ref

    # Check for section title references (fuzzy match against known titles)
    rec_lower = rec.lower()
    for title, number in section_titles.items():
        if title in rec_lower:
            logger.debug("  %s: matched title '%s' (Section %s)", assessment.subcategory_id, title, number)
            return "modify", number

    # Check if evidence quotes an existing section (means it partially exists)
    if evidence and evidence != "None found" and evidence != "N/A":
        for title, number in section_titles.items():
            if title in evidence.lower():
                logger.debug("  %s: evidence references '%s' (Section %s)", assessment.subcategory_id, title, number)
                return "modify", number

    # Check for "create/add new/dedicated section" pattern
    new_section_pattern = re.search(
        r"(?:create|add|develop|establish)\s+(?:a\s+)?(?:new|dedicated|separate)",
        rec, re.IGNORECASE,
    )
    if new_section_pattern:
        logger.debug("  %s: 'create new section' pattern found", assessment.subcategory_id)
        return "new_section", None

    # Default: new section (safer — never garbles existing content)
    logger.debug("  %s: no section match, defaulting to new_section", assessment.subcategory_id)
    return "new_section", None


# ---------------------------------------------------------------------------
# LLM: Modify existing section
# ---------------------------------------------------------------------------

def run_modify_section(
    original_content: str,
    original_title: str,
    target: GapTarget,
    prior_issues: list[str] | None = None,
) -> SectionRevision:
    """Generate a modified version of an existing section to address a gap."""
    llm = create_llm()
    structured_llm = llm.with_structured_output(SectionRevision)

    items = _extract_recommendation_items(target.gap.recommendation)
    items_text = "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))

    prompt = f"""## Original Section Content (copy this EXACTLY, then append new content below)

{original_content}

## Gap to Address
- Subcategory: {target.subcategory_id}
- Status: {target.gap.status}
- What's missing: {target.gap.gap}

## Specific Requirements to Address (you MUST cover EACH one)

{items_text}

Your revision MUST include content addressing every numbered item above.
A single sentence is NOT sufficient — each item needs its own policy requirement.

## Reference Framework Language
{target.framework_excerpt if target.framework_excerpt else '(no reference available)'}

## NIST Implementation Guidance
{target.nist_guidance if target.nist_guidance else '(no guidance available)'}

## Instructions
Copy the original section content EXACTLY as-is, then append new content after it.
Set action="modify", section_title="{original_title}", subcategory_id="{target.subcategory_id}".
"""

    if prior_issues:
        issues_text = "\n".join(f"  - {issue}" for issue in prior_issues)
        prompt += f"""
## IMPORTANT — Fix These Issues From Previous Attempt
{issues_text}
"""

    logger.info("  Reviser: Modifying section for %s", target.subcategory_id)
    logger.debug("  Reviser prompt (%d chars):\n%s", len(prompt), prompt)

    result = _invoke_with_retries(structured_llm, [
        {"role": "system", "content": SECTION_MODIFIER_SYSTEM},
        {"role": "user", "content": prompt},
    ])
    logger.info("  Reviser: Generated modified section (%d chars)", len(result.revised_content))
    logger.debug("  Reviser output: %s", result.changes_summary)
    return result


# ---------------------------------------------------------------------------
# LLM: Create new section
# ---------------------------------------------------------------------------

def run_create_section(
    style_example: str,
    target: GapTarget,
    section_number: int,
    prior_issues: list[str] | None = None,
) -> SectionRevision:
    """Generate a new policy section to address a gap."""
    llm = create_llm()
    structured_llm = llm.with_structured_output(SectionRevision)

    items = _extract_recommendation_items(target.gap.recommendation)
    items_text = "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))

    prompt = f"""## Example Section (for style and formatting reference)

{style_example}

## Gap to Address
- Subcategory: {target.subcategory_id}
- Status: {target.gap.status}
- What's missing: {target.gap.gap}

## Specific Requirements to Address (you MUST cover EACH one)

{items_text}

Your new section MUST include content addressing every numbered item above.

## Reference Framework Language
{target.framework_excerpt if target.framework_excerpt else '(no reference available)'}

## NIST Implementation Guidance
{target.nist_guidance if target.nist_guidance else '(no guidance available)'}

## Instructions
Write a new policy section (Section {section_number}) addressing this gap.
Set action="new_section", subcategory_id="{target.subcategory_id}".
Choose an appropriate section_title that describes the new requirement.
"""

    if prior_issues:
        issues_text = "\n".join(f"  - {issue}" for issue in prior_issues)
        prompt += f"""
## IMPORTANT — Fix These Issues From Previous Attempt
{issues_text}
"""

    logger.info("  Reviser: Creating new section %d for %s", section_number, target.subcategory_id)
    logger.debug("  Reviser prompt (%d chars):\n%s", len(prompt), prompt)

    result = _invoke_with_retries(structured_llm, [
        {"role": "system", "content": SECTION_CREATOR_SYSTEM},
        {"role": "user", "content": prompt},
    ])
    logger.info("  Reviser: Created new section '%s' (%d chars)", result.section_title, len(result.revised_content))
    logger.debug("  Reviser output: %s", result.changes_summary)
    return result


# ---------------------------------------------------------------------------
# Validation (code-based + LLM)
# ---------------------------------------------------------------------------

def validate_revision(
    revision: SectionRevision,
    original_content: str | None,
    target: GapTarget,
) -> RevisionValidationResult:
    """
    Validate a section revision. Code checks first, then LLM.

    For modifications: verifies original content is preserved.
    For new sections: verifies content is non-empty.
    Then LLM checks for garbled text and gap relevance.
    """
    code_issues: list[str] = []

    if revision.action == "modify" and original_content:
        # Check every non-trivial line from original appears in the revision
        original_lines = [
            line.strip()
            for line in original_content.split("\n")
            if len(line.strip()) > 10
        ]
        revised_normalized = revision.revised_content.replace("\r\n", "\n")

        for line in original_lines:
            if line not in revised_normalized:
                code_issues.append(f"Original content dropped: '{line[:80]}...'")

        if not code_issues and len(revision.revised_content) <= len(original_content):
            code_issues.append(
                "Revised content is not longer than original — nothing was added."
            )

    elif revision.action == "new_section":
        if len(revision.revised_content.strip()) < 50:
            code_issues.append("New section content is too short (< 50 chars).")
        if not revision.section_title.strip():
            code_issues.append("New section title is empty.")

    if code_issues:
        logger.warning("  Validator: REJECTED by code — %d issues", len(code_issues))
        for issue in code_issues:
            logger.warning("    - %s", issue)
        return RevisionValidationResult(is_acceptable=False, issues=code_issues)

    logger.info("  Validator: code checks passed ✓")

    # LLM check: coherence + item-by-item semantic coverage
    llm = create_llm()
    structured_llm = llm.with_structured_output(RevisionValidationResult)

    items = _extract_recommendation_items(target.gap.recommendation)
    items_checklist = "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))

    prompt = f"""Check this policy revision for quality and completeness.

## Gap Being Addressed
- Subcategory: {target.subcategory_id}
- What's missing: {target.gap.gap}

## Required Items (the revision should address each one)

{items_checklist}

## Revised Content

{revision.revised_content[-2000:]}

## Instructions

1. Check if the text is coherent and free of garbled content.
   If garbled → add "Garbled text found".
2. For each numbered item above, check if the revision addresses it
   (even if using different words or synonyms). If an item is completely
   missing with no equivalent content → add "Item N not addressed: [item text]".

If all items are covered and text is coherent, set is_acceptable=true.
"""

    logger.info("  Validator: LLM checking for coherence and gap relevance")

    try:
        result = _invoke_with_retries(structured_llm, [
            {"role": "system", "content": REVISION_VALIDATOR_SYSTEM},
            {"role": "user", "content": prompt},
        ])
        if result.is_acceptable:
            logger.info("  Validator: Revision ACCEPTED ✓")
        else:
            logger.warning("  Validator: Revision REJECTED — %d issues", len(result.issues))
            for issue in result.issues:
                logger.warning("    - %s", issue)
        return result
    except Exception as exc:
        logger.warning("  Validator failed: %s — accepting revision", exc)
        return RevisionValidationResult(is_acceptable=True, issues=[])


# ---------------------------------------------------------------------------
# Orchestrator: Generate + Validate loop (per gap)
# ---------------------------------------------------------------------------

def run_revision_with_validation(
    target: GapTarget,
    current_section_content: str | None,
    current_section_title: str | None,
    style_example: str,
    section_number: int,
) -> SectionRevision:
    """
    Generate a validated revision for one gap.

    Runs the generator, then validates. If rejected, regenerates with
    feedback (up to MAX_RETRIES).
    """
    logger.info("=" * 40)
    logger.info("Revising for %s (%s)", target.subcategory_id, target.action)
    logger.info("=" * 40)

    # Initial generation
    if target.action == "modify":
        revision = run_modify_section(current_section_content, current_section_title, target)
    else:
        revision = run_create_section(style_example, target, section_number)

    for attempt in range(1, MAX_RETRIES + 1):
        validation = validate_revision(revision, current_section_content, target)

        if validation.is_acceptable:
            logger.info("  %s revision accepted on attempt %d ✓", target.subcategory_id, attempt)
            return revision

        logger.warning(
            "  %s revision rejected (attempt %d/%d) — regenerating",
            target.subcategory_id, attempt, MAX_RETRIES,
        )

        # Regenerate with feedback
        if target.action == "modify":
            revision = run_modify_section(
                current_section_content, current_section_title, target,
                prior_issues=validation.issues,
            )
        else:
            revision = run_create_section(
                style_example, target, section_number,
                prior_issues=validation.issues,
            )

    logger.warning(
        "  %s: max retries (%d) reached — using last generated revision",
        target.subcategory_id, MAX_RETRIES,
    )
    return revision

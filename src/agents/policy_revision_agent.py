"""
Policy Revision Agent — RAPTOR + CoVe architecture.

Three-role pipeline per section:

  Role A  Addition Writer + CoVe Validation (per gap):
    1. Writer generates a delta block for ONE gap only (never reproduces the section).
    2. CoVe Questioner generates 3-5 yes/no verification questions from the gap text.
    3. CoVe Verifier answers each question against the block independently.
    4. If any question fails, the Writer regenerates with the failed questions as feedback.
    After all gaps for a cluster (NIST function group) are processed:
    5. Cluster Summarizer produces a ~200-char RAPTOR level-1 summary.
       This summary is passed to subsequent Addition Writers as context to avoid repetition.

  Role C  Integration Editor (once per section, after all clusters):
    6. Merges original section + all AdditionBlocks into one fluent cohesive section.
    7. Integration Validator confirms all subcategory IDs are present and text is coherent.

  Role D  Section Creator (for new_section gaps — unchanged from prior design):
    8. Creates a complete new section for gaps that don't target any existing section.
    9. Validated with CoVe.

No regex is used anywhere in this module. Section targeting uses an LLM call.
Recommendation parsing uses raw text — the LLM receives the full recommendation
and gap fields and reasons about them directly.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Literal

from pydantic import BaseModel, Field

from llm import create_llm
from agents.nist_gap_agents import SubcategoryAssessment
from agents.policy_revision_schema import (
    AdditionBlock,
    ClusterSummary,
    IntegrationResult,
    RevisionValidationResult,
    SectionRevision,
    VerificationQuestion,
)
from agents.gap_analysis_tools import get_framework_excerpt, get_function_subcategories
from agents.text_summarizer import summarize_lossless
from prompts.policy_revision_prompt import (
    ADDITION_WRITER_SYSTEM,
    CLUSTER_SUMMARIZER_SYSTEM,
    INTEGRATION_EDITOR_SYSTEM,
    INTEGRATION_VALIDATOR_SYSTEM,
    SECTION_CREATOR_SYSTEM,
    SECTION_TARGETER_SYSTEM,
    VERIFICATION_QUESTIONER_SYSTEM,
    VERIFIER_SYSTEM,
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


# LLM schema for section targeting
class SectionTargetResult(BaseModel):
    """LLM output for deciding which section a gap targets."""

    action: Literal["modify", "new_section"] = Field(
        description="'modify' if the gap belongs in an existing section, 'new_section' otherwise.",
    )
    section_number: str | None = Field(
        default=None,
        description="The section number to modify (e.g. '4'). None if action is 'new_section'.",
    )


# LLM schema for generating multiple VerificationQuestions at once
class VerificationQuestionsResult(BaseModel):
    """CoVe step-2 output — a list of verification questions for one gap."""

    questions: list[str] = Field(
        description="3 to 5 specific yes/no questions that verify the block addresses the gap.",
    )


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------


def _invoke_with_retries(
    structured_llm, messages: list[dict], retries: int = LLM_INVOKE_RETRIES
):
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
                    attempt,
                    retries,
                    exc,
                )
            else:
                logger.error(
                    "    LLM invoke failed after %d attempts: %s",
                    retries,
                    exc,
                )
    raise last_exc


# ---------------------------------------------------------------------------
# Gap targeting — LLM-based, no regex
# ---------------------------------------------------------------------------


def classify_gap_target(
    assessment: SubcategoryAssessment,
    sections: list[dict],
) -> tuple[Literal["modify", "new_section"], str | None]:
    """
    Use an LLM to determine which section a gap should target.

    Replaces the regex-based _determine_target. The LLM receives the
    recommendation text and list of section titles and returns a structured
    decision. This is one cheap structured-output call per gap.

    Args:
        assessment: The SubcategoryAssessment with recommendation text.
        sections: List of section dicts with 'number' and 'title' keys.

    Returns:
        Tuple of (action, section_number_or_None).
    """
    sections_list = "\n".join(
        f"  Section {s['number']}: {s['title']}" for s in sections
    )

    prompt = (
        f"Existing policy sections:\n{sections_list}\n\n"
        f"Gap subcategory: {assessment.subcategory_id}\n"
        f"Gap description: {assessment.gap}\n\n"
        f"Recommendation:\n{assessment.recommendation}\n\n"
        f"Which existing section should this gap be added to? "
        f"If none fits, return action='new_section'."
    )

    llm = create_llm()
    structured_llm = llm.with_structured_output(SectionTargetResult)

    try:
        result = _invoke_with_retries(
            structured_llm,
            [
                {"role": "system", "content": SECTION_TARGETER_SYSTEM},
                {"role": "user", "content": prompt},
            ],
        )
        logger.debug(
            "  %s: targeter → action=%s section=%s",
            assessment.subcategory_id,
            result.action,
            result.section_number,
        )
        # Validate the section number actually exists
        if result.action == "modify" and result.section_number:
            known = {s["number"] for s in sections}
            if result.section_number not in known:
                logger.warning(
                    "  %s: targeter returned unknown section %s — switching to new_section",
                    assessment.subcategory_id,
                    result.section_number,
                )
                return "new_section", None
        return result.action, result.section_number
    except Exception as exc:
        logger.warning(
            "  %s: section targeter failed (%s) — defaulting to new_section",
            assessment.subcategory_id,
            exc,
        )
        return "new_section", None


from agents.gap_analysis_tools import build_allowlist_for_templates

# ---------------------------------------------------------------------------
# Keyword → CIS MS-ISAC template name map.
# Keys are frozensets of lowercase keywords; values are the EXACT policy
# template names as they appear in nist_config.yaml "Policies" fields.
# Covers all 35 documents in src/nist/framework-documents/.
# ---------------------------------------------------------------------------
_POLICY_KEYWORD_MAP: list[tuple[frozenset[str], list[str]]] = [
    (frozenset({"access control", "identity management", "iam", "rbac",
                "least privilege", "provisioning", "privileged access",
                "authentication policy", "identification and authentication"}),
     ["Access Control Policy", "Account Management/Access Control Standard",
      "Authentication Tokens Standard", "Identification and Authentication Policy",
      "Remote Access Standard",
      "Personnel Security Policy"]),  # joiner/mover/leaver HR lifecycle is core IAM

    (frozenset({"incident response", "incident handling", "containment",
                "eradication", "incident management", "cyber incident"}),
     ["Computer Security Threat Response Policy", "Cyber Incident Response Standard",
      "Incident Response Policy"]),

    (frozenset({"contingency planning", "business continuity",
                "disaster recovery", "bcp", "drp", "continuity of operations"}),
     ["Contingency Planning Policy"]),

    (frozenset({"risk assessment", "risk management", "risk register",
                "risk appetite", "risk tolerance"}),
     ["Risk Assessment Policy", "Information Security Risk Management Standard",
      "Planning Policy"]),

    (frozenset({"patch management", "patching", "vulnerability management",
                "software update", "firmware update"}),
     ["Patch Management Standard", "Vulnerability Scanning Standard"]),

    (frozenset({"vulnerability scanning", "vulnerability assessment",
                "penetration testing", "vuln scan"}),
     ["Vulnerability Scanning Standard"]),

    (frozenset({"configuration management", "secure configuration",
                "hardening", "baseline configuration", "cmdb",
                "configuration baseline"}),
     ["Configuration Management Policy", "Secure Configuration Standard"]),

    (frozenset({"data privacy", "data protection", "gdpr", "hipaa",
                "personal data", "phi", "pii", "personally identifiable",
                "privacy policy"}),
     ["Encryption Standard", "Media Protection Policy",
      "Sanitization Secure Disposal Standard", "Information Classification Standard"]),

    (frozenset({"encryption", "cryptograph", "key management", "tls", "aes",
                "encryption standard"}),
     ["Encryption Standard"]),

    (frozenset({"information security management", "isms"}),
     ["Information Security Policy", "Information Security Risk Management Standard",
      "Security Awareness and Training Policy",
      "Acceptable Use of Information Technology Resource Policy"]),

    (frozenset({"information security policy", "overall security policy",
                "master security policy", "enterprise security policy"}),
     ["Information Security Policy"]),

    (frozenset({"security awareness", "security training",
                "awareness training", "phishing training"}),
     ["Security Awareness and Training Policy",
      "Acceptable Use of Information Technology Resource Policy"]),

    (frozenset({"acceptable use", "aup", "computer use policy",
                "it use policy", "technology use"}),
     ["Acceptable Use of Information Technology Resource Policy"]),

    (frozenset({"auditing", "audit log", "accountability",
                "audit trail", "auditing and accountability"}),
     ["Auditing and Accountability Policy", "Security Logging Standard"]),

    (frozenset({"security logging", "log management", "log retention",
                "logging standard", "siem policy"}),
     ["Security Logging Standard", "Auditing and Accountability Policy"]),

    (frozenset({"remote access", "vpn", "telework", "work from home",
                "remote access standard"}),
     ["Remote Access Standard"]),

    (frozenset({"personnel security", "hr security", "background check",
                "employee security", "onboarding security", "offboarding",
                "personnel security policy"}),
     ["Personnel Security Policy"]),

    (frozenset({"physical security", "environmental protection",
                "physical access", "facility security",
                "data center access", "physical and environmental"}),
     ["Physical and Environmental Protection Policy"]),

    (frozenset({"maintenance policy", "system maintenance",
                "maintenance window", "maintenance standard"}),
     ["Maintenance Policy"]),

    (frozenset({"media protection", "media handling",
                "removable media", "usb", "portable media"}),
     ["Media Protection Policy"]),

    (frozenset({"mobile device", "byod", "smartphone",
                "tablet security", "mobile security"}),
     ["Mobile Device Security"]),

    (frozenset({"information classification", "data classification",
                "classification standard", "sensitivity label",
                "classification scheme"}),
     ["Information Classification Standard"]),

    (frozenset({"system development", "sdlc",
                "software development life cycle",
                "secure development", "devops security",
                "secure sdlc"}),
     ["Secure System Development Life Cycle Standard"]),

    (frozenset({"security assessment", "security authorization",
                "authorization policy", "assessment and authorization",
                "security assessment policy"}),
     ["Security Assessment and Authorization Policy"]),

    (frozenset({"communications protection", "network security",
                "network protection", "firewall policy",
                "system communications protection"}),
     ["System and Communications Protection Policy"]),

    (frozenset({"system integrity", "information integrity",
                "malware", "anti-virus", "antivirus",
                "integrity policy", "system and information integrity"}),
     ["System and Information Integrity Policy"]),

    (frozenset({"acquisition", "vendor management", "supply chain",
                "third party", "third-party", "procurement security",
                "services acquisition"}),
     ["Systems and Services Acquisition Policy"]),

    (frozenset({"sanitization", "secure disposal",
                "data destruction", "disk wiping",
                "sanitization standard"}),
     ["Sanitization Secure Disposal Standard"]),

    (frozenset({"planning policy", "system security plan",
                "ssp", "security planning"}),
     ["Planning Policy"]),
]

# Subcategory IDs that are EXCLUDED even when their template matches.
# These map to IAM/access-control templates for indirect reasons
# (e.g. "access management depends on asset inventory") but adding their
# full implementation procedures to an IAM policy creates wrong-domain content.
_EXPLICIT_EXCLUSIONS: dict[str, set[str]] = {
    "access_control_templates": {
        "ID.AM-1", "ID.AM-2",          # hardware/software inventory → asset mgmt standard
        "GV.SC-01", "GV.SC-03", "GV.SC-04", "GV.SC-05",
        "GV.SC-06", "GV.SC-07", "GV.SC-09", "GV.SC-10",  # supply chain → separate policy
    }
}


def detect_policy_templates(sections: list[dict]) -> list[str]:
    """
    Match the policy's title and first-section content against the keyword map
    and return the list of CIS MS-ISAC policy template names that best describe
    this policy's domain. Covers all 35 framework documents.

    No LLM — pure keyword matching, zero latency.
    """
    text = " ".join(
        (s.get("title", "") + " " + s.get("content", ""))
        for s in sections[:3]
    ).lower()

    best_templates: list[str] = []
    best_score = 0

    for keywords, templates in _POLICY_KEYWORD_MAP:
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_templates = templates

    if best_score == 0:
        logger.info("  Domain detection: no keyword match — no domain filter applied")
        return []

    logger.info(
        "  Domain detection: matched templates %s (score=%d)",
        best_templates, best_score,
    )
    return best_templates


def build_revision_allowlist(sections: list[dict]) -> set[str]:
    """
    Compute the set of NIST subcategory IDs that should be revised in this policy.
    Derived from nist_config.yaml — no hardcoded subcategory IDs.

    Returns empty set if domain cannot be determined (no filter applied).
    """
    templates = detect_policy_templates(sections)
    if not templates:
        return set()   # empty = no restriction

    allowlist = build_allowlist_for_templates(templates)

    # Apply explicit exclusions for known false-positive mappings
    # (subcategories that map to access-control templates for indirect reasons)
    ac_templates = {t.lower() for t in templates}
    ac_indicator = any(
        t in ac_templates for t in {
            "access control policy",
            "identification and authentication policy",
            "account management/access control standard",
        }
    )
    if ac_indicator:
        allowlist -= _EXPLICIT_EXCLUSIONS["access_control_templates"]
        logger.info(
            "  Applied access-control exclusions: removed ID.AM-1/2 and GV.SC-* from allowlist"
        )

    logger.info("  Revision allowlist: %d subcategories", len(allowlist))
    return allowlist


def parse_gap_targets(
    all_assessments: dict[str, list[SubcategoryAssessment]],
    sections: list[dict],
) -> list[GapTarget]:
    """
    Determine which section each gap targets and load supporting data.

    Uses an LLM call per gap for section targeting (no regex).
    Returns list sorted by priority: Not Addressed first, then Partially Addressed.
    """
    # Build allowlist from nist_config.yaml — zero hardcoded subcategory IDs
    revision_allowlist = build_revision_allowlist(sections)
    using_filter = bool(revision_allowlist)

    targets: list[GapTarget] = []

    for function_name, assessments in all_assessments.items():
        for a in assessments:
            if a.status not in ("Not Addressed", "Partially Addressed"):
                continue

            # Domain filter — skip subcategories that belong in a different policy.
            if using_filter and a.subcategory_id not in revision_allowlist:
                logger.info(
                    "  Skipping %s — not in revision allowlist for this policy domain",
                    a.subcategory_id,
                )
                continue

            # Secondary filter: skip gaps whose recommendation explicitly points
            # to a separate policy document (belt-and-suspenders with domain filter).
            rec_lower = (a.recommendation or "").lower()
            separate_policy_signals = (
                "dedicated" in rec_lower and "policy" in rec_lower,
                "separate policy" in rec_lower,
                "create a" in rec_lower and "policy" in rec_lower,
                "establish a" in rec_lower and "policy" in rec_lower,
                "adopt the" in rec_lower and "policy" in rec_lower,
            )
            if any(separate_policy_signals):
                logger.info(
                    "  Skipping %s — recommendation points to a separate policy document",
                    a.subcategory_id,
                )
                continue

            action, target_num = classify_gap_target(a, sections)

            policy_names = _get_policies_for_subcategory(
                a.subcategory_id, function_name
            )
            excerpt = get_framework_excerpt(policy_names) if policy_names else ""
            guidance = _get_nist_guidance(a.subcategory_id, function_name)

            targets.append(
                GapTarget(
                    subcategory_id=a.subcategory_id,
                    function_name=function_name,
                    action=action,
                    target_section_number=target_num,
                    gap=a,
                    framework_excerpt=excerpt,
                    nist_guidance=guidance,
                )
            )

    priority = {"Not Addressed": 0, "Partially Addressed": 1}
    targets.sort(key=lambda t: priority.get(t.gap.status, 2))

    logger.info(
        "Parsed %d gap targets: %d modify, %d new_section",
        len(targets),
        sum(1 for t in targets if t.action == "modify"),
        sum(1 for t in targets if t.action == "new_section"),
    )
    return targets


# ---------------------------------------------------------------------------
# NIST config helpers
# ---------------------------------------------------------------------------


def _get_nist_guidance(subcategory_id: str, function_name: str) -> str:
    subcategories = get_function_subcategories(function_name)
    for sub in subcategories:
        if sub["id"] == subcategory_id:
            return sub.get("guidance", "")
    return ""


def _get_policies_for_subcategory(subcategory_id: str, function_name: str) -> list[str]:
    subcategories = get_function_subcategories(function_name)
    for sub in subcategories:
        if sub["id"] == subcategory_id:
            return sub.get("policies", [])
    return []


def _function_for_subcategory(subcategory_id: str) -> str:
    prefix = subcategory_id.split(".")[0]
    return {
        "GV": "Govern",
        "ID": "Identify",
        "PR": "Protect",
        "DE": "Detect",
        "RS": "Respond",
        "RC": "Recover",
    }.get(prefix, "Govern")


# ---------------------------------------------------------------------------
# Role A — Addition Writer
# ---------------------------------------------------------------------------


def run_write_addition(
    target: GapTarget,
    original_section_content: str,
    original_section_title: str,
    prior_additions_summary: str,
    prior_issues: list[str] | None = None,
) -> AdditionBlock:
    """
    Generate a delta block for ONE gap. Never reproduces the full section.

    The LLM receives:
    - The original section (read-only, for style reference only)
    - A compact summary of what prior additions already cover (RAPTOR context)
    - The gap description, recommendation, NIST guidance, and framework excerpt

    It writes ONLY the new content for this specific gap.

    Args:
        target: The gap to address.
        original_section_content: The original section text (style reference only).
        original_section_title: Title of the section being modified.
        prior_additions_summary: RAPTOR-style summary of what has already been added.
        prior_issues: CoVe failure feedback from a previous attempt.

    Returns:
        AdditionBlock containing only the new content.
    """
    llm = create_llm()
    structured_llm = llm.with_structured_output(AdditionBlock)

    # Truncate original to a style sample — we don't need the full thing
    # Compress the original section to a style reference — the model only needs to
    # understand the tone and formatting, not reproduce it, so lossy compression
    # is acceptable here. Use summarize_lossless so nothing structural is cut mid-sentence.
    style_sample = summarize_lossless(
        original_section_content,
        context_hint=f"policy section '{original_section_title}' used as style reference only",
        threshold=4_000,
    )

    # Compress recommendation if it is long — keeps the Addition Writer prompt focused
    recommendation = summarize_lossless(
        target.gap.recommendation,
        context_hint=f"NIST {target.subcategory_id} gap recommendation",
        threshold=4_000,
    )
    nist_guidance = (
        summarize_lossless(
            target.nist_guidance,
            context_hint=f"NIST {target.subcategory_id} implementation guidance",
            threshold=4_000,
        )
        if target.nist_guidance
        else "(none available)"
    )

    prompt = (
        f"## Section Being Modified: {original_section_title}\n\n"
        f"### Style Reference (first 800 chars of original — do NOT reproduce this)\n\n"
        f"{style_sample}\n\n"
        f"---\n\n"
        f"### What Has Already Been Added (do NOT repeat these topics)\n\n"
        f"{prior_additions_summary}\n\n"
        f"---\n\n"
        f"### Gap to Address\n\n"
        f"Subcategory: {target.subcategory_id}\n"
        f"Status: {target.gap.status}\n"
        f"What is missing: {target.gap.gap}\n\n"
        f"### Recommendation\n\n"
        f"{recommendation}\n\n"
        f"### NIST Implementation Guidance\n\n"
        f"{nist_guidance}\n\n"
        f"### Reference Framework Language\n\n"
        f"{target.framework_excerpt if target.framework_excerpt else '(none available)'}\n\n"
        f"---\n\n"
        f"Write the new content block for subcategory {target.subcategory_id}. "
        f"Address every requirement in the recommendation above."
    )

    if prior_issues:
        issues_text = "\n".join(f"  - {issue}" for issue in prior_issues)
        prompt += (
            f"\n\n### IMPORTANT — Fix These Issues From Previous Attempt\n\n"
            f"{issues_text}"
        )

    logger.info("  Addition Writer: writing block for %s", target.subcategory_id)
    logger.debug("  Addition Writer prompt (%d chars)", len(prompt))

    result = _invoke_with_retries(
        structured_llm,
        [
            {"role": "system", "content": ADDITION_WRITER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )
    logger.info(
        "  Addition Writer: generated block '%s' (%d chars)",
        result.heading,
        len(result.content),
    )
    return result


# ---------------------------------------------------------------------------
# Role A — CoVe Validation (Steps 2 + 3)
# ---------------------------------------------------------------------------


def _generate_verification_questions(target: GapTarget) -> list[str]:
    """
    CoVe Step 2: Generate 3-5 yes/no verification questions for a gap.

    The LLM reads only the gap description and recommendation.
    No block content is involved at this stage.

    Returns:
        List of question strings.
    """
    llm = create_llm()
    structured_llm = llm.with_structured_output(VerificationQuestionsResult)

    prompt = (
        f"Gap subcategory: {target.subcategory_id}\n"
        f"What is missing: {target.gap.gap}\n\n"
        f"Full recommendation:\n{target.gap.recommendation}\n\n"
        f"Generate 3 to 5 specific yes/no questions that would verify "
        f"a policy block actually addresses this gap."
    )

    logger.info("  CoVe Questioner: generating questions for %s", target.subcategory_id)

    try:
        result = _invoke_with_retries(
            structured_llm,
            [
                {"role": "system", "content": VERIFICATION_QUESTIONER_SYSTEM},
                {"role": "user", "content": prompt},
            ],
        )
        logger.info(
            "  CoVe Questioner: %d questions for %s",
            len(result.questions),
            target.subcategory_id,
        )
        return result.questions
    except Exception as exc:
        logger.warning(
            "  CoVe Questioner failed for %s: %s — skipping CoVe",
            target.subcategory_id,
            exc,
        )
        return []


def _verify_one_question(block_content: str, question: str) -> VerificationQuestion:
    """
    CoVe Step 3: Answer one verification question against the block.

    One LLM call per question — the model only needs to hold one criterion.

    Args:
        block_content: The AdditionBlock content to verify.
        question: The yes/no question to answer.

    Returns:
        VerificationQuestion with answer and evidence.
    """
    llm = create_llm()
    structured_llm = llm.with_structured_output(VerificationQuestion)

    prompt = f"Policy block to check:\n\n{block_content}\n\nQuestion: {question}"

    result = _invoke_with_retries(
        structured_llm,
        [
            {"role": "system", "content": VERIFIER_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )
    return result


def validate_addition_cove(
    block: AdditionBlock,
    target: GapTarget,
) -> RevisionValidationResult:
    """
    CoVe 4-step validation for an AdditionBlock.

    Step 1: Block already written (input).
    Step 2: Generate verification questions from the gap text.
    Step 3: Answer each question independently against the block.
    Step 4: Collect failures — any False answer becomes a rejection issue.

    Args:
        block: The AdditionBlock to validate.
        target: The GapTarget providing gap context.

    Returns:
        RevisionValidationResult — accepted if all questions pass.
    """
    # Basic length check first (code — no LLM needed)
    if len(block.content.strip()) < 80:
        return RevisionValidationResult(
            is_acceptable=False,
            issues=["Block content is too short to address any requirement."],
        )

    questions = _generate_verification_questions(target)
    if not questions:
        # Questioner failed — accept with a warning rather than blocking forever
        logger.warning(
            "  CoVe: no questions generated for %s — accepting block",
            target.subcategory_id,
        )
        return RevisionValidationResult(is_acceptable=True, issues=[])

    issues: list[str] = []
    for q in questions:
        try:
            verification = _verify_one_question(block.content, q)
            logger.debug(
                "  CoVe Verifier: Q='%s' → %s | %s",
                q[:60],
                verification.answer,
                verification.evidence[:80],
            )
            if not verification.answer:
                issues.append(f"Not addressed: {q} — {verification.evidence}")
        except Exception as exc:
            logger.warning("  CoVe Verifier failed for question '%s': %s", q[:60], exc)
            # Skip this question on error — don't block on infrastructure failures

    if issues:
        logger.warning(
            "  CoVe: block for %s REJECTED — %d questions failed",
            target.subcategory_id,
            len(issues),
        )
        for issue in issues:
            logger.warning("    - %s", issue)
        return RevisionValidationResult(is_acceptable=False, issues=issues)

    logger.info("  CoVe: block for %s ACCEPTED ✓", target.subcategory_id)
    return RevisionValidationResult(is_acceptable=True, issues=[])


# ---------------------------------------------------------------------------
# Role A — Orchestrator: Write + CoVe loop (per gap)
# ---------------------------------------------------------------------------


def run_addition_with_validation(
    target: GapTarget,
    original_section_content: str,
    original_section_title: str,
    prior_additions_summary: str,
) -> AdditionBlock:
    """
    Generate and CoVe-validate an AdditionBlock for one gap.

    Runs the Addition Writer, then CoVe-validates. On failure, regenerates
    with the failed verification questions as structured feedback.
    Up to MAX_RETRIES attempts.

    Args:
        target: The gap to address.
        original_section_content: Original section (style reference only).
        original_section_title: Section title.
        prior_additions_summary: RAPTOR cluster summary of prior additions.

    Returns:
        A validated AdditionBlock.
    """
    logger.info("=" * 40)
    logger.info("Addition Writer: %s (%s)", target.subcategory_id, target.gap.status)
    logger.info("=" * 40)

    block = run_write_addition(
        target,
        original_section_content,
        original_section_title,
        prior_additions_summary,
    )

    for attempt in range(1, MAX_RETRIES + 1):
        validation = validate_addition_cove(block, target)

        if validation.is_acceptable:
            logger.info(
                "  %s block accepted on attempt %d ✓",
                target.subcategory_id,
                attempt,
            )
            return block

        logger.warning(
            "  %s block rejected (attempt %d/%d) — regenerating",
            target.subcategory_id,
            attempt,
            MAX_RETRIES,
        )

        block = run_write_addition(
            target,
            original_section_content,
            original_section_title,
            prior_additions_summary,
            prior_issues=validation.issues,
        )

    logger.warning(
        "  %s: max retries (%d) reached — using last generated block",
        target.subcategory_id,
        MAX_RETRIES,
    )
    return block


# ---------------------------------------------------------------------------
# RAPTOR Level-1 — Cluster Summarizer
# ---------------------------------------------------------------------------


def run_cluster_summarizer(
    function_name: str,
    blocks: list[AdditionBlock],
) -> ClusterSummary:
    """
    RAPTOR Step: Summarize all AdditionBlocks in one NIST function cluster.

    The output is a compact ~200-char summary passed to subsequent Addition
    Writers so they know what has already been covered without receiving
    the full block text.

    Args:
        function_name: NIST function name (e.g. 'Protect').
        blocks: All AdditionBlocks written for this function's gaps.

    Returns:
        ClusterSummary with covered IDs and a compact summary.
    """
    if not blocks:
        return ClusterSummary(
            function_name=function_name,
            covered_ids=[],
            summary="No additions have been made yet.",
        )

    llm = create_llm()
    structured_llm = llm.with_structured_output(ClusterSummary)

    # Each block may be 800-1200 chars. Summarize each individually so the
    # subcategory ID and key requirements survive but the combined prompt stays small.
    block_inputs = []
    for b in blocks:
        compressed = summarize_lossless(
            b.content,
            context_hint=f"policy addition block for {b.subcategory_id} — {b.heading}",
            threshold=4_000,
        )
        block_inputs.append(
            f"Block for {b.subcategory_id} — {b.heading}:\n{compressed}"
        )

    blocks_text = "\n\n".join(block_inputs)

    prompt = (
        f"NIST Function: {function_name}\n\n"
        f"These blocks were written to address gaps in this function:\n\n"
        f"{blocks_text}\n\n"
        f"Summarize what has been added. List the covered subcategory IDs "
        f"and key topics so subsequent writers can avoid repeating them."
    )

    logger.info(
        "  Cluster Summarizer: summarizing %d blocks for %s",
        len(blocks),
        function_name,
    )

    try:
        result = _invoke_with_retries(
            structured_llm,
            [
                {"role": "system", "content": CLUSTER_SUMMARIZER_SYSTEM},
                {"role": "user", "content": prompt},
            ],
        )
        logger.info(
            "  Cluster Summarizer: %s — covered %s",
            function_name,
            result.covered_ids,
        )
        return result
    except Exception as exc:
        logger.warning(
            "  Cluster Summarizer failed for %s: %s — building fallback",
            function_name,
            exc,
        )
        # Fallback: build a minimal summary from block headings
        return ClusterSummary(
            function_name=function_name,
            covered_ids=[b.subcategory_id for b in blocks],
            summary=(
                f"The following topics have been added for {function_name}: "
                + ", ".join(b.heading for b in blocks)
                + "."
            ),
        )


def build_prior_summary(cluster_summaries: list[ClusterSummary]) -> str:
    """
    Build the prior additions summary string passed to each Addition Writer.

    Combines all cluster summaries into a compact context block.
    This is pure code — no LLM call.

    Args:
        cluster_summaries: All ClusterSummary objects produced so far.

    Returns:
        A short text block describing what has already been added.
    """
    if not cluster_summaries:
        return "(none yet — this is the first addition)"

    parts = []
    for cs in cluster_summaries:
        ids_str = ", ".join(cs.covered_ids) if cs.covered_ids else "none"
        parts.append(f"[{cs.function_name}] Covered IDs: {ids_str}\n  {cs.summary}")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# RAPTOR Root — Integration Editor
# ---------------------------------------------------------------------------


def run_integration_pass(
    original_content: str,
    original_title: str,
    blocks: list[AdditionBlock],
    expected_ids: list[str],
    prior_issues: list[str] | None = None,
) -> IntegrationResult:
    """
    RAPTOR root step: merge original section + all blocks into one fluent section.

    Runs once per section after all AdditionBlocks have been collected.
    The Integration Editor receives the original content and all blocks,
    and produces a single coherent policy section.

    Args:
        original_content: The original section text.
        original_title: The section title.
        blocks: All AdditionBlocks targeting this section.
        expected_ids: Subcategory IDs that must appear in the output.
        prior_issues: Integration validator feedback from a previous attempt.

    Returns:
        IntegrationResult with the merged section content.
    """
    llm = create_llm()
    structured_llm = llm.with_structured_output(IntegrationResult)

    # Summarize the original section only if it is long.
    # Most sections are under 1000 chars so this is usually a no-op.
    original_summary = summarize_lossless(
        original_content,
        context_hint=f"original policy section '{original_title}' to be preserved intact",
        threshold=4_000,
    )

    # Pass blocks as a numbered structured list — NOT as a single concatenated
    # string fed through summarize_blocks. The summarizer cannot losslessly
    # compress 10+ detailed policy blocks into ≤2000 chars; it reliably drops
    # specific requirements and causes a validator death spiral.
    # The Integration Editor receives each block individually so it can merge
    # them cleanly without losing any requirement.
    blocks_text = "\n\n".join(
        f"[Block {i + 1}/{len(blocks)} — {b.subcategory_id}: {b.heading}]\n{b.content}"
        for i, b in enumerate(blocks)
    )

    prompt = (
        f"## Section to Integrate: {original_title}\n\n"
        f"### Original Section (preserve all requirements at the top)\n\n"
        f"{original_summary}\n\n"
        f"---\n\n"
        f"### New Content Blocks to Merge ({len(blocks)} blocks)\n\n"
        f"{blocks_text}\n\n"
        f"---\n\n"
        f"Required subcategory IDs that must be covered in the output: "
        f"{', '.join(expected_ids)}\n\n"
        f"Merge the original section and all blocks into one fluent, "
        f"coherent policy section. Eliminate repetition and use consistent terminology."
    )

    if prior_issues:
        issues_text = "\n".join(f"  - {issue}" for issue in prior_issues)
        prompt += (
            f"\n\n### IMPORTANT — Fix These Issues From Previous Attempt\n\n"
            f"{issues_text}"
        )

    logger.info(
        "  Integration Editor: merging %d blocks for section '%s'",
        len(blocks),
        original_title,
    )
    logger.debug("  Integration Editor prompt (%d chars)", len(prompt))

    result = _invoke_with_retries(
        structured_llm,
        [
            {"role": "system", "content": INTEGRATION_EDITOR_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )
    logger.info(
        "  Integration Editor: merged section (%d chars)",
        len(result.integrated_content),
    )
    return result


def validate_integration(
    result: IntegrationResult,
    original_content: str,
    expected_ids: list[str],
) -> RevisionValidationResult:
    """
    Validate the IntegrationResult.

    Two checks only:
      1. CODE — ID coverage via the schema field covered_subcategory_ids (never misses)
      2. CODE — length sanity (integrated must not be shorter than original)
      3. LLM  — coherence and garbled text ONLY (not ID coverage — a 2B model
                 scanning a 6K char section for 6 IDs reliably produces false negatives)

    The ID coverage check is entirely code-based. This eliminates the false-negative
    loop seen when the LLM validator claimed GV.PO-01, ID.AM-1, ID.AM-2 were missing
    even though they were present in the text.

    Args:
        result: The IntegrationResult to validate.
        original_content: Original section content.
        expected_ids: Subcategory IDs that must appear.

    Returns:
        RevisionValidationResult.
    """
    code_issues: list[str] = []

    # Check 1: ID coverage — the Integration Editor self-reports which IDs it covered.
    # If it forgot to list an ID, feed that back as an issue for the next attempt.
    covered_set = set(result.covered_subcategory_ids)
    expected_set = set(expected_ids)
    missing = expected_set - covered_set
    if missing:
        code_issues.append(
            f"Integration result did not list these IDs as covered: "
            f"{', '.join(sorted(missing))}. Ensure each is explicitly addressed."
        )

    # Check 2: length sanity — integrated output must not be shorter than original.
    if len(result.integrated_content.strip()) < len(original_content) * 0.8:
        code_issues.append(
            "Integrated content is shorter than the original — "
            "original requirements may have been dropped."
        )

    if code_issues:
        logger.warning(
            "  Integration Validator: REJECTED by code — %d issues",
            len(code_issues),
        )
        for issue in code_issues:
            logger.warning("    - %s", issue)
        return RevisionValidationResult(is_acceptable=False, issues=code_issues)

    logger.info("  Integration Validator: code checks passed ✓")

    # Check 3: LLM coherence check ONLY — does the text read clearly?
    # ID coverage is fully handled by the code check above.
    # The LLM only needs to check "is this text garbled or contradictory?" —
    # for this question, reading the first 1500 chars is always sufficient.
    # Do NOT run summarize_lossless here: the summarizer on an 8K+ section
    # produces a 15-min validator death spiral trying to fit 40 key points
    # into a 2000-char output. Coherence is a LOCAL property — any 1500-char
    # window reveals garbled text.
    llm = create_llm()
    structured_llm = llm.with_structured_output(RevisionValidationResult)

    coherence_sample = result.integrated_content[:1500]

    prompt = (
        f"Policy section excerpt (first 1500 chars):\n\n"
        f"{coherence_sample}\n\n"
        f"Check ONLY: Is this text coherent and free of garbled, contradictory, "
        f"or nonsensical content? Do NOT check for specific subcategory IDs.\n"
        f"If the text reads clearly: is_acceptable=true, issues=[].\n"
        f"If garbled or contradictory content found: describe it in issues."
    )

    logger.info("  Integration Validator: LLM checking coherence only")

    try:
        llm_result = _invoke_with_retries(
            structured_llm,
            [
                {"role": "system", "content": INTEGRATION_VALIDATOR_SYSTEM},
                {"role": "user", "content": prompt},
            ],
        )
        if llm_result.is_acceptable:
            logger.info("  Integration Validator: ACCEPTED ✓")
        else:
            logger.warning(
                "  Integration Validator: REJECTED — %d issues",
                len(llm_result.issues),
            )
            for issue in llm_result.issues:
                logger.warning("    - %s", issue)
        return llm_result
    except Exception as exc:
        logger.warning(
            "  Integration Validator failed: %s — accepting integration",
            exc,
        )
        return RevisionValidationResult(is_acceptable=True, issues=[])


def run_integration_with_validation(
    original_content: str,
    original_title: str,
    blocks: list[AdditionBlock],
    expected_ids: list[str],
) -> IntegrationResult:
    """
    Run the Integration Editor with a validation loop.

    Attempts up to MAX_RETRIES. On failure, feeds the validator issues
    back to the Integration Editor as prior_issues.

    Args:
        original_content: The original section text.
        original_title: The section title.
        blocks: All AdditionBlocks for this section.
        expected_ids: Subcategory IDs that must be covered.

    Returns:
        A validated IntegrationResult.
    """
    logger.info("=" * 40)
    logger.info(
        "Integration Editor: section '%s', %d blocks", original_title, len(blocks)
    )
    logger.info("=" * 40)

    integration = run_integration_pass(
        original_content,
        original_title,
        blocks,
        expected_ids,
    )

    for attempt in range(1, MAX_RETRIES + 1):
        validation = validate_integration(integration, original_content, expected_ids)

        if validation.is_acceptable:
            logger.info(
                "  Integration accepted on attempt %d ✓",
                attempt,
            )
            return integration

        logger.warning(
            "  Integration rejected (attempt %d/%d) — regenerating",
            attempt,
            MAX_RETRIES,
        )

        integration = run_integration_pass(
            original_content,
            original_title,
            blocks,
            expected_ids,
            prior_issues=validation.issues,
        )

    logger.warning(
        "  Integration: max retries (%d) reached — assembling fallback from blocks",
        MAX_RETRIES,
    )
    # Fallback: assemble mechanically (never drops content)
    fallback_content = (
        original_content + "\n\n" + "\n\n".join(b.content for b in blocks)
    )
    return IntegrationResult(
        integrated_content=fallback_content,
        covered_subcategory_ids=[b.subcategory_id for b in blocks],
        changes_summary=f"Appended {len(blocks)} gap blocks (integration failed after {MAX_RETRIES} attempts).",
    )


# ---------------------------------------------------------------------------
# Role D — Section Creator (new_section gaps, unchanged logic)
# ---------------------------------------------------------------------------


def run_create_section(
    style_example: str,
    target: GapTarget,
    section_number: int,
    prior_issues: list[str] | None = None,
) -> SectionRevision:
    """
    Generate a brand-new policy section for a gap that has no existing home.

    Args:
        style_example: An existing section for style/formatting reference.
        target: The gap to address.
        section_number: The section number to assign.
        prior_issues: Validator feedback from a previous attempt.

    Returns:
        SectionRevision with complete new section content.
    """
    llm = create_llm()
    structured_llm = llm.with_structured_output(SectionRevision)

    prompt = (
        f"## Example Section (style reference)\n\n"
        f"{summarize_lossless(style_example, context_hint='policy section used as style/format reference for new section creation', threshold=4_000)}\n\n"
        f"---\n\n"
        f"## Gap to Address\n\n"
        f"Subcategory: {target.subcategory_id}\n"
        f"Status: {target.gap.status}\n"
        f"What is missing: {target.gap.gap}\n\n"
        f"## Full Recommendation\n\n"
        f"{target.gap.recommendation}\n\n"
        f"## NIST Implementation Guidance\n\n"
        f"{target.nist_guidance if target.nist_guidance else '(none available)'}\n\n"
        f"## Reference Framework Language\n\n"
        f"{target.framework_excerpt if target.framework_excerpt else '(none available)'}\n\n"
        f"---\n\n"
        f"Write a new policy section (Section {section_number}) addressing "
        f"subcategory {target.subcategory_id}. Set action='new_section'."
    )

    if prior_issues:
        issues_text = "\n".join(f"  - {issue}" for issue in prior_issues)
        prompt += (
            f"\n\n## IMPORTANT — Fix These Issues From Previous Attempt\n\n"
            f"{issues_text}"
        )

    logger.info(
        "  Section Creator: creating Section %d for %s",
        section_number,
        target.subcategory_id,
    )
    logger.debug("  Section Creator prompt (%d chars)", len(prompt))

    result = _invoke_with_retries(
        structured_llm,
        [
            {"role": "system", "content": SECTION_CREATOR_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )
    logger.info(
        "  Section Creator: created '%s' (%d chars)",
        result.section_title,
        len(result.revised_content),
    )
    return result


def validate_new_section(
    revision: SectionRevision,
    target: GapTarget,
) -> RevisionValidationResult:
    """
    Validate a new section using an LLM quality check.

    Code check: non-empty content and title.
    LLM check: gap coverage and coherence.

    Args:
        revision: The SectionRevision to validate.
        target: The GapTarget providing gap context.

    Returns:
        RevisionValidationResult.
    """
    code_issues: list[str] = []
    if len(revision.revised_content.strip()) < 50:
        code_issues.append("New section content is too short (< 50 chars).")
    if not revision.section_title.strip():
        code_issues.append("New section title is empty.")

    if code_issues:
        logger.warning(
            "  New Section Validator: REJECTED by code — %d issues",
            len(code_issues),
        )
        return RevisionValidationResult(is_acceptable=False, issues=code_issues)

    logger.info("  New Section Validator: code checks passed ✓")

    llm = create_llm()
    structured_llm = llm.with_structured_output(RevisionValidationResult)

    prompt = (
        f"Gap subcategory: {target.subcategory_id}\n"
        f"What is missing: {target.gap.gap}\n\n"
        f"Recommendation:\n{target.gap.recommendation}\n\n"
        f"New section content:\n"
        f"{summarize_lossless(revision.revised_content, context_hint=f'new policy section for {target.subcategory_id} being validated for gap coverage', threshold=4_000)}\n\n"
        f"Check: does the section address the gap? Is the text coherent?"
    )

    logger.info(
        "  New Section Validator: LLM checking %s",
        target.subcategory_id,
    )

    try:
        result = _invoke_with_retries(
            structured_llm,
            [
                {"role": "system", "content": REVISION_VALIDATOR_SYSTEM},
                {"role": "user", "content": prompt},
            ],
        )
        if result.is_acceptable:
            logger.info("  New Section Validator: ACCEPTED ✓")
        else:
            logger.warning(
                "  New Section Validator: REJECTED — %d issues",
                len(result.issues),
            )
        return result
    except Exception as exc:
        logger.warning(
            "  New Section Validator failed: %s — accepting section",
            exc,
        )
        return RevisionValidationResult(is_acceptable=True, issues=[])


def run_new_section_with_validation(
    target: GapTarget,
    style_example: str,
    section_number: int,
) -> SectionRevision:
    """
    Generate and validate a new section for a new_section gap.

    Args:
        target: The gap to address.
        style_example: Existing section for style reference.
        section_number: Section number to assign.

    Returns:
        A validated SectionRevision.
    """
    logger.info("=" * 40)
    logger.info("Section Creator: %s (new_section)", target.subcategory_id)
    logger.info("=" * 40)

    revision = run_create_section(style_example, target, section_number)

    for attempt in range(1, MAX_RETRIES + 1):
        validation = validate_new_section(revision, target)

        if validation.is_acceptable:
            logger.info(
                "  %s new section accepted on attempt %d ✓",
                target.subcategory_id,
                attempt,
            )
            return revision

        logger.warning(
            "  %s new section rejected (attempt %d/%d) — regenerating",
            target.subcategory_id,
            attempt,
            MAX_RETRIES,
        )

        revision = run_create_section(
            style_example,
            target,
            section_number,
            prior_issues=validation.issues,
        )

    logger.warning(
        "  %s: max retries (%d) reached — using last generated section",
        target.subcategory_id,
        MAX_RETRIES,
    )
    return revision

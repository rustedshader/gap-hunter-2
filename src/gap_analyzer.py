"""
NIST CSF Gap Analysis Orchestrator

Combines policy summaries from master_list.json and runs 6 NIST function agents
to perform comprehensive gap analysis.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Literal

from agents.nist_gap_agents import (
    run_nist_gap_agent,
    build_consolidated_report,
    classify_policy_functions,
    SubcategoryAssessment,
)
from agents.gap_analysis_tools import get_function_subcategories
from agents.function_summarizer_agent import (
    build_code_summary,
    FunctionGapSummary,
)

_CONTENT_CHAR_LIMIT = 12_000  # per section, avoid overloading context window

logger = logging.getLogger(__name__)

NIST_FUNCTIONS: list[
    Literal["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]
] = ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]


def load_master_list(master_list_path: Path) -> list[dict]:
    """Load the master list JSON file."""
    with open(master_list_path, "r") as f:
        return json.load(f)


def create_combined_policy_content(
    master_list: list[dict], sections_path: Path | None = None
) -> str:
    """
    Build a rich policy content string for gap analysis agents.

    Includes the full section text from sections_output.json when available,
    falling back to the summaries in master_list.json. This gives agents real
    policy language to quote as evidence rather than pre-digested summaries.

    Args:
        master_list: List of policy sections with summaries from master_list.json.
        sections_path: Optional path to sections_output.json for full content.

    Returns:
        Formatted string with full policy content ready for gap analysis.
    """
    # Try to load full section content
    full_content_map: dict[str, str] = {}
    if sections_path and sections_path.exists():
        try:
            with open(sections_path) as f:
                raw_sections = json.load(f)
            for sec in raw_sections:
                key = str(sec.get("number", ""))
                content = (sec.get("content") or "").strip()
                if content:
                    # Truncate very long sections to avoid context overflow
                    full_content_map[key] = content[:_CONTENT_CHAR_LIMIT]
        except Exception:
            logger.warning("Could not load sections_output.json; using summaries only")

    lines: list[str] = []
    lines.append("=" * 80)
    lines.append("POLICY DOCUMENT CONTENT")
    lines.append("=" * 80)
    lines.append("")

    for section in master_list:
        number = str(section.get("number", ""))
        title = section.get("title", "")
        summary = section.get("summary")

        # Skip pure header sections with no content
        if not summary and number not in full_content_map:
            continue

        lines.append(f"### Section {number}: {title}")
        lines.append("")

        # Prefer full content over summary
        if number in full_content_map:
            lines.append(full_content_map[number])
        elif summary and summary not in (None, "null"):
            lines.append("*[Summary]*")
            lines.append(summary)

        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    return "\n".join(lines)


def run_gap_analysis(
    master_list_path: Path,
    run_output_dir: Path,
    model_name: str = "gemma4:e2b",
    sections_path: Path | None = None,
) -> dict[str, str]:
    """
    Run comprehensive NIST CSF gap analysis using all 6 function agents.

    Args:
        master_list_path: Path to master_list.json
        run_output_dir: Timestamped output directory (already created by caller).
        model_name: LLM model to use
        sections_path: Optional path to sections_output.json for full section text.
                       Defaults to sections_output.json next to master_list.json.

    Returns:
        Dictionary of function name → report text.
    """
    logger.info("Starting NIST CSF gap analysis")

    # Default sections path: sibling of master_list.json
    if sections_path is None:
        sections_path = master_list_path.parent / "sections_output.json"

    # Load master list
    master_list = load_master_list(master_list_path)
    logger.info("Loaded %d sections from master list", len(master_list))

    # Build rich policy content (full text preferred over summaries)
    policy_content = create_combined_policy_content(master_list, sections_path)
    logger.info("Built policy content (%d chars)", len(policy_content))

    # Step 1: Classify which NIST functions are relevant to this policy
    logger.info("=" * 60)
    logger.info("Step 1: Classifying policy scope")
    logger.info("=" * 60)

    relevant_functions = classify_policy_functions(policy_content, model_name)

    skipped_functions = [f for f in NIST_FUNCTIONS if f not in relevant_functions]
    if skipped_functions:
        logger.info(
            "Skipping %d irrelevant functions: %s",
            len(skipped_functions),
            ", ".join(skipped_functions),
        )

    # Step 2: Run agents for relevant functions, skip the rest
    reports: dict[str, str] = {}
    all_assessments: dict[str, list[SubcategoryAssessment]] = {}
    all_summaries: dict[str, FunctionGapSummary] = {}

    for function in NIST_FUNCTIONS:
        logger.info("=" * 60)

        if function not in relevant_functions:
            # Mark all subcategories as Out of Scope — zero LLM calls
            logger.info("Skipping %s (out of scope for this policy)", function)
            subcategories = get_function_subcategories(function)
            out_assessments = []
            for sub in subcategories:
                policy_templates = ", ".join(sub.get("policies", [])) or "N/A"
                out_assessments.append(
                    SubcategoryAssessment(
                        subcategory_id=sub["id"],
                        title=sub.get("category", sub["id"]),
                        status="Out of Scope",
                        evidence="N/A — function not relevant to this policy type",
                        gap=f"Requires dedicated policy: {policy_templates}",
                        recommendation=policy_templates,
                    )
                )
            all_assessments[function] = out_assessments

            # Build a minimal report for this skipped function
            from agents.nist_gap_agents import _assemble_function_report

            report = _assemble_function_report(function, out_assessments)
            reports[function] = report

            report_path = run_output_dir / f"{function.lower()}_gap_analysis.md"
            report_path.write_text(report)

            all_summaries[function] = build_code_summary(function, out_assessments)
            continue

        logger.info("Analyzing NIST Function: %s", function)
        logger.info("=" * 60)

        try:
            report, assessments = run_nist_gap_agent(
                function_name=function,
                policy_content=policy_content,
                model_name=model_name,
            )

            reports[function] = report
            all_assessments[function] = assessments

            report_path = run_output_dir / f"{function.lower()}_gap_analysis.md"
            report_path.write_text(report)
            logger.info("Saved %s report to %s", function, report_path)

            all_summaries[function] = build_code_summary(function, assessments)
            logger.info("Built code summary for %s", function)

        except Exception as e:
            logger.exception("Failed to analyze %s function", function)
            reports[function] = f"Error: {str(e)}"
            all_assessments[function] = []

    # Create combined report
    combined_report = create_combined_report(reports)
    combined_path = run_output_dir / "combined_gap_analysis.md"
    combined_path.write_text(combined_report)
    logger.info("Saved combined report to %s", combined_path)

    # Build consolidated report from structured data (no LLM call)
    logger.info("=" * 60)
    logger.info("Building Consolidated Report")
    logger.info("=" * 60)

    consolidated_report = build_consolidated_report(all_assessments, all_summaries)
    consolidated_path = run_output_dir / "consolidated_gap_analysis.md"
    consolidated_path.write_text(consolidated_report)
    logger.info("Saved consolidated report to %s", consolidated_path)

    # Save structured assessments for Phase 3 (policy revision)
    assessments_data = {
        fn: [a.model_dump() for a in assessments]
        for fn, assessments in all_assessments.items()
    }
    assessments_path = run_output_dir / "assessments.json"
    with open(assessments_path, "w") as f:
        json.dump(assessments_data, f, indent=2)
    logger.info("Saved assessments to %s", assessments_path)

    logger.info("Gap analysis complete!")
    return reports


def create_combined_report(reports: dict[str, str]) -> str:
    """Create a combined report from all function analyses."""
    lines = []
    lines.append("# NIST Cybersecurity Framework Gap Analysis Report")
    lines.append("")
    lines.append(
        "This report provides a comprehensive gap analysis of the organization's policies"
    )
    lines.append("against the NIST Cybersecurity Framework 2.0.")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    for function in NIST_FUNCTIONS:
        lines.append(f"## {function} Function Analysis")
        lines.append("")
        lines.append(reports.get(function, "No analysis available"))
        lines.append("")
        lines.append("=" * 80)
        lines.append("")

    return "\n".join(lines)


def save_gap_analysis_summary(
    reports: dict[str, str], output_path: Path, consolidated: bool = True
) -> None:
    """Save a JSON summary of gap analysis results."""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "functions_analyzed": list(reports.keys()),
        "consolidated_report_generated": consolidated,
        "reports": {
            func: {
                "length": len(report),
                "preview": report[:200] + "..." if len(report) > 200 else report,
            }
            for func, report in reports.items()
        },
    }

    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info("Saved gap analysis summary to %s", output_path)


if __name__ == "__main__":
    # Use src/main.py as the CLI entry point instead.
    print("Use: python src/main.py <policy.pdf>")
    print("Run: python src/main.py --help for options")

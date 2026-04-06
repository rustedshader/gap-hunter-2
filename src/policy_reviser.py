"""
Policy Reviser — Phase 3 orchestrator.

Takes gap analysis outputs (assessments.json + sections_output.json) and
produces a revised policy document with all identified gaps addressed.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from agents.nist_gap_agents import SubcategoryAssessment
from agents.function_summary_schema import FunctionGapSummary
from agents.policy_revision_agent import (
    GapTarget,
    parse_gap_targets,
    run_revision_with_validation,
)
from agents.roadmap_agent import run_roadmap_with_validation, render_improvement_roadmap

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_assessments(path: Path) -> dict[str, list[SubcategoryAssessment]]:
    """Load structured assessments from JSON (saved by Phase 2)."""
    with open(path) as f:
        raw = json.load(f)
    return {
        fn: [SubcategoryAssessment(**a) for a in items]
        for fn, items in raw.items()
    }


def load_sections(path: Path) -> list[dict]:
    """Load original policy sections from JSON."""
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def load_summaries(run_dir: Path) -> dict[str, FunctionGapSummary]:
    """Load per-function summaries by reading the summary markdown files.

    Falls back to empty summaries if files don't exist.
    """
    from agents.function_summarizer_agent import FunctionGapSummary
    import json

    # Try loading from summary.json metadata
    summaries: dict[str, FunctionGapSummary] = {}
    for func in ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]:
        summary_path = run_dir / f"{func.lower()}_gap_summary.md"
        if not summary_path.exists():
            continue
        # Build a minimal summary from the gap analysis report stats
        report_path = run_dir / f"{func.lower()}_gap_analysis.md"
        if not report_path.exists():
            continue
        report = report_path.read_text()
        # Parse stats from report header
        import re
        total = int(m.group(1)) if (m := re.search(r"Total Subcategories\*\*:\s*(\d+)", report)) else 0
        in_scope = int(m.group(1)) if (m := re.search(r"In Scope\*\*:\s*(\d+)", report)) else 0
        addressed = int(m.group(1)) if (m := re.search(r"Addressed\*\*:\s*(\d+)", report)) else 0
        partial = int(m.group(1)) if (m := re.search(r"Partially Addressed\*\*:\s*(\d+)", report)) else 0
        not_addr = int(m.group(1)) if (m := re.search(r"Not Addressed\*\*:\s*(\d+)", report)) else 0
        oos = int(m.group(1)) if (m := re.search(r"Out of Scope\*\*:\s*(\d+)", report)) else 0

        # Read the summary markdown for critical gaps and recommendations
        summary_text = summary_path.read_text()
        critical_gaps = re.findall(r"^\d+\.\s+(.+)$", summary_text, re.MULTILINE)
        recommendations = []
        required_docs = re.findall(r"^- (.+)$", summary_text, re.MULTILINE)

        summaries[func] = FunctionGapSummary(
            function_name=func,
            executive_summary="",
            maturity_rating="",
            total_subcategories=total,
            in_scope_count=in_scope,
            addressed_count=addressed,
            partially_addressed_count=partial,
            not_addressed_count=not_addr,
            out_of_scope_count=oos,
            critical_gaps=critical_gaps[:5],
            key_recommendations=recommendations[:5],
            required_policy_documents=required_docs[:15],
        )

    return summaries


def run_policy_revision(
    sections_path: Path,
    assessments_path: Path,
    run_output_dir: Path,
    model_name: str = "gemma4:e2b",
) -> None:
    """
    Phase 3: Generate a revised policy addressing all identified gaps.

    Processes each gap in priority order (Not Addressed first), modifying
    existing sections or creating new ones. Produces revised_policy.md
    and revision_report.md.
    """
    logger.info("=" * 60)
    logger.info("Phase 3: Policy Revision")
    logger.info("=" * 60)

    # Load inputs
    sections = load_sections(sections_path)
    all_assessments = load_assessments(assessments_path)

    logger.info("Loaded %d policy sections", len(sections))
    logger.info("Loaded assessments for %d functions", len(all_assessments))

    # Parse gap targets (code-based: determine action + section for each gap)
    targets = parse_gap_targets(all_assessments, sections)

    if not targets:
        logger.info("No actionable gaps found — policy revision skipped.")
        (run_output_dir / "revised_policy.md").write_text(
            "# No Revisions Needed\n\nAll in-scope subcategories are addressed."
        )
        return

    # Build mutable section map
    section_map: dict[str, dict] = {s["number"]: dict(s) for s in sections}

    # Style example for new sections (use the longest existing section)
    style_example = max(
        (s["content"] for s in sections),
        key=len,
        default="",
    )

    # Track revisions for the report
    revision_reports: list[dict] = []

    # Process modifications first (operate on existing sections)
    modifications = [t for t in targets if t.action == "modify"]
    new_section_targets = [t for t in targets if t.action == "new_section"]

    for target in modifications:
        section = section_map.get(target.target_section_number)
        if not section:
            logger.warning(
                "  Target section %s not found for %s — switching to new_section",
                target.target_section_number, target.subcategory_id,
            )
            target.action = "new_section"
            new_section_targets.append(target)
            continue

        revision = run_revision_with_validation(
            target=target,
            current_section_content=section["content"],
            current_section_title=section["title"],
            style_example=style_example,
            section_number=int(section["number"]),
        )

        # Apply the modification
        section_map[target.target_section_number]["content"] = revision.revised_content
        if revision.section_title:
            section_map[target.target_section_number]["title"] = revision.section_title

        revision_reports.append({
            "subcategory_id": target.subcategory_id,
            "action": "modified",
            "target_section": f"Section {section['number']}: {section['title']}",
            "changes_summary": revision.changes_summary,
        })

        logger.info(
            "Applied modification to Section %s for %s",
            target.target_section_number, target.subcategory_id,
        )

    # Process new sections
    next_number = max((int(s["number"]) for s in sections), default=0) + 1
    new_sections: list[dict] = []

    for target in new_section_targets:
        revision = run_revision_with_validation(
            target=target,
            current_section_content=None,
            current_section_title=None,
            style_example=style_example,
            section_number=next_number,
        )

        new_section = {
            "number": str(next_number),
            "title": revision.section_title,
            "content": revision.revised_content,
            "is_new": True,
        }
        new_sections.append(new_section)

        revision_reports.append({
            "subcategory_id": target.subcategory_id,
            "action": "new_section",
            "target_section": f"Section {next_number}: {revision.section_title} (NEW)",
            "changes_summary": revision.changes_summary,
        })

        logger.info(
            "Created new Section %d: '%s' for %s",
            next_number, revision.section_title, target.subcategory_id,
        )
        next_number += 1

    # Assemble final outputs
    original_title = sections[0]["title"] if sections else "Policy Document"

    all_final_sections = list(section_map.values()) + new_sections
    revised_md = render_revised_policy(all_final_sections, original_title)
    report_md = render_revision_report(revision_reports, len(modifications), len(new_sections))

    # Save
    revised_path = run_output_dir / "revised_policy.md"
    revised_path.write_text(revised_md)
    logger.info("Saved revised policy to %s", revised_path)

    report_path = run_output_dir / "revision_report.md"
    report_path.write_text(report_md)
    logger.info("Saved revision report to %s", report_path)

    logger.info("Policy revision complete! %d gaps addressed.", len(revision_reports))

    # Generate improvement roadmap (multi-agent pipeline)
    logger.info("=" * 60)
    logger.info("Generating Improvement Roadmap")
    logger.info("=" * 60)

    all_summaries = load_summaries(run_output_dir)
    roadmap = run_roadmap_with_validation(all_assessments, all_summaries)
    roadmap_md = render_improvement_roadmap(roadmap)
    roadmap_path = run_output_dir / "improvement_roadmap.md"
    roadmap_path.write_text(roadmap_md)
    logger.info("Saved improvement roadmap to %s", roadmap_path)


# ---------------------------------------------------------------------------
# Markdown renderers
# ---------------------------------------------------------------------------

def render_revised_policy(sections: list[dict], original_title: str) -> str:
    """Render the complete revised policy as markdown."""
    lines: list[str] = []

    lines.append(f"# {original_title}")
    lines.append(f"*Revised per NIST CSF Gap Analysis — {datetime.now().strftime('%Y-%m-%d')}*\n")

    for section in sections:
        is_new = section.get("is_new", False)
        tag = " *(NEW — added per gap analysis)*" if is_new else ""
        lines.append(f"## {section['number']}. {section['title']}{tag}\n")
        lines.append(section["content"])
        lines.append("")
        lines.append("---\n")

    return "\n".join(lines)


def render_revision_report(
    reports: list[dict],
    modifications_count: int,
    new_sections_count: int,
) -> str:
    """Render the revision changelog as markdown."""
    lines: list[str] = []

    lines.append("# Policy Revision Report")
    lines.append(f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

    lines.append("## Summary\n")
    lines.append(f"- **Total gaps addressed**: {len(reports)}")
    lines.append(f"- **Sections modified**: {modifications_count}")
    lines.append(f"- **New sections added**: {new_sections_count}")
    lines.append("")

    lines.append("## Changes\n")
    lines.append("| # | NIST ID | Action | Section | Description |")
    lines.append("|---|---------|--------|---------|-------------|")
    for i, r in enumerate(reports, 1):
        lines.append(
            f"| {i} | {r['subcategory_id']} | {r['action']} | "
            f"{r['target_section']} | {r['changes_summary']} |"
        )
    lines.append("")

    lines.append("## Detailed Changes\n")
    for i, r in enumerate(reports, 1):
        lines.append(f"### {i}. {r['subcategory_id']}\n")
        lines.append(f"- **Action**: {r['action']}")
        lines.append(f"- **Section**: {r['target_section']}")
        lines.append(f"- **What changed**: {r['changes_summary']}")
        lines.append("")

    return "\n".join(lines)

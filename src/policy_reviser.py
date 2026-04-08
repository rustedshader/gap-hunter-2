"""
Policy Reviser — Phase 3 orchestrator.

RAPTOR + CoVe architecture:

  Phase A  Collect additions (per gap, per section):
    For each modification gap (grouped by target section):
      - Build prior_additions_summary from all ClusterSummaries produced so far
      - Run Addition Writer + CoVe validation loop → AdditionBlock
      - After all gaps in a NIST function cluster are done:
        Run Cluster Summarizer → ClusterSummary (RAPTOR level-1)
        This summary is fed to the next function's writers as compact context

  Phase B  Integrate (once per section):
    For each section that received additions:
      - Run Integration Editor with all its AdditionBlocks → IntegrationResult
      - CoVe-style Integration Validator confirms all IDs present + coherent

  Phase C  New sections:
    For gaps that target no existing section:
      - Run Section Creator + validation loop → SectionRevision (unchanged)

  Phase D  Roadmap generation (unchanged)
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from agents.nist_gap_agents import SubcategoryAssessment
from agents.function_summary_schema import FunctionGapSummary
from agents.policy_revision_agent import (
    GapTarget,
    parse_gap_targets,
    run_addition_with_validation,
    run_cluster_summarizer,
    build_prior_summary,
    run_integration_with_validation,
    run_new_section_with_validation,
)
from agents.roadmap_agent import run_roadmap_with_validation, render_improvement_roadmap
from events import emit_event

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_assessments(path: Path) -> dict[str, list[SubcategoryAssessment]]:
    """Load structured assessments from JSON (saved by Phase 2)."""
    with open(path) as f:
        raw = json.load(f)
    return {
        fn: [SubcategoryAssessment(**a) for a in items] for fn, items in raw.items()
    }


def load_sections(path: Path) -> list[dict]:
    """Load original policy sections from JSON."""
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Summary loader
# ---------------------------------------------------------------------------


def load_summaries(run_dir: Path) -> dict[str, FunctionGapSummary]:
    """
    Load per-function summaries from the gap analysis output directory.

    Builds minimal FunctionGapSummary objects from the report markdown files.
    Falls back gracefully if files don't exist.
    """
    from agents.function_summarizer_agent import FunctionGapSummary

    summaries: dict[str, FunctionGapSummary] = {}
    for func in ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]:
        summary_path = run_dir / f"{func.lower()}_gap_summary.md"
        report_path = run_dir / f"{func.lower()}_gap_analysis.md"
        if not summary_path.exists() or not report_path.exists():
            continue

        report = report_path.read_text()
        summary_text = summary_path.read_text()

        # Parse stats — these are structured numbers in the markdown header,
        # extracted with simple string search (not regex) via str.split
        def _extract_stat(text: str, label: str) -> int:
            """Extract 'N' from '**Label**: N' lines without regex."""
            marker = f"**{label}**:"
            idx = text.find(marker)
            if idx == -1:
                return 0
            after = text[idx + len(marker) :].strip()
            token = after.split()[0] if after.split() else "0"
            return int(token) if token.isdigit() else 0

        total = _extract_stat(report, "Total Subcategories")
        in_scope = _extract_stat(report, "In Scope")
        addressed = _extract_stat(report, "Addressed")
        partial = _extract_stat(report, "Partially Addressed")
        not_addr = _extract_stat(report, "Not Addressed")
        oos = _extract_stat(report, "Out of Scope")

        # Parse critical gaps and required docs from summary markdown
        # Lines starting with a digit+dot are critical gaps; lines starting with "- " are docs
        critical_gaps = [
            line.split(". ", 1)[1].strip()
            for line in summary_text.splitlines()
            if line.strip() and line.strip()[0].isdigit() and ". " in line
        ]
        required_docs = [
            line[2:].strip()
            for line in summary_text.splitlines()
            if line.startswith("- ")
        ]

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
            key_recommendations=[],
            required_policy_documents=required_docs[:15],
        )

    return summaries


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def run_policy_revision(
    sections_path: Path,
    assessments_path: Path,
    run_output_dir: Path,
    model_name: str = "gemma4:e2b",
) -> None:
    """
    Phase 3: Generate a revised policy addressing all identified gaps.

    Uses RAPTOR (cluster summaries → integration pass) and CoVe (4-step
    verification per block) to produce a cohesive, gap-free policy document.

    Produces revised_policy.md, revision_report.md, and improvement_roadmap.md.
    """
    logger.info("=" * 60)
    logger.info("Phase 3: Policy Revision (RAPTOR + CoVe)")
    emit_event(
        "revision_started",
        {"run_dir": str(run_output_dir), "model": model_name},
    )
    logger.info("=" * 60)

    sections = load_sections(sections_path)
    all_assessments = load_assessments(assessments_path)

    logger.info("Loaded %d policy sections", len(sections))
    logger.info("Loaded assessments for %d functions", len(all_assessments))

    # Parse gap targets — LLM-based section targeting (no regex)
    targets = parse_gap_targets(all_assessments, sections)

    if not targets:
        logger.info("No actionable gaps found — policy revision skipped.")
        (run_output_dir / "revised_policy.md").write_text(
            "# No Revisions Needed\n\nAll in-scope subcategories are addressed."
        )
        return

    # Build mutable section map
    section_map: dict[str, dict] = {s["number"]: dict(s) for s in sections}

    # Style example for new sections
    style_example = max(
        (s["content"] for s in sections),
        key=len,
        default="",
    )

    # Separate modification targets from new-section targets
    modifications = [t for t in targets if t.action == "modify"]
    new_section_targets = [t for t in targets if t.action == "new_section"]

    # -----------------------------------------------------------------------
    # Phase A: Collect AdditionBlocks, grouped by section then by function
    # -----------------------------------------------------------------------
    #
    # Structure:
    #   additions_per_section[section_num] = list[AdditionBlock]
    #   cluster_summaries = list[ClusterSummary] (grows as functions complete)
    #
    # For each NIST function, we process all its modification gaps in order,
    # then run the Cluster Summarizer. The resulting ClusterSummary is folded
    # into prior_additions_summary for all subsequent Addition Writers.

    # Group modifications by function (preserving priority order within each)
    mods_by_function: dict[str, list[GapTarget]] = defaultdict(list)
    for t in modifications:
        mods_by_function[t.function_name].append(t)

    # Ordered NIST function processing (Govern → Identify → Protect → …)
    function_order = ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]

    additions_per_section: dict[str, list] = defaultdict(list)
    cluster_summaries: list = []

    for function_name in function_order:
        func_targets = mods_by_function.get(function_name, [])
        if not func_targets:
            continue

        logger.info("=" * 60)
        logger.info("Phase A — %s function (%d gaps)", function_name, len(func_targets))
        logger.info("=" * 60)

        # Build the compact prior-additions summary from all completed clusters
        prior_summary = build_prior_summary(cluster_summaries)

        function_blocks: list = []  # all blocks written in this function cluster

        for target in func_targets:
            section = section_map.get(target.target_section_number)
            if not section:
                logger.warning(
                    "  Target section %s not found for %s — switching to new_section",
                    target.target_section_number,
                    target.subcategory_id,
                )
                target.action = "new_section"
                new_section_targets.append(target)
                continue

            block = run_addition_with_validation(
                target=target,
                original_section_content=section["content"],
                original_section_title=section["title"],
                prior_additions_summary=prior_summary,
            )

            additions_per_section[target.target_section_number].append(block)
            function_blocks.append(block)

        # RAPTOR: produce cluster summary for this function group
        if function_blocks:
            cs = run_cluster_summarizer(function_name, function_blocks)
            cluster_summaries.append(cs)
            logger.info(
                "  Cluster Summary for %s: covered %s",
                function_name,
                cs.covered_ids,
            )

    # -----------------------------------------------------------------------
    # Phase B: Integration pass — one per section
    # -----------------------------------------------------------------------

    revision_reports: list[dict] = []

    logger.info("=" * 60)
    logger.info("Phase B — Integration pass (%d sections)", len(additions_per_section))
    logger.info("=" * 60)

    for section_num, blocks in additions_per_section.items():
        section = section_map[section_num]
        expected_ids = [b.subcategory_id for b in blocks]

        integration = run_integration_with_validation(
            original_content=section["content"],
            original_title=section["title"],
            blocks=blocks,
            expected_ids=expected_ids,
        )

        section_map[section_num]["content"] = integration.integrated_content

        revision_reports.append(
            {
                "subcategory_id": ", ".join(expected_ids),
                "action": "modified",
                "target_section": f"Section {section_num}: {section['title']}",
                "changes_summary": integration.changes_summary,
            }
        )

        logger.info(
            "Applied integration to Section %s (%d gaps: %s)",
            section_num,
            len(blocks),
            ", ".join(expected_ids),
        )

    # -----------------------------------------------------------------------
    # Phase C: New sections
    # -----------------------------------------------------------------------

    logger.info("=" * 60)
    logger.info("Phase C — New sections (%d gaps)", len(new_section_targets))
    logger.info("=" * 60)

    next_number = max((int(s["number"]) for s in sections), default=0) + 1
    new_sections: list[dict] = []

    for target in new_section_targets:
        revision = run_new_section_with_validation(
            target=target,
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

        revision_reports.append(
            {
                "subcategory_id": target.subcategory_id,
                "action": "new_section",
                "target_section": f"Section {next_number}: {revision.section_title} (NEW)",
                "changes_summary": revision.changes_summary,
            }
        )

        logger.info(
            "Created new Section %d: '%s' for %s",
            next_number,
            revision.section_title,
            target.subcategory_id,
        )
        next_number += 1

    # -----------------------------------------------------------------------
    # Assemble and save outputs
    # -----------------------------------------------------------------------

    original_title = sections[0]["title"] if sections else "Policy Document"
    all_final_sections = list(section_map.values()) + new_sections

    revised_md = render_revised_policy(all_final_sections, original_title)
    report_md = render_revision_report(
        revision_reports,
        modifications_count=len(additions_per_section),
        new_sections_count=len(new_sections),
    )

    revised_path = run_output_dir / "revised_policy.md"
    revised_path.write_text(revised_md)
    logger.info("Saved revised policy to %s", revised_path)

    report_path = run_output_dir / "revision_report.md"
    report_path.write_text(report_md)
    logger.info("Saved revision report to %s", report_path)

    logger.info("Policy revision complete — %d gaps addressed.", len(revision_reports))
    emit_event(
        "revision_outputs_ready",
        {
            "run_dir": str(run_output_dir),
            "modified_sections": len(additions_per_section),
            "new_sections": len(new_sections),
            "gaps_addressed": len(revision_reports),
        },
    )

    # -----------------------------------------------------------------------
    # Phase D: Improvement roadmap
    # -----------------------------------------------------------------------

    logger.info("=" * 60)
    logger.info("Phase D — Improvement Roadmap")
    logger.info("=" * 60)

    all_summaries = load_summaries(run_output_dir)
    roadmap = run_roadmap_with_validation(all_assessments, all_summaries)
    roadmap_md = render_improvement_roadmap(roadmap)
    roadmap_path = run_output_dir / "improvement_roadmap.md"
    roadmap_path.write_text(roadmap_md)
    logger.info("Saved improvement roadmap to %s", roadmap_path)
    emit_event(
        "roadmap_ready",
        {"run_dir": str(run_output_dir), "tiers": len(roadmap.tiers)},
    )


# ---------------------------------------------------------------------------
# Markdown renderers
# ---------------------------------------------------------------------------


def render_revised_policy(sections: list[dict], original_title: str) -> str:
    """Render the complete revised policy as markdown."""
    lines: list[str] = []
    lines.append(f"# {original_title}")
    lines.append(
        f"*Revised per NIST CSF Gap Analysis — {datetime.now().strftime('%Y-%m-%d')}*\n"
    )

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

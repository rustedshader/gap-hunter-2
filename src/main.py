"""
Gap Hunter 2 — NIST CSF Policy Gap Analysis CLI

Usage:
    python src/main.py <policy.pdf>
    python src/main.py <policy.pdf> --model gemma4:e2b --output-dir reports
    python src/main.py <policy.pdf> --extract-only
    python src/main.py <policy.pdf> --skip-extraction --run-dir gap_analysis_reports/20260404_030622
"""

# Must be set before ANY import that touches HuggingFace hub or Docling.
# The hub performs a network HEAD request on every model load to check for
# updates. With models already cached this only wastes time (or hangs
# indefinitely without internet). All required Docling models are cached at
# ~/.cache/huggingface/hub/ so offline mode is safe.
import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

from extractor import (
    extract_all_sections,
    save_sections_json,
    generate_master_list,
    save_master_list,
)
from gap_analyzer import run_gap_analysis, save_gap_analysis_summary, NIST_FUNCTIONS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)-40s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def _setup_debug_file_log(run_dir: Path) -> None:
    """Add a DEBUG-level file handler writing to run_dir/debug.log."""
    debug_path = run_dir / "debug.log"
    fh = logging.FileHandler(debug_path, mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter(
            "%(asctime)s  %(levelname)-8s  %(name)-40s  %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logging.getLogger().addHandler(fh)
    logging.getLogger().setLevel(logging.DEBUG)
    log.info("Debug log → %s", debug_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gap-hunter",
        description="Analyze a policy PDF against the CIS MS-ISAC NIST CSF Policy Template Guide (2024).",
    )
    parser.add_argument(
        "pdf",
        type=Path,
        nargs="?",
        default=None,
        help="Path to the policy PDF to analyze (not required with --revision-only)",
    )
    parser.add_argument(
        "--model",
        default="gemma4:e2b",
        help="Ollama model name (default: gemma4:e2b)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("gap_analysis_reports"),
        help="Base directory for reports (default: gap_analysis_reports)",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=None,
        help="Reuse an existing run directory (for --skip-extraction)",
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=80,
        help="Lines per extraction chunk (default: 80)",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=20,
        help="Overlap lines between chunks (default: 20)",
    )
    parser.add_argument(
        "--extract-only",
        action="store_true",
        help="Only extract sections, skip gap analysis",
    )
    parser.add_argument(
        "--skip-revision",
        action="store_true",
        help="Skip policy revision (Phase 3) after gap analysis",
    )
    parser.add_argument(
        "--skip-extraction",
        action="store_true",
        help="Skip extraction, reuse existing run directory (requires --run-dir)",
    )
    parser.add_argument(
        "--revision-only",
        action="store_true",
        help=(
            "Skip extraction and gap analysis — run Phase 3 (policy revision + roadmap) "
            "only. Requires --run-dir pointing to a completed Phase 2 run directory "
            "that contains assessments.json and sections_output.json."
        ),
    )
    return parser.parse_args()


def create_run_dir(output_dir: Path) -> Path:
    """Create a timestamped run directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / timestamp
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def run_extraction(args: argparse.Namespace, run_dir: Path) -> None:
    """Phase 1: Extract sections from PDF and generate master list."""
    log.info("Phase 1: Extracting sections from %s", args.pdf)

    if not args.pdf.exists():
        print(f"Error: PDF not found: {args.pdf}")
        sys.exit(1)

    sections_path = run_dir / "sections_output.json"
    master_list_path = run_dir / "master_list.json"

    sections = extract_all_sections(
        pdf_path=args.pdf,
        model_name=args.model,
        window_size=args.window_size,
        overlap=args.overlap,
    )

    save_sections_json(sections, sections_path)
    log.info("Extracted %d sections → %s", len(sections), sections_path)

    log.info("Generating master list with summaries...")
    master_list = generate_master_list(sections, model_name=args.model)
    save_master_list(master_list, master_list_path)
    log.info("Master list → %s", master_list_path)

    print(f"\n{'─' * 60}")
    print(f"  Extracted {len(sections)} sections from {args.pdf.name}")
    print(f"  Output directory: {run_dir}")
    print(f"  Sections: {sections_path.name}")
    print(f"  Master List: {master_list_path.name}")
    print(f"{'─' * 60}\n")

    for s in sections:
        status = "✓" if s.is_complete else "… (continues)"
        print(
            f"  [{s.number}] {s.title}  (lines {s.start_line}–{s.end_line})  {status}"
        )
    print()


def run_analysis(args: argparse.Namespace, run_dir: Path) -> None:
    """Phase 2: Run NIST CSF gap analysis on extracted sections."""
    log.info("Phase 2: Running NIST CSF gap analysis")

    master_list_path = run_dir / "master_list.json"
    sections_path = run_dir / "sections_output.json"

    if not master_list_path.exists():
        print(f"Error: Master list not found: {master_list_path}")
        print("Run extraction first (without --skip-extraction)")
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print("  NIST Cybersecurity Framework Gap Analysis")
    print(f"{'=' * 60}")
    print(f"\n  Policy: {args.pdf.name}")
    print(f"  Model: {args.model}")
    print(f"  Run directory: {run_dir}")
    print(f"  Analyzing against all 6 NIST CSF functions:")
    for i, func in enumerate(NIST_FUNCTIONS, 1):
        print(f"    {i}. {func}")
    print()

    reports = run_gap_analysis(
        master_list_path=master_list_path,
        run_output_dir=run_dir,
        model_name=args.model,
        sections_path=sections_path,
    )

    save_gap_analysis_summary(reports, run_dir / "summary.json")

    print(f"\n{'=' * 60}")
    print("  Gap Analysis Complete!")
    print(f"{'=' * 60}")
    print(f"\n  All outputs in: {run_dir}/")
    print("\n  Files:")
    print(f"    - sections_output.json")
    print(f"    - master_list.json")
    for function in NIST_FUNCTIONS:
        print(f"    - {function.lower()}_gap_analysis.md")
        print(f"    - {function.lower()}_gap_summary.md   ← Executive summary")
    print(f"    - combined_gap_analysis.md")
    print(f"    - consolidated_gap_analysis.md")
    print(f"    - master_gap_summary.md         ← Master executive summary")
    print(f"    - summary.json")
    print(f"    - debug.log                     ← Full debug trace")
    print()


def run_revision(args: argparse.Namespace, run_dir: Path) -> None:
    """Phase 3: Generate revised policy from gap analysis results."""
    from policy_reviser import run_policy_revision

    log.info("Phase 3: Generating revised policy")

    sections_path = run_dir / "sections_output.json"
    assessments_path = run_dir / "assessments.json"

    if not assessments_path.exists():
        print(f"Error: Assessments not found: {assessments_path}")
        print("Run gap analysis first (Phase 2 generates assessments.json)")
        sys.exit(1)

    run_policy_revision(
        sections_path=sections_path,
        assessments_path=assessments_path,
        run_output_dir=run_dir,
        model_name=args.model,
    )

    print(f"\n{'=' * 60}")
    print("  Policy Revision Complete!")
    print(f"{'=' * 60}")
    print(f"\n  All outputs in: {run_dir}/")
    print("\n  Files:")
    print(f"    - sections_output.json")
    print(f"    - master_list.json")
    for function in NIST_FUNCTIONS:
        print(f"    - {function.lower()}_gap_analysis.md")
        print(f"    - {function.lower()}_gap_summary.md   ← Executive summary")
    print(f"    - combined_gap_analysis.md")
    print(f"    - consolidated_gap_analysis.md")
    print(f"    - master_gap_summary.md         ← Master executive summary")
    print(f"    - revised_policy.md             ← Revised policy document")
    print(f"    - revision_report.md            ← Revision changelog")
    print(f"    - improvement_roadmap.md        ← Improvement roadmap")
    print(f"    - summary.json")
    print(f"    - debug.log                     ← Full debug trace")
    print()


def main() -> None:
    args = parse_args()

    # --revision-only: skip straight to Phase 3 using an existing run directory
    if args.revision_only:
        if not args.run_dir:
            print("Error: --revision-only requires --run-dir <path>")
            sys.exit(1)
        run_dir = args.run_dir
        if not run_dir.exists():
            print(f"Error: Run directory not found: {run_dir}")
            sys.exit(1)
        _setup_debug_file_log(run_dir)
        run_revision(args, run_dir)
        return

    if args.pdf is None:
        print("Error: pdf argument is required unless using --revision-only")
        sys.exit(1)

    if args.skip_extraction:
        if not args.run_dir:
            print("Error: --skip-extraction requires --run-dir <path>")
            sys.exit(1)
        run_dir = args.run_dir
    else:
        run_dir = args.run_dir or create_run_dir(args.output_dir)

    _setup_debug_file_log(run_dir)

    if not args.skip_extraction:
        run_extraction(args, run_dir)

    if not args.extract_only:
        run_analysis(args, run_dir)

    if not args.extract_only and not args.skip_revision:
        run_revision(args, run_dir)


if __name__ == "__main__":
    main()

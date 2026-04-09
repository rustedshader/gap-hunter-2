"""
Benchmark script for Gap Hunter 2.

Runs the full gap-analysis pipeline on each dummy policy in tests/dummy_policies/,
compares LLM output against the ground truth in tests/expected_gaps.json, and
writes a results matrix to tests/benchmark_results/.

Usage:
    # From repo root:
    cd /path/to/gap-hunter-2
    python tests/benchmark.py
    python tests/benchmark.py --model gemma4:e2b --policies-dir tests/dummy_policies
    python tests/benchmark.py --policy 01_isms_strong.md   # single policy
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Offline mode (same as main.py) ──────────────────────────────────────────
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# ── Make src/ importable ─────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from extractor import detect_rule_based_sections, generate_master_list, save_sections_json, save_master_list
from gap_analyzer import run_gap_analysis, NIST_FUNCTIONS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)-30s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("benchmark")


def _setup_file_log(run_dir: Path) -> None:
    """Mirror main.py: write a DEBUG-level debug.log inside the run directory."""
    debug_path = run_dir / "debug.log"
    fh = logging.FileHandler(debug_path, mode="w", encoding="utf-8")
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

TESTS_DIR = Path(__file__).parent
POLICIES_DIR = TESTS_DIR / "dummy_policies"
EXPECTED_GAPS_PATH = TESTS_DIR / "expected_gaps.json"
RESULTS_DIR = TESTS_DIR / "benchmark_results"

# All subcategory IDs in NIST CSF 2.0 (from nist_config.yaml)
ALL_SUBCATEGORIES: list[str] = [
    # Govern
    "GV.OC-01","GV.OC-02","GV.OC-03","GV.OC-04","GV.OC-05",
    "GV.RM-01","GV.RM-02","GV.RM-03","GV.RM-04","GV.RM-05","GV.RM-06","GV.RM-07",
    "GV.RR-01","GV.RR-02","GV.RR-03","GV.RR-04",
    "GV.PO-01","GV.PO-02",
    "GV.OV-01","GV.OV-02","GV.OV-03",
    "GV.SC-01","GV.SC-02","GV.SC-03","GV.SC-04","GV.SC-05",
    "GV.SC-06","GV.SC-07","GV.SC-08","GV.SC-09","GV.SC-10",
    # Identify
    "ID.AM-1","ID.AM-2","ID.AM-3","ID.AM-4","ID.AM-5","ID.AM-7","ID.AM-8",
    "ID.RA-01","ID.RA-02","ID.RA-03","ID.RA-04","ID.RA-05",
    "ID.RA-06","ID.RA-07","ID.RA-08","ID.RA-09","ID.RA-10",
    "ID.IM-01","ID.IM-02","ID.IM-03","ID.IM-04",
    # Protect
    "PR.AA-01","PR.AA-02","PR.AA-03","PR.AA-04","PR.AA-05","PR.AA-06",
    "PR.AT-01","PR.AT-02",
    "PR.DS-01","PR.DS-02","PR.DS-10","PR.DS-11",
    "PR.PS-01","PR.PS-02","PR.PS-03","PR.PS-04","PR.PS-05","PR.PS-06",
    "PR.IR-01","PR.IR-02","PR.IR-03","PR.IR-04",
    # Detect
    "DE.AE-02","DE.AE-03","DE.AE-04","DE.AE-06","DE.AE-07","DE.AE-08",
    "DE.CM-01","DE.CM-02","DE.CM-03","DE.CM-06","DE.CM-09",
    # Respond
    "RS.MA-01","RS.MA-02","RS.MA-03","RS.MA-04","RS.MA-05",
    "RS.CO-02","RS.CO-03",
    "RS.AN-03","RS.AN-06","RS.AN-07","RS.AN-08",
    "RS.MI-01","RS.MI-02",
    # Recover
    "RC.RP-01","RC.RP-02","RC.RP-03","RC.RP-04","RC.RP-05","RC.RP-06",
    "RC.CO-03","RC.CO-04",
]


# ── Markdown → doc_lines (bypasses pdf_to_markdown) ─────────────────────────

def markdown_to_doc_lines(md_path: Path) -> list[tuple[int, str]]:
    """Read a markdown file and return (line_number, text) tuples."""
    text = md_path.read_text(encoding="utf-8")
    return [(i + 1, line) for i, line in enumerate(text.splitlines())]


# ── Extract subcategory assessments from gap analysis output ─────────────────

def _nist_status_to_benchmark(status: str) -> str:
    """
    Map assessments.json NIST vocabulary → benchmark vocabulary.

    assessments.json uses:  "Addressed" | "Partially Addressed" |
                            "Not Addressed" | "Out of Scope"
    expected_gaps.json uses: "COVERED" | "PARTIAL" | "GAP"
    """
    s = status.strip().lower()
    if s == "addressed":
        return "COVERED"
    if s == "partially addressed":
        return "PARTIAL"
    # "not addressed" and "out of scope" both map to GAP
    return "GAP"


def parse_assessments(run_dir: Path) -> dict[str, str]:
    """
    Read assessments.json produced by run_gap_analysis and return a flat
    {subcategory_id: status} dict. Status values: COVERED / PARTIAL / GAP.
    """
    assessments_path = run_dir / "assessments.json"
    if not assessments_path.exists():
        log.warning("assessments.json not found in %s", run_dir)
        return {}

    with open(assessments_path) as f:
        data = json.load(f)

    flat: dict[str, str] = {}
    # assessments.json structure: list of {function, subcategories: [{id, status, ...}]}
    # OR dict keyed by function — handle both shapes.
    if isinstance(data, list):
        for entry in data:
            for sub in entry.get("subcategories", []):
                sid = sub.get("id") or sub.get("subcategory_id", "")
                raw = sub.get("status") or sub.get("assessment", "GAP")
                if sid:
                    flat[sid] = _nist_status_to_benchmark(raw)
    elif isinstance(data, dict):
        for _fn, subcats in data.items():
            if isinstance(subcats, list):
                for sub in subcats:
                    sid = sub.get("id") or sub.get("subcategory_id", "")
                    raw = sub.get("status") or sub.get("assessment", "GAP")
                    if sid:
                        flat[sid] = _nist_status_to_benchmark(raw)
    return flat


# ── Score comparison ─────────────────────────────────────────────────────────

def score(predicted: str, expected: str) -> str:
    """
    Returns:
      TP  — predicted COVERED/PARTIAL, expected COVERED/PARTIAL
      TN  — predicted GAP, expected GAP
      FP  — predicted COVERED/PARTIAL, expected GAP   (false alarm)
      FN  — predicted GAP, expected COVERED/PARTIAL   (missed gap)
    """
    pred_positive = predicted in ("COVERED", "PARTIAL")
    exp_positive  = expected  in ("COVERED", "PARTIAL")

    if pred_positive and exp_positive:
        return "TP"
    if not pred_positive and not exp_positive:
        return "TN"
    if pred_positive and not exp_positive:
        return "FP"
    return "FN"


def compute_metrics(results: list[dict]) -> dict:
    """Precision, recall, F1, accuracy from per-subcategory result rows."""
    tp = sum(1 for r in results if r["score"] == "TP")
    tn = sum(1 for r in results if r["score"] == "TN")
    fp = sum(1 for r in results if r["score"] == "FP")
    fn = sum(1 for r in results if r["score"] == "FN")

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1        = (2 * precision * recall / (precision + recall)
                 if (precision + recall) > 0 else 0.0)
    accuracy  = (tp + tn) / len(results) if results else 0.0

    return {
        "TP": tp, "TN": tn, "FP": fp, "FN": fn,
        "precision": round(precision, 3),
        "recall":    round(recall, 3),
        "f1":        round(f1, 3),
        "accuracy":  round(accuracy, 3),
    }


# ── Per-policy pipeline ──────────────────────────────────────────────────────

def run_policy_benchmark(
    policy_path: Path,
    expected: dict[str, str],
    run_dir: Path,
    model_name: str,
) -> dict:
    """
    Full pipeline for one policy file. Returns a result dict with metrics and
    per-subcategory details.
    """
    log.info("── %s ──────────────────────────────────", policy_path.name)

    # Per-policy debug.log (mirrors main.py behaviour)
    policy_log_path = run_dir / "debug.log"
    fh = logging.FileHandler(policy_log_path, mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)-40s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logging.getLogger().addHandler(fh)
    log.info("Per-policy debug log → %s", policy_log_path)

    try:
        return _run_policy_benchmark_inner(policy_path, expected, run_dir, model_name)
    finally:
        # Remove the per-policy handler so it doesn't bleed into the next policy
        logging.getLogger().removeHandler(fh)
        fh.close()


def _run_policy_benchmark_inner(
    policy_path: Path,
    expected: dict[str, str],
    run_dir: Path,
    model_name: str,
) -> dict:
    # Phase 1: section extraction (markdown-aware, no PDF conversion)
    doc_lines = markdown_to_doc_lines(policy_path)
    sections = detect_rule_based_sections(doc_lines)
    if not sections:
        log.warning("Rule-based detection found 0 sections; LLM fallback would be needed for real PDFs")

    sections_path = run_dir / "sections_output.json"
    save_sections_json(sections, sections_path)

    # Phase 2: master list (LLM summarisation)
    log.info("Generating master list (%d sections)…", len(sections))
    master_list = generate_master_list(sections, model_name=model_name)
    master_list_path = run_dir / "master_list.json"
    save_master_list(master_list, master_list_path)

    # Phase 3: gap analysis
    log.info("Running gap analysis…")
    run_gap_analysis(
        master_list_path=master_list_path,
        run_output_dir=run_dir,
        model_name=model_name,
        sections_path=sections_path,
    )

    # Parse results
    predicted = parse_assessments(run_dir)

    # Build per-subcategory comparison
    rows: list[dict] = []
    for sub_id in ALL_SUBCATEGORIES:
        pred = predicted.get(sub_id, "GAP")   # default GAP if not mentioned
        exp  = expected.get(sub_id, "GAP")
        rows.append({
            "subcategory":  sub_id,
            "function":     sub_id.split(".")[0],
            "expected":     exp,
            "predicted":    pred,
            "score":        score(pred, exp),
        })

    metrics = compute_metrics(rows)
    log.info(
        "  Precision=%.3f  Recall=%.3f  F1=%.3f  Accuracy=%.3f",
        metrics["precision"], metrics["recall"], metrics["f1"], metrics["accuracy"],
    )

    return {
        "policy":   policy_path.name,
        "run_dir":  str(run_dir),
        "metrics":  metrics,
        "details":  rows,
    }


# ── Matrix output ────────────────────────────────────────────────────────────

def write_csv_matrix(all_results: list[dict], out_dir: Path) -> None:
    """Write two CSVs: summary matrix and full per-subcategory detail."""

    # 1. Summary matrix (one row per policy)
    summary_path = out_dir / "benchmark_summary.csv"
    with open(summary_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Policy", "Precision", "Recall", "F1", "Accuracy", "TP", "TN", "FP", "FN"])
        for r in all_results:
            m = r["metrics"]
            writer.writerow([
                r["policy"],
                m["precision"], m["recall"], m["f1"], m["accuracy"],
                m["TP"], m["TN"], m["FP"], m["FN"],
            ])
    log.info("Summary CSV → %s", summary_path)

    # 2. Full detail (one row per policy × subcategory)
    detail_path = out_dir / "benchmark_detail.csv"
    with open(detail_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Policy", "NIST_Function", "Subcategory", "Expected", "Predicted", "Score"])
        for r in all_results:
            for row in r["details"]:
                writer.writerow([
                    r["policy"],
                    row["function"],
                    row["subcategory"],
                    row["expected"],
                    row["predicted"],
                    row["score"],
                ])
    log.info("Detail CSV  → %s", detail_path)


def write_function_heatmap(all_results: list[dict], out_dir: Path) -> None:
    """
    Write a per-NIST-function accuracy heatmap CSV.
    Rows = policies, Columns = NIST functions (Govern, Identify, …).
    Cell value = F1 score for that function in that policy.
    """
    functions = ["GV", "ID", "PR", "DE", "RS", "RC"]
    func_labels = {
        "GV": "Govern", "ID": "Identify", "PR": "Protect",
        "DE": "Detect",  "RS": "Respond",  "RC": "Recover",
    }

    heatmap_path = out_dir / "benchmark_heatmap.csv"
    with open(heatmap_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Policy"] + [func_labels[fn] for fn in functions])
        for r in all_results:
            row_vals = [r["policy"]]
            for fn in functions:
                fn_rows = [d for d in r["details"] if d["function"] == fn]
                fn_metrics = compute_metrics(fn_rows)
                row_vals.append(fn_metrics["f1"])
            writer.writerow(row_vals)
    log.info("Heatmap CSV → %s", heatmap_path)


def write_json_report(all_results: list[dict], out_dir: Path) -> None:
    """Write complete results as JSON for programmatic access."""
    report_path = out_dir / "benchmark_report.json"
    report_path.write_text(json.dumps(all_results, indent=2))
    log.info("JSON report → %s", report_path)


def print_summary_table(all_results: list[dict]) -> None:
    header = f"{'Policy':<45} {'Precision':>9} {'Recall':>7} {'F1':>6} {'Accuracy':>9}"
    print(f"\n{'=' * len(header)}")
    print("  BENCHMARK RESULTS SUMMARY")
    print(f"{'=' * len(header)}")
    print(header)
    print("-" * len(header))
    for r in all_results:
        m = r["metrics"]
        print(
            f"  {r['policy']:<43} {m['precision']:>9.3f} {m['recall']:>7.3f}"
            f" {m['f1']:>6.3f} {m['accuracy']:>9.3f}"
        )
    print(f"{'=' * len(header)}\n")


# ── CLI ──────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="benchmark",
        description="Benchmark Gap Hunter 2 against dummy policies with known NIST gap ground truth.",
    )
    p.add_argument("--policies-dir", type=Path, default=POLICIES_DIR)
    p.add_argument("--expected",     type=Path, default=EXPECTED_GAPS_PATH)
    p.add_argument("--results-dir",  type=Path, default=RESULTS_DIR)
    p.add_argument("--model",        default="gemma4:e2b")
    p.add_argument(
        "--policy",
        default=None,
        help="Run benchmark for a single policy file (filename only, e.g. 01_isms_strong.md)",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()

    # Load ground truth
    if not args.expected.exists():
        print(f"Error: expected_gaps.json not found at {args.expected}")
        sys.exit(1)
    with open(args.expected) as f:
        ground_truth_raw = json.load(f)

    # Build lookup: filename → expected subcategory map
    ground_truth: dict[str, dict[str, str]] = {
        entry["file"]: entry["subcategories"]
        for entry in ground_truth_raw["policies"]
    }

    # Discover policy files
    if args.policy:
        policy_files = [args.policies_dir / args.policy]
    else:
        policy_files = sorted(args.policies_dir.glob("*.md"))

    if not policy_files:
        print(f"No policy files found in {args.policies_dir}")
        sys.exit(1)

    # Create timestamped results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_root = args.results_dir / timestamp
    run_root.mkdir(parents=True, exist_ok=True)

    # Set up file logging for the entire benchmark run
    _setup_file_log(run_root)
    log.info("Results directory: %s", run_root)

    all_results: list[dict] = []

    for policy_path in policy_files:
        if policy_path.name not in ground_truth:
            log.warning("No ground truth for %s — skipping", policy_path.name)
            continue

        expected = ground_truth[policy_path.name]
        policy_run_dir = run_root / policy_path.stem
        policy_run_dir.mkdir(parents=True, exist_ok=True)

        try:
            result = run_policy_benchmark(
                policy_path=policy_path,
                expected=expected,
                run_dir=policy_run_dir,
                model_name=args.model,
            )
            all_results.append(result)
        except Exception:
            log.exception("Failed to benchmark %s", policy_path.name)

    if not all_results:
        print("No results generated.")
        sys.exit(1)

    # Write outputs
    write_csv_matrix(all_results, run_root)
    write_function_heatmap(all_results, run_root)
    write_json_report(all_results, run_root)
    print_summary_table(all_results)

    print(f"All outputs written to: {run_root}/")
    print("  benchmark_summary.csv  — per-policy precision/recall/F1/accuracy")
    print("  benchmark_detail.csv   — per-subcategory expected vs predicted")
    print("  benchmark_heatmap.csv  — F1 per NIST function per policy")
    print("  benchmark_report.json  — full machine-readable results")


if __name__ == "__main__":
    main()

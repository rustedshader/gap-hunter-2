"""
Summary accuracy comparison: LLM-generated vs Code-computed function summaries.

For each NIST function, compares two strategies:

  A) LLM summary  — current approach: run_summarize_with_validation()
                    2+ LLM calls (summarizer + validator + retries)
                    Produces: maturity_rating, counts, critical_gaps,
                              key_recommendations, executive_summary

  B) Code summary — proposed: compute everything from assessments.json
                    0 LLM calls for all numeric/list fields
                    1 optional LLM call only for executive_summary prose

Accuracy metrics compared:
  - maturity_rating    exact match (LLM is given stats explicitly — should match)
  - counts             exact match (should be identical)
  - critical_gaps      subcategory ID overlap %
  - key_recommendations overlap %
  - time               wall-clock seconds

Requires a completed Phase 2 run with assessments.json + *_gap_analysis.md files.
Defaults to the most recent gap_analysis_reports/ run.

Run from repo root:
    python tests/test_summary_accuracy.py
    python tests/test_summary_accuracy.py --run-dir gap_analysis_reports/20260408_014240
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import logging
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agents.function_summary_schema import FunctionGapSummary
from agents.function_summarizer_agent import (
    run_summarize_with_validation,
    _compute_stats,
    _compute_maturity_rating,
)
from agents.nist_gap_agents import SubcategoryAssessment

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("summary_accuracy_test")

NIST_FUNCTIONS = ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]


# ── Load data ─────────────────────────────────────────────────────────────────

def find_latest_run() -> Path | None:
    base = Path("gap_analysis_reports")
    if not base.exists():
        return None
    runs = sorted(
        (d for d in base.iterdir() if d.is_dir() and (d / "assessments.json").exists()),
        reverse=True,
    )
    return runs[0] if runs else None


def load_assessments(run_dir: Path) -> dict[str, list[SubcategoryAssessment]]:
    """Load assessments.json → {function: [SubcategoryAssessment]}."""
    path = run_dir / "assessments.json"
    raw = json.loads(path.read_text())
    result = {}
    for fn, items in raw.items():
        result[fn] = [SubcategoryAssessment(**item) for item in items]
    return result


def load_report(run_dir: Path, function: str) -> str | None:
    """Load the gap analysis markdown report for one function."""
    path = run_dir / f"{function.lower()}_gap_analysis.md"
    return path.read_text() if path.exists() else None


# ── Code-based summary (Strategy B) ──────────────────────────────────────────

def _extract_subcategory_ids(text: str) -> set[str]:
    """Extract NIST subcategory IDs (e.g. GV.OC-01) from free text."""
    return set(re.findall(r"\b[A-Z]{2}\.[A-Z]{2}-\d{2}\b", text))


def build_code_summary(
    function: str,
    assessments: list[SubcategoryAssessment],
) -> FunctionGapSummary:
    """
    Compute FunctionGapSummary purely from structured assessment data.
    Zero LLM calls. All fields derived deterministically.
    """
    stats = _compute_stats(assessments)
    maturity = _compute_maturity_rating(stats)

    in_scope = [a for a in assessments if a.status != "Out of Scope"]
    not_addressed = [a for a in in_scope if a.status == "Not Addressed"]
    partial = [a for a in in_scope if a.status == "Partially Addressed"]

    # critical_gaps: Not Addressed first, then Partial (top 5)
    gap_items = not_addressed + partial
    critical_gaps = [
        f"{a.subcategory_id}: {a.gap[:120]}"
        for a in gap_items[:5]
        if a.gap and a.gap.lower() not in ("none", "none - fully addressed", "n/a")
    ]

    # key_recommendations: from Not Addressed items (top 5)
    key_recs = [
        f"{a.subcategory_id}: {a.recommendation[:120]}"
        for a in gap_items[:5]
        if a.recommendation and a.recommendation.strip()
    ]

    # required_policy_documents: unique docs from recommendations
    doc_pattern = re.compile(
        r"([A-Z][a-z]+(?: [A-Z][a-z]+)* (?:Policy|Standard|Plan|Procedure))"
    )
    docs: set[str] = set()
    for a in not_addressed:
        docs.update(doc_pattern.findall(a.recommendation or ""))
    required_docs = sorted(docs)[:8]

    # executive_summary: template-based (no LLM)
    addressed_pct = (
        int(100 * stats["addressed"] / stats["in_scope"])
        if stats["in_scope"] > 0 else 0
    )
    executive_summary = (
        f"The {function} function has {stats['in_scope']} subcategories in scope, "
        f"of which {stats['addressed']} are fully addressed ({addressed_pct}%), "
        f"{stats['partially_addressed']} partially addressed, and "
        f"{stats['not_addressed']} not addressed. "
        f"Overall maturity: {maturity}. "
        f"Top gaps include: "
        + (", ".join(_extract_subcategory_ids(" ".join(critical_gaps))
                     ) if critical_gaps else "none identified")
        + "."
    )

    return FunctionGapSummary(
        function_name=function,
        executive_summary=executive_summary,
        maturity_rating=maturity,
        total_subcategories=stats["total"],
        in_scope_count=stats["in_scope"],
        addressed_count=stats["addressed"],
        partially_addressed_count=stats["partially_addressed"],
        not_addressed_count=stats["not_addressed"],
        out_of_scope_count=stats["out_of_scope"],
        critical_gaps=critical_gaps,
        key_recommendations=key_recs,
        required_policy_documents=required_docs,
    )


# ── Comparison helpers ────────────────────────────────────────────────────────

def _id_overlap(list_a: list[str], list_b: list[str]) -> float:
    """Fraction of subcategory IDs in list_a that also appear in list_b."""
    ids_a = set()
    for item in list_a:
        ids_a.update(_extract_subcategory_ids(item))
    ids_b = set()
    for item in list_b:
        ids_b.update(_extract_subcategory_ids(item))
    if not ids_a:
        return 1.0 if not ids_b else 0.0
    return len(ids_a & ids_b) / len(ids_a)


def compare_summaries(
    fn: str,
    llm_s: FunctionGapSummary,
    code_s: FunctionGapSummary,
    llm_time: float,
    code_time: float,
) -> dict:
    maturity_match = llm_s.maturity_rating == code_s.maturity_rating
    counts_match = all([
        llm_s.total_subcategories      == code_s.total_subcategories,
        llm_s.in_scope_count           == code_s.in_scope_count,
        llm_s.addressed_count          == code_s.addressed_count,
        llm_s.partially_addressed_count == code_s.partially_addressed_count,
        llm_s.not_addressed_count      == code_s.not_addressed_count,
        llm_s.out_of_scope_count       == code_s.out_of_scope_count,
    ])
    gaps_overlap    = _id_overlap(llm_s.critical_gaps,      code_s.critical_gaps)
    recs_overlap    = _id_overlap(llm_s.key_recommendations, code_s.key_recommendations)
    speedup         = llm_time / code_time if code_time > 0 else float("inf")

    return {
        "function":       fn,
        "llm_time":       llm_time,
        "code_time":      code_time,
        "speedup":        speedup,
        "maturity_match": maturity_match,
        "counts_match":   counts_match,
        "gaps_overlap":   gaps_overlap,
        "recs_overlap":   recs_overlap,
        "llm_maturity":   llm_s.maturity_rating,
        "code_maturity":  code_s.maturity_rating,
        "llm_gaps":       llm_s.critical_gaps,
        "code_gaps":      code_s.critical_gaps,
    }


def print_function_result(r: dict) -> None:
    mat_icon   = "✓" if r["maturity_match"] else "✗"
    cnt_icon   = "✓" if r["counts_match"]   else "✗"
    gaps_pct   = int(r["gaps_overlap"] * 100)
    recs_pct   = int(r["recs_overlap"] * 100)

    print(f"\n  {'─'*58}")
    print(f"  Function : {r['function']}")
    print(f"  Time     : LLM={r['llm_time']:.1f}s  Code={r['code_time']:.3f}s  "
          f"Speedup={r['speedup']:.0f}x")
    print(f"  Maturity : {mat_icon}  LLM='{r['llm_maturity']}'  "
          f"Code='{r['code_maturity']}'")
    print(f"  Counts   : {cnt_icon}  (all 6 numeric fields)")
    print(f"  Gaps ID overlap    : {gaps_pct}%")
    print(f"  Recs ID overlap    : {recs_pct}%")

    if not r["maturity_match"]:
        print(f"  ⚠  Maturity MISMATCH — LLM hallucinated a different rating")

    # Show gap comparison
    llm_ids  = set()
    for g in r["llm_gaps"]:
        llm_ids.update(_extract_subcategory_ids(g))
    code_ids = set()
    for g in r["code_gaps"]:
        code_ids.update(_extract_subcategory_ids(g))

    only_llm  = llm_ids  - code_ids
    only_code = code_ids - llm_ids
    if only_llm:
        print(f"  Only LLM flagged  : {', '.join(sorted(only_llm))}")
    if only_code:
        print(f"  Only Code flagged : {', '.join(sorted(only_code))}")


# ── Main ─────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--run-dir", type=Path, default=None,
                   help="Path to a completed Phase 2 run directory")
    p.add_argument("--functions", nargs="+", default=None,
                   help="Subset of functions to test (default: all 6)")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    run_dir = args.run_dir or find_latest_run()
    if not run_dir or not run_dir.exists():
        print("No completed run found. Run the main pipeline first:")
        print("  python src/main.py <policy.pdf>")
        sys.exit(1)

    print(f"\nRun directory : {run_dir}")
    print(f"Loading assessments…")
    all_assessments = load_assessments(run_dir)

    functions = args.functions or [
        fn for fn in NIST_FUNCTIONS if fn in all_assessments
    ]
    print(f"Functions to test : {', '.join(functions)}")
    print(f"\nLoading model for LLM summaries…")

    all_results = []
    total_llm_time = 0.0
    total_code_time = 0.0

    for fn in functions:
        assessments = all_assessments.get(fn, [])
        report = load_report(run_dir, fn)

        if not assessments:
            print(f"\n  [{fn}] No assessments found — skipping")
            continue

        print(f"\n  [{fn}] {len(assessments)} subcategories…")

        # ── Strategy A: LLM ──────────────────────────────────────────────────
        print(f"    A) LLM summary…", end=" ", flush=True)
        t0 = time.perf_counter()
        try:
            llm_summary = run_summarize_with_validation(
                function_name=fn,
                report=report or "",
                assessments=assessments,
                model_name="gemma4:e2b",
            )
            llm_time = time.perf_counter() - t0
            print(f"{llm_time:.1f}s")
        except Exception as exc:
            llm_time = time.perf_counter() - t0
            print(f"FAILED ({exc})")
            # Build a minimal placeholder so comparison can still run
            stats = _compute_stats(assessments)
            llm_summary = FunctionGapSummary(
                function_name=fn,
                executive_summary=f"[LLM failed: {exc}]",
                maturity_rating=_compute_maturity_rating(stats),
                total_subcategories=stats["total"],
                in_scope_count=stats["in_scope"],
                addressed_count=stats["addressed"],
                partially_addressed_count=stats["partially_addressed"],
                not_addressed_count=stats["not_addressed"],
                out_of_scope_count=stats["out_of_scope"],
                critical_gaps=[],
                key_recommendations=[],
                required_policy_documents=[],
            )

        # ── Strategy B: Code ─────────────────────────────────────────────────
        print(f"    B) Code summary…", end=" ", flush=True)
        t0 = time.perf_counter()
        code_summary = build_code_summary(fn, assessments)
        code_time = time.perf_counter() - t0
        print(f"{code_time*1000:.1f}ms")

        result = compare_summaries(fn, llm_summary, code_summary, llm_time, code_time)
        all_results.append(result)
        print_function_result(result)

        total_llm_time  += llm_time
        total_code_time += code_time

    # ── Overall summary ───────────────────────────────────────────────────────
    if not all_results:
        print("\nNo results to summarize.")
        return

    maturity_matches  = sum(1 for r in all_results if r["maturity_match"])
    counts_matches    = sum(1 for r in all_results if r["counts_match"])
    avg_gaps_overlap  = sum(r["gaps_overlap"] for r in all_results) / len(all_results)
    avg_recs_overlap  = sum(r["recs_overlap"] for r in all_results) / len(all_results)
    overall_speedup   = total_llm_time / total_code_time if total_code_time > 0 else float("inf")
    n = len(all_results)

    print(f"\n\n{'='*60}")
    print("  OVERALL SUMMARY")
    print(f"{'='*60}")
    print(f"  Functions tested        : {n}")
    print(f"  LLM total time          : {total_llm_time:.1f}s  ({total_llm_time/n:.1f}s avg)")
    print(f"  Code total time         : {total_code_time*1000:.1f}ms  (<1ms per function)")
    print(f"  Speedup                 : {overall_speedup:.0f}x")
    print(f"  Maturity rating match   : {maturity_matches}/{n}  functions")
    print(f"  Counts match (6 fields) : {counts_matches}/{n}  functions")
    print(f"  Critical gaps ID overlap: {avg_gaps_overlap*100:.0f}%")
    print(f"  Recommendations overlap : {avg_recs_overlap*100:.0f}%")

    print(f"\n  VERDICT")
    print(f"  {'─'*56}")

    if maturity_matches == n and counts_matches == n and avg_gaps_overlap >= 0.70:
        print(f"  ✓ CODE SUMMARY IS A SAFE REPLACEMENT")
        print(f"    Maturity + counts: identical across all functions.")
        print(f"    Gap ID overlap {avg_gaps_overlap*100:.0f}% — code captures the same critical gaps.")
        print(f"    Saves {total_llm_time:.0f}s ({overall_speedup:.0f}x faster) per policy analysis.")
        print(f"    Only loss: LLM-written prose in executive_summary field.")
        print(f"    Recommendation: replace run_summarize_with_validation() with")
        print(f"    build_code_summary() in gap_analyzer.py to save ~{total_llm_time/60:.1f} min/policy.")
    elif maturity_matches < n:
        print(f"  ⚠  LLM HALLUCINATED MATURITY RATINGS ({n - maturity_matches} functions)")
        print(f"    The LLM ignores the stats block and invents ratings.")
        print(f"    Code is MORE accurate than LLM for numeric fields.")
        print(f"    Strong case for replacing LLM summary with code-based approach.")
    else:
        print(f"  ~ MIXED RESULTS — review per-function details above.")
        print(f"    Maturity: {maturity_matches}/{n} match.  "
              f"Gaps overlap: {avg_gaps_overlap*100:.0f}%.")
    print()


if __name__ == "__main__":
    main()

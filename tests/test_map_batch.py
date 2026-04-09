"""
Map strategy comparison: Sequential (current) vs Batched (proposed).

Current approach  — _map_one_section():
  For each subcategory: N_sections sequential LLM calls → N_sections results
  Cost: N_sections × ~4s = ~60s per subcategory

Batched approach  — _map_all_sections_batched():
  For each subcategory: 1 LLM call with all sections → N_sections results
  Cost: 1 call × ~10-15s = ~10-15s per subcategory

This test runs both strategies on the same 3 subcategories using real policy
sections and compares:
  - Wall-clock time (speedup factor)
  - Agreement rate  (do both find the same sections as having evidence?)
  - Evidence quality (are the snippets meaningful?)

Run from repo root:
    python tests/test_map_batch.py

Requires a completed Phase 1 run with sections_output.json. Defaults to the
ISMS strong benchmark run if available; falls back to inline sample sections.
"""

from __future__ import annotations

import json
import os
import sys
import time
import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm import create_llm

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("map_batch_test")

# ── Test subcategories (representative mix) ───────────────────────────────────
# Chosen to cover: a topic clearly present, one partially present, one absent.
TEST_SUBCATEGORIES = [
    {
        "id": "GV.OC-01",
        "description": (
            "The organizational mission is understood and informs cybersecurity "
            "risk management. Cybersecurity decisions are made with explicit "
            "awareness of what the organization exists to do and what would cause "
            "the most harm if disrupted."
        ),
    },
    {
        "id": "GV.RM-02",
        "description": (
            "Risk appetite and risk tolerance statements are established, "
            "communicated, and maintained. Risk appetite defines how much risk "
            "the organization will accept; tolerance defines acceptable variation."
        ),
    },
    {
        "id": "GV.SC-03",
        "description": (
            "Cybersecurity supply chain risk management is integrated into "
            "broader enterprise risk management and cybersecurity risk programs. "
            "Third-party and vendor risks are formally assessed and managed."
        ),
    },
]

# ── Schemas ───────────────────────────────────────────────────────────────────

class SectionEvidenceResult(BaseModel):
    """Current approach: result for ONE section × ONE subcategory."""
    has_evidence: bool = Field(
        description="True if this section contains text relevant to the subcategory."
    )
    evidence_snippet: str = Field(
        description="Direct quote (max 200 chars) from the section, or 'None found'."
    )


class BatchSectionMatch(BaseModel):
    """Batched approach: result for ONE section (part of a batch response)."""
    section_number: str = Field(
        description="The section number exactly as given in the input."
    )
    has_evidence: bool = Field(
        description="True if this section contains relevant text."
    )
    evidence_snippet: str = Field(
        description="Direct quote (max 200 chars) from the section, or 'None found'."
    )


class BatchMapResult(BaseModel):
    """Batched approach: results for ALL sections in one LLM call."""
    sections: list[BatchSectionMatch] = Field(
        description=(
            "One entry per section provided. Include ALL section numbers — "
            "set has_evidence=false for sections with no relevant content."
        )
    )


# ── Load sections ─────────────────────────────────────────────────────────────

def _load_sections() -> list[dict]:
    """Load sections from the latest benchmark run, or use inline fallback."""
    results_dir = Path(__file__).parent / "benchmark_results"
    if results_dir.exists():
        runs = sorted(results_dir.iterdir(), reverse=True)
        for run in runs:
            candidate = run / "01_isms_strong" / "sections_output.json"
            if candidate.exists():
                sections = json.loads(candidate.read_text())
                meaningful = [
                    s for s in sections
                    if len((s.get("content") or "").strip()) >= 80
                ]
                if meaningful:
                    print(f"  Loaded {len(meaningful)} sections from {candidate}")
                    return meaningful

    # Inline fallback — 5 representative sections
    print("  Using inline fallback sections (no benchmark run found)")
    return [
        {
            "number": "1",
            "title": "Purpose and Scope",
            "content": (
                "This ISMS Policy establishes the framework for protecting "
                "confidentiality, integrity, and availability of Acme Technologies "
                "information assets. The policy applies to all employees, contractors "
                "and third parties. Our mission is to deliver innovative technology "
                "solutions and cybersecurity decisions are made with explicit awareness "
                "of this mission."
            ),
        },
        {
            "number": "2",
            "title": "Risk Management Strategy",
            "content": (
                "Risk appetite statements have been formally approved by the Board: "
                "Low appetite for operational risk, zero tolerance for compliance "
                "violations. Risk tolerance thresholds are defined in the Risk "
                "Assessment Policy. Risk owners are trained on tolerance levels and "
                "must escalate when thresholds are breached. The organization uses "
                "mitigate, transfer, accept, and avoid as response strategies."
            ),
        },
        {
            "number": "3",
            "title": "Asset Management",
            "content": (
                "All hardware and software assets are tracked in a CMDB updated "
                "in real-time. Network components including routers, switches, "
                "firewalls are inventoried. Assets are tracked through full lifecycle: "
                "procurement, deployment, operation, and disposal."
            ),
        },
        {
            "number": "4",
            "title": "Data Security",
            "content": (
                "All Restricted and Confidential data must be encrypted at rest "
                "using AES-256. All data transmissions involving sensitive data "
                "must use TLS 1.2 or higher. Unencrypted protocols are prohibited."
            ),
        },
        {
            "number": "5",
            "title": "Policy Compliance",
            "content": (
                "Compliance with this policy is mandatory. Violations are subject "
                "to disciplinary action. Exceptions require written approval from "
                "the CISO with a documented risk acceptance rationale."
            ),
        },
    ]


# ── Strategy A: Sequential (current) ─────────────────────────────────────────

def run_sequential(
    sections: list[dict],
    sub: dict,
    llm,
) -> tuple[list[dict], float]:
    """
    Current approach: one LLM call per section.
    Returns (results, wall_seconds).
    """
    structured_llm = llm.with_structured_output(SectionEvidenceResult)
    results = []
    t0 = time.perf_counter()

    for s in sections:
        prompt = (
            f"Policy section {s['number']} — {s['title']}:\n\n"
            f"{s['content']}\n\n"
            f"---\n\n"
            f"NIST subcategory {sub['id']} requires:\n{sub['description']}\n\n"
            f"Does this section contain any text relevant to this requirement? "
            f"If yes, quote the most relevant passage (max 200 chars). "
            f"If no, set has_evidence=false."
        )
        try:
            r = structured_llm.invoke(prompt)
            results.append({
                "section": s["number"],
                "title": s["title"],
                "has_evidence": r.has_evidence,
                "snippet": r.evidence_snippet,
            })
        except Exception as exc:
            log.warning("Sequential call failed s%s: %s", s["number"], exc)
            results.append({
                "section": s["number"],
                "title": s["title"],
                "has_evidence": False,
                "snippet": "None found",
            })

    wall = time.perf_counter() - t0
    return results, wall


# ── Strategy B: Batched (proposed) ───────────────────────────────────────────

def run_batched(
    sections: list[dict],
    sub: dict,
    llm,
) -> tuple[list[dict], float]:
    """
    Proposed approach: one LLM call with all sections concatenated.
    Returns (results, wall_seconds).
    """
    structured_llm = llm.with_structured_output(BatchMapResult)

    sections_block = "\n\n".join(
        f"[Section {s['number']}] {s['title']}\n{s['content']}"
        for s in sections
    )
    section_nums = [s["number"] for s in sections]
    section_titles = {s["number"]: s["title"] for s in sections}

    prompt = (
        f"You are scanning a policy document for evidence related to a NIST CSF requirement.\n\n"
        f"NIST subcategory {sub['id']} requires:\n{sub['description']}\n\n"
        f"---\n\n"
        f"Below are {len(sections)} policy sections. For EACH section, determine "
        f"whether it contains text relevant to the requirement above.\n\n"
        f"You MUST return one result entry per section (all {len(sections)} of them), "
        f"using the exact section numbers shown in brackets.\n\n"
        f"{sections_block}\n\n"
        f"---\n\n"
        f"Return one entry for every section number: "
        f"{', '.join(section_nums)}."
    )

    results = []
    t0 = time.perf_counter()

    try:
        batch_result = structured_llm.invoke(prompt)
        # Index by section_number for alignment
        result_map = {r.section_number: r for r in batch_result.sections}

        for num in section_nums:
            r = result_map.get(num)
            if r:
                results.append({
                    "section": num,
                    "title": section_titles[num],
                    "has_evidence": r.has_evidence,
                    "snippet": r.evidence_snippet,
                })
            else:
                # Model missed this section number in its response
                results.append({
                    "section": num,
                    "title": section_titles[num],
                    "has_evidence": False,
                    "snippet": "None found (section missing from batch response)",
                })
    except Exception as exc:
        log.warning("Batched call failed: %s", exc)
        for s in sections:
            results.append({
                "section": s["number"],
                "title": s["title"],
                "has_evidence": False,
                "snippet": f"None found (batch failed: {exc})",
            })

    wall = time.perf_counter() - t0
    return results, wall


# ── Comparison helpers ────────────────────────────────────────────────────────

def agreement_rate(seq_results: list[dict], bat_results: list[dict]) -> float:
    """Fraction of sections where both strategies agree on has_evidence."""
    bat_map = {r["section"]: r["has_evidence"] for r in bat_results}
    matches = sum(
        1 for r in seq_results
        if bat_map.get(r["section"]) == r["has_evidence"]
    )
    return matches / len(seq_results) if seq_results else 0.0


def missing_rate(seq_results: list[dict], bat_results: list[dict]) -> float:
    """Fraction of sections the batch response omitted entirely."""
    bat_nums = {r["section"] for r in bat_results}
    seq_nums = {r["section"] for r in seq_results}
    missing = seq_nums - bat_nums
    return len(missing) / len(seq_nums) if seq_nums else 0.0


def print_side_by_side(
    sub_id: str,
    sections: list[dict],
    seq_results: list[dict],
    bat_results: list[dict],
) -> None:
    bat_map = {r["section"]: r for r in bat_results}
    seq_map = {r["section"]: r for r in seq_results}

    print(f"\n  Subcategory: {sub_id}")
    print(f"  {'Sec':<4} {'Title':<38} {'Seq':^8} {'Batch':^8}  {'Match':^6}")
    print(f"  {'─'*4} {'─'*38} {'─'*8} {'─'*8}  {'─'*6}")

    for s in sections:
        num = s["number"]
        seq_r = seq_map.get(num)
        bat_r = bat_map.get(num)
        seq_flag  = "✓" if (seq_r and seq_r["has_evidence"]) else "✗"
        bat_flag  = "✓" if (bat_r and bat_r["has_evidence"]) else "✗"
        match = "=" if seq_flag == bat_flag else "≠"
        title = s["title"][:36]
        print(f"  {num:<4} {title:<38} {seq_flag:^8} {bat_flag:^8}  {match:^6}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading model…")
    llm = create_llm(n_ctx=8192, max_tokens=1024)
    print("Model loaded.\n")

    sections = _load_sections()
    n = len(sections)

    total_seq_time = 0.0
    total_bat_time = 0.0
    all_agreements = []
    all_missing = []

    for sub in TEST_SUBCATEGORIES:
        print(f"\n{'='*65}")
        print(f"  Subcategory: {sub['id']}")
        print(f"  {sub['description'][:80]}…")
        print(f"{'='*65}")

        # ── Sequential ──────────────────────────────────────────────────────
        print(f"\n  [A] Sequential — {n} LLM calls…")
        seq_results, seq_time = run_sequential(sections, sub, llm)
        seq_hits = sum(1 for r in seq_results if r["has_evidence"])
        print(f"      Done in {seq_time:.1f}s  |  {seq_hits}/{n} sections with evidence")

        # ── Batched ─────────────────────────────────────────────────────────
        print(f"\n  [B] Batched  — 1 LLM call…")
        bat_results, bat_time = run_batched(sections, sub, llm)
        bat_hits = sum(1 for r in bat_results if r["has_evidence"])
        miss_r = missing_rate(seq_results, bat_results)
        print(f"      Done in {bat_time:.1f}s  |  {bat_hits}/{n} sections with evidence")
        if miss_r > 0:
            print(f"      WARNING: batch omitted {miss_r*100:.0f}% of sections from response")

        # ── Agreement ────────────────────────────────────────────────────────
        agree = agreement_rate(seq_results, bat_results)
        speedup = seq_time / bat_time if bat_time > 0 else 0
        print(f"\n  Agreement: {agree*100:.0f}%  |  Speedup: {speedup:.2f}x")

        print_side_by_side(sub["id"], sections, seq_results, bat_results)

        total_seq_time += seq_time
        total_bat_time += bat_time
        all_agreements.append(agree)
        all_missing.append(miss_r)

    # ── Summary ──────────────────────────────────────────────────────────────
    overall_speedup = total_seq_time / total_bat_time if total_bat_time > 0 else 0
    avg_agreement   = sum(all_agreements) / len(all_agreements)
    avg_missing     = sum(all_missing) / len(all_missing)

    print(f"\n\n{'='*65}")
    print("  SUMMARY")
    print(f"{'='*65}")
    print(f"  Subcategories tested : {len(TEST_SUBCATEGORIES)}")
    print(f"  Sections per sub     : {n}")
    print(f"  Sequential total     : {total_seq_time:.1f}s  ({total_seq_time/len(TEST_SUBCATEGORIES):.1f}s avg/sub)")
    print(f"  Batched total        : {total_bat_time:.1f}s  ({total_bat_time/len(TEST_SUBCATEGORIES):.1f}s avg/sub)")
    print(f"  Speedup              : {overall_speedup:.2f}x")
    print(f"  Agreement rate       : {avg_agreement*100:.0f}%  (how often batch agrees with sequential)")
    print(f"  Missing section rate : {avg_missing*100:.0f}%  (sections batch omitted from response)")

    print(f"\n  VERDICT")
    print(f"  {'─'*60}")

    if overall_speedup >= 2.0 and avg_agreement >= 0.80 and avg_missing <= 0.10:
        print(f"  ✓ BATCHING IS WORTH IT")
        print(f"    {overall_speedup:.1f}x faster with {avg_agreement*100:.0f}% agreement.")
        print(f"    Recommendation: replace _map_sections_for_subcategory() with")
        print(f"    the batched implementation to cut Map-phase time by ~{(1-1/overall_speedup)*100:.0f}%.")
    elif overall_speedup >= 2.0 and avg_agreement < 0.80:
        print(f"  ⚠  BATCHING IS FAST BUT LOSSY")
        print(f"    {overall_speedup:.1f}x faster but only {avg_agreement*100:.0f}% agreement.")
        print(f"    The model loses precision when scanning all sections at once.")
        print(f"    Consider: batch in groups of 4-5 sections instead of all-at-once.")
    elif overall_speedup < 2.0:
        print(f"  ✗ BATCHING GIVES NO MEANINGFUL SPEEDUP ({overall_speedup:.2f}x)")
        print(f"    llama.cpp likely bottlenecks on the larger prompt, not on call overhead.")
        print(f"    Keep the current sequential approach.")

    print()


if __name__ == "__main__":
    main()

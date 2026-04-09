"""
Parallelism feasibility test for ChatLlamaCpp + LangChain.

Tests four strategies to determine if llama.cpp can handle concurrent
inference and whether it's safe to parallelize the Map phase.

Run from repo root:
    python tests/test_parallelism.py

What each test does:
  1. Sequential baseline       — 3 calls back-to-back, measures baseline latency
  2. ThreadPoolExecutor        — 3 calls fired simultaneously via threads
  3. LangChain .batch()        — uses LangChain's built-in batch dispatch
  4. asyncio + ainvoke         — async concurrent calls via event loop

A test PASSES parallelism if wall-clock time < 0.7 × sequential time.
If llama.cpp serializes internally, threaded/async wall time ≈ sequential.
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from llm import create_llm
from langchain_core.messages import HumanMessage, SystemMessage

logging.basicConfig(level=logging.WARNING)  # suppress llm noise during test

PROMPT = "Reply with exactly one sentence: what is risk management?"
SYSTEM  = "You are a concise assistant. One sentence only."
N = 3  # number of concurrent calls — keep small to avoid OOM

MESSAGES = [
    SystemMessage(content=SYSTEM),
    HumanMessage(content=PROMPT),
]


# ── helpers ──────────────────────────────────────────────────────────────────

def _call(llm, i: int) -> tuple[int, float, str]:
    """Single blocking LLM call. Returns (index, elapsed_sec, reply_text)."""
    t0 = time.perf_counter()
    result = llm.invoke(MESSAGES)
    elapsed = time.perf_counter() - t0
    text = result.content if hasattr(result, "content") else str(result)
    return i, elapsed, text[:80]


# ── Test 1: Sequential ────────────────────────────────────────────────────────

def test_sequential(llm) -> float:
    print(f"\n{'─'*60}")
    print(f"  Test 1: Sequential ({N} calls)")
    print(f"{'─'*60}")
    t0 = time.perf_counter()
    for i in range(N):
        idx, elapsed, text = _call(llm, i)
        print(f"  [{idx}] {elapsed:.1f}s  →  {text!r}")
    wall = time.perf_counter() - t0
    print(f"  Wall time: {wall:.1f}s")
    return wall


# ── Test 2: ThreadPoolExecutor ───────────────────────────────────────────────

def test_threads(llm) -> float:
    print(f"\n{'─'*60}")
    print(f"  Test 2: ThreadPoolExecutor ({N} threads)")
    print(f"{'─'*60}")
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=N) as pool:
        futures = [pool.submit(_call, llm, i) for i in range(N)]
        for fut in as_completed(futures):
            idx, elapsed, text = fut.result()
            print(f"  [{idx}] {elapsed:.1f}s  →  {text!r}")
    wall = time.perf_counter() - t0
    print(f"  Wall time: {wall:.1f}s")
    return wall


# ── Test 3: LangChain .batch() ───────────────────────────────────────────────

def test_batch(llm) -> float:
    print(f"\n{'─'*60}")
    print(f"  Test 3: LangChain .batch() ({N} inputs)")
    print(f"{'─'*60}")
    inputs = [MESSAGES] * N
    t0 = time.perf_counter()
    try:
        results = llm.batch(inputs)
        wall = time.perf_counter() - t0
        for i, r in enumerate(results):
            text = r.content if hasattr(r, "content") else str(r)
            print(f"  [{i}]  →  {text[:80]!r}")
    except Exception as exc:
        wall = time.perf_counter() - t0
        print(f"  FAILED: {exc}")
    print(f"  Wall time: {wall:.1f}s")
    return wall


# ── Test 4: asyncio + ainvoke ────────────────────────────────────────────────

def test_async(llm) -> float:
    print(f"\n{'─'*60}")
    print(f"  Test 4: asyncio + ainvoke ({N} coroutines)")
    print(f"{'─'*60}")

    async def _async_call(i: int):
        t0 = time.perf_counter()
        try:
            result = await llm.ainvoke(MESSAGES)
            elapsed = time.perf_counter() - t0
            text = result.content if hasattr(result, "content") else str(result)
            print(f"  [{i}] {elapsed:.1f}s  →  {text[:80]!r}")
            return elapsed
        except Exception as exc:
            elapsed = time.perf_counter() - t0
            print(f"  [{i}] FAILED after {elapsed:.1f}s: {exc}")
            return elapsed

    async def _run():
        return await asyncio.gather(*[_async_call(i) for i in range(N)])

    t0 = time.perf_counter()
    try:
        asyncio.run(_run())
    except Exception as exc:
        print(f"  asyncio.run FAILED: {exc}")
    wall = time.perf_counter() - t0
    print(f"  Wall time: {wall:.1f}s")
    return wall


# ── Verdict ──────────────────────────────────────────────────────────────────

def verdict(label: str, seq_time: float, parallel_time: float) -> None:
    speedup = seq_time / parallel_time if parallel_time > 0 else 0
    threshold = 0.7  # 30% faster = meaningful parallelism
    parallelized = parallel_time < seq_time * threshold
    status = "PARALLEL ✓" if parallelized else "SERIALIZED ✗"
    print(f"  {label:<30} speedup={speedup:.2f}x  [{status}]")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading model (this may take a few seconds)…")
    # Use smaller n_ctx for the test to load faster
    llm = create_llm(n_ctx=4096, max_tokens=64)
    print("Model loaded.\n")

    seq   = test_sequential(llm)
    thr   = test_threads(llm)
    bat   = test_batch(llm)
    aio   = test_async(llm)

    print(f"\n{'='*60}")
    print("  RESULTS SUMMARY")
    print(f"{'='*60}")
    print(f"  Sequential baseline: {seq:.1f}s ({seq/N:.1f}s per call)")
    verdict("ThreadPoolExecutor", seq, thr)
    verdict("LangChain .batch()", seq, bat)
    verdict("asyncio + ainvoke",  seq, aio)

    print(f"\n{'='*60}")
    print("  INTERPRETATION")
    print(f"{'='*60}")
    any_parallel = any(
        t < seq * 0.7 for t in [thr, bat, aio]
    )
    if any_parallel:
        print("  ✓ At least one strategy achieves real parallelism.")
        print("  → Safe to fire multiple Map-phase section scans concurrently.")
        print("  → Recommendation: use ThreadPoolExecutor or .batch() in nist_gap_agents.py")
    else:
        print("  ✗ llama.cpp serializes all concurrent calls (GIL or internal lock).")
        print("  → Parallelising the Map phase will NOT reduce wall-clock time.")
        print("  → Consider: load N model instances (high RAM) or accept serial execution.")
    print()


if __name__ == "__main__":
    main()

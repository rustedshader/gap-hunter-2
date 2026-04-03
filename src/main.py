"""
Gap Hunter 2 — Policy Section Extractor

Extracts structured sections from policy PDFs using a sliding‑window
LLM approach with carry‑over context for cross‑boundary sections.
"""

import logging
import sys
from pathlib import Path

from extractor import extract_all_sections, save_sections_json

# ── Configuration ──────────────────────────────
PDF_SOURCE   = Path("./policies/Data-protection-and-data-security-policy-R1.0-2021-09-24.pdf")
OUTPUT_JSON  = Path("sections_output.json")
MODEL_NAME   = "gemma4:e2b"
WINDOW_SIZE  = 80   # lines per chunk
OVERLAP      = 20   # lines shared between consecutive chunks

# ── Logging ────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def main() -> None:
    log.info("Starting extraction: %s → %s", PDF_SOURCE, OUTPUT_JSON)
    log.info("Model: %s | Window: %d lines | Overlap: %d lines", MODEL_NAME, WINDOW_SIZE, OVERLAP)

    sections = extract_all_sections(
        pdf_path=PDF_SOURCE,
        model_name=MODEL_NAME,
        window_size=WINDOW_SIZE,
        overlap=OVERLAP,
    )

    save_sections_json(sections, OUTPUT_JSON)

    log.info("Done — extracted %d sections", len(sections))

    # Quick summary to stdout
    print(f"\n{'─' * 60}")
    print(f"  Extracted {len(sections)} sections from {PDF_SOURCE.name}")
    print(f"  Output: {OUTPUT_JSON}")
    print(f"{'─' * 60}\n")

    for s in sections:
        status = "✓" if s.is_complete else "… (continues)"
        print(f"  [{s.number}] {s.title}  (lines {s.start_line}–{s.end_line})  {status}")

    print()


if __name__ == "__main__":
    main()

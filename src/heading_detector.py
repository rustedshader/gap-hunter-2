"""
Multi-pattern heading detector for PDF-converted markdown documents.

Tries heading patterns in priority order and returns the first that
yields a plausible number of sections (2–100). Falls back to a combined
markdown+numbered pass for mixed-format documents.

Priority:
  P1  markdown   ## Title  or  ## N. Title
  P2  numbered   1. Title  (short lines only, ≤60 chars after the number)
  P3  allcaps    ALL CAPS HEADING
  P4  bold       **Title**
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

MIN_SECTIONS = 2
MAX_SECTIONS = 100


@dataclass
class HeadingCandidate:
    line_num: int
    title: str
    pattern: str


# Each tuple: (name, compiled_regex).
# Every regex must have exactly one capture group that yields the title text.
_PATTERNS: list[tuple[str, re.Pattern]] = [
    # P1 – Markdown heading: strips leading hashes and optional leading number
    ("markdown", re.compile(r'^#{1,3}\s+(?:\d+[\.\s]+)?(.+)$')),
    # P2 – Plain numbered heading: title portion capped at 60 chars
    #       Rejects inline heading+content lines that Docling sometimes produces
    ("numbered", re.compile(r'^\d+[\.\)]\s+(.{1,60})$')),
    # P3 – ALL CAPS heading (5–80 chars, only caps/digits/punctuation allowed)
    ("allcaps", re.compile(r'^([A-Z][A-Z\s\d\-\(\)\/\:\&]{4,79})$')),
    # P4 – Bold markdown heading
    ("bold", re.compile(r'^\*\*([^*]{3,80})\*\*$')),
]


def _clean_title(raw: str, pattern: str) -> str | None:
    """
    Clean and sanity-check an extracted title.
    Returns None if the text looks like sentence content rather than a heading.
    """
    title = raw.strip()
    if not title:
        return None
    # Long sentence ending in a period → body content, not a heading
    if title.endswith('.') and len(title) > 20:
        return None
    # Numbered lines that are too long are inline heading+content from Docling
    if pattern == "numbered" and len(title) > 60:
        return None
    return title


def detect_headings(doc_lines: list[tuple[int, str]]) -> list[HeadingCandidate]:
    """
    Scan doc_lines for section headings using multiple patterns.

    Returns a sorted list of HeadingCandidate, or [] if no reliable
    pattern found (caller should fall back to LLM pipeline).
    """
    results: dict[str, list[HeadingCandidate]] = {}

    for pat_name, pat_regex in _PATTERNS:
        candidates: list[HeadingCandidate] = []
        for ln, text in doc_lines:
            m = pat_regex.match(text.strip())
            if m:
                # Last capture group is always the title
                raw_title = m.group(m.lastindex)
                title = _clean_title(raw_title, pat_name)
                if title:
                    candidates.append(HeadingCandidate(ln, title, pat_name))
        results[pat_name] = candidates
        logger.debug("Pattern %-10s : %d candidates", pat_name, len(candidates))

    # --- Try single-pattern match in priority order ---
    for pat_name, _ in _PATTERNS:
        hits = results[pat_name]
        if MIN_SECTIONS <= len(hits) <= MAX_SECTIONS:
            logger.info(
                "Heading detection: pattern='%s', %d headings found",
                pat_name, len(hits),
            )
            return sorted(hits, key=lambda h: h.line_num)

    # --- Fallback: combine markdown + numbered (handles mixed-format PDFs) ---
    seen: dict[int, HeadingCandidate] = {}
    # markdown takes precedence over numbered when on same line
    for h in results["numbered"] + results["markdown"]:
        seen[h.line_num] = h
    combined = sorted(seen.values(), key=lambda h: h.line_num)

    if MIN_SECTIONS <= len(combined) <= MAX_SECTIONS:
        logger.info(
            "Heading detection: combined markdown+numbered, %d headings found",
            len(combined),
        )
        return combined

    logger.info(
        "Heading detection: no reliable pattern found (counts: %s)",
        {k: len(v) for k, v in results.items()},
    )
    return []

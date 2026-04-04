"""
Sliding-window policy section extractor with multi-agent validation loop.

Architecture (per chunk):
  1. Extractor Agent — identifies sections from the chunk
  2. Validator Agent — compares extraction against original text, finds errors
  3. Corrector Agent — fixes errors flagged by validator
  Loop steps 2-3 until validator approves (max 2 correction rounds).

This works well with small models because validation ("is this right?")
is a much simpler task than extraction ("find everything").
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Generator

from langchain_ollama import ChatOllama

from models import (
    ChunkResult,
    ExtractedSection,
    IncompleteSection,
)
from agents.extractor_agent import run_extractor
from agents.validator_agent import run_validator
from agents.corrector_agent import run_corrector
from agents.schemas import ExtractionResult
from tools.pdf import pdf_to_markdown
from heading_detector import detect_headings

logger = logging.getLogger(__name__)

MAX_CORRECTION_ROUNDS = 2
# Max sections a single window can reasonably contain.
# window_size=80 lines can hold at most ~20 real sections; anything beyond is hallucination.
MAX_SECTIONS_PER_WINDOW = 20

# ──────────────────────────────────────────────
# 1. Document Preparation
# ──────────────────────────────────────────────

def prepare_document(pdf_path: Path) -> list[tuple[int, str]]:
    """Convert a PDF to markdown and return (line_number, text) tuples."""
    logger.info("Converting PDF to markdown: %s", pdf_path)
    md_text: str = pdf_to_markdown(pdf_path)
    lines = md_text.splitlines()
    numbered = [(i + 1, line) for i, line in enumerate(lines)]
    logger.info("Document has %d lines", len(numbered))
    return numbered


def extract_content_from_lines(
    doc_lines: list[tuple[int, str]],
    start_line: int,
    end_line: int,
    strip_heading: bool = True,
) -> str:
    """
    Extract content directly from source lines (no LLM involved).
    
    Args:
        doc_lines: Full document as (line_num, text) tuples
        start_line: First line of section (usually the heading)
        end_line: Last line of section
        strip_heading: If True, skip lines that look like headings (##, ALL CAPS)
    
    Returns:
        Extracted content as string
    """
    content_lines = []
    first_line_text = None
    
    for line_num, text in doc_lines:
        if start_line <= line_num <= end_line:
            # Remember first line to check if it's a heading
            if line_num == start_line:
                first_line_text = text.strip()
                # Skip if it's clearly a heading
                if strip_heading and (
                    text.strip().startswith('##') or 
                    (text.strip() and text.strip().isupper() and len(text.strip()) < 100)
                ):
                    continue
            
            # Skip any other lines that are section headings (## markers)
            if text.strip().startswith('##'):
                continue
                
            content_lines.append(text)
    
    return "\n".join(content_lines).strip()


# ──────────────────────────────────────────────
# 2. Rule-Based Section Detection
# ──────────────────────────────────────────────

def detect_rule_based_sections(doc_lines: list[tuple[int, str]]) -> list[ExtractedSection]:
    """
    Detect sections using structural heading patterns (no LLM).

    Works for any document that Docling converts with recognisable heading
    markers (##, numbered headings, ALL CAPS, bold).  Returns an empty list
    when no reliable pattern is found so the caller can fall back to the LLM
    pipeline.
    """
    headings = detect_headings(doc_lines)
    if not headings:
        return []

    last_line = doc_lines[-1][0]
    sections: list[ExtractedSection] = []

    for i, heading in enumerate(headings):
        start = heading.line_num
        # end = line just before next heading, or last doc line
        end = headings[i + 1].line_num - 1 if i + 1 < len(headings) else last_line

        content = extract_content_from_lines(doc_lines, start, end)

        sections.append(ExtractedSection(
            number=str(i + 1),
            title=heading.title,
            content=content,
            start_line=start,
            end_line=end,
            is_complete=True,
        ))

    logger.info("Rule-based detection: %d sections", len(sections))
    return sections


# ──────────────────────────────────────────────
# 3. Sliding Window Generator
# ──────────────────────────────────────────────

def build_windows(
    lines: list[tuple[int, str]],
    window_size: int = 80,
    overlap: int = 20,
) -> Generator[tuple[str, int, int], None, None]:
    """Yield (chunk_text, start_line, end_line) for each window."""
    step = window_size - overlap
    if step <= 0:
        raise ValueError("window_size must be greater than overlap")
    total = len(lines)
    i = 0
    while i < total:
        window = lines[i : i + window_size]
        chunk_text = "\n".join(f"LINE {ln}: {text}" for ln, text in window)
        start_line = window[0][0]
        end_line = window[-1][0]
        yield chunk_text, start_line, end_line
        i += step


# ──────────────────────────────────────────────
# 3. Multi-Agent Extraction Per Chunk
# ──────────────────────────────────────────────

def extract_sections_from_chunk(
    llm: ChatOllama,
    chunk_text: str,
    doc_lines: list[tuple[int, str]],
    start_line: int,
    end_line: int,
    last_section_num: int = 0,
    carry_over: IncompleteSection | None = None,
) -> ChunkResult:
    """Multi-agent extraction with validation loop. LLM identifies boundaries, content extracted directly."""

    # ── Agent 1: Extract boundaries only ──
    extraction = run_extractor(llm, chunk_text, start_line, end_line, last_section_num, carry_over)

    # Sanity check: too many sections = hallucination, discard immediately
    if len(extraction.sections) > MAX_SECTIONS_PER_WINDOW:
        logger.warning(
            "  Extractor returned %d sections (> cap %d) — likely hallucination, discarding",
            len(extraction.sections), MAX_SECTIONS_PER_WINDOW,
        )
        extraction.sections = []

    # ── Agent 2 + 3: Validate and Correct loop ──
    for round_num in range(1, MAX_CORRECTION_ROUNDS + 1):
        logger.info("  Validation round %d", round_num)

        # Agent 2: Validate boundaries
        validation = run_validator(llm, chunk_text, extraction)

        if validation.is_correct:
            logger.info("  -> Validator APPROVED (round %d)", round_num)
            break

        issues_text = "\n".join(f"  - {issue}" for issue in validation.issues)
        missing_text = "\n".join(f"  - {m}" for m in validation.missing_sections)
        logger.info("  -> Validator found issues (round %d):\n%s\n  Missing: %s",
                     round_num, issues_text, missing_text)

        # Agent 3: Correct boundaries
        prev_count = len(extraction.sections)
        corrected = run_corrector(llm, chunk_text, extraction, validation)

        # Reject correction if it hallucinated (too many sections) or made things worse
        if len(corrected.sections) > MAX_SECTIONS_PER_WINDOW:
            logger.warning(
                "  Corrector returned %d sections (> cap %d) — rejecting correction",
                len(corrected.sections), MAX_SECTIONS_PER_WINDOW,
            )
        else:
            extraction = corrected
    else:
        logger.warning("  Max correction rounds reached, using best extraction")

    # ── Validate and clamp line numbers to document bounds ──
    max_line = max(ln for ln, _ in doc_lines)
    
    # ── Extract content directly from source lines ──
    sections = []
    for s in extraction.sections:
        # Clamp line numbers to valid range
        clamped_start = max(1, min(s.start_line, max_line))
        clamped_end = max(1, min(s.end_line, max_line))
        
        if clamped_start != s.start_line or clamped_end != s.end_line:
            logger.warning("  Clamped section %d boundaries: (%d-%d) -> (%d-%d)",
                         s.section_num, s.start_line, s.end_line, clamped_start, clamped_end)
        
        # Skip sections with invalid boundaries
        if clamped_start > clamped_end:
            logger.warning("  Skipping section %d with invalid boundaries: %d-%d",
                         s.section_num, clamped_start, clamped_end)
            continue
        
        # Direct extraction from source (no LLM involvement)
        content = extract_content_from_lines(
            doc_lines,
            clamped_start,
            clamped_end,
            strip_heading=True  # Remove heading line from content
        )
        
        # Merge carry-over if applicable
        if carry_over and str(s.section_num) == carry_over.number:
            if carry_over.partial_content and carry_over.partial_content not in content:
                content = carry_over.partial_content + "\n" + content

        sections.append(ExtractedSection(
            number=str(s.section_num),
            title=s.title,
            content=content,  # From direct extraction, not LLM
            start_line=clamped_start,
            end_line=clamped_end,
            is_complete=True,  # will be overridden below if needed
        ))

    # Check if last section might be incomplete (extends to end of chunk)
    last = sections[-1] if sections else None
    has_incomplete = False
    inc_context = None
    if last and last.end_line >= end_line:
        has_incomplete = True
        last.is_complete = False
        inc_context = IncompleteSection(
            number=last.number,
            title=last.title,
            partial_content=last.content,
            original_start_line=last.start_line,
        )

    return ChunkResult(
        sections=sections,
        has_incomplete_section=has_incomplete,
        incomplete_section=inc_context,
    )


# ──────────────────────────────────────────────
# 4. Deduplication
# ──────────────────────────────────────────────

def _dedup_sections(sections: list[ExtractedSection]) -> list[ExtractedSection]:
    """Remove duplicate sections from overlapping windows using start_line as key."""
    best: dict[int, ExtractedSection] = {}
    
    for sec in sections:
        key = sec.start_line
        existing = best.get(key)
        
        if existing is None:
            best[key] = sec
        else:
            # Keep section with wider range (more complete boundaries)
            existing_range = existing.end_line - existing.start_line
            new_range = sec.end_line - sec.start_line
            if new_range > existing_range:
                logger.debug("  Replacing section at line %d (range %d -> %d)", 
                           key, existing_range, new_range)
                best[key] = sec
    
    deduped = sorted(best.values(), key=lambda s: s.start_line)
    logger.info("Deduplication: %d -> %d sections", len(sections), len(deduped))
    return deduped


def _remove_overlapping_sections(sections: list[ExtractedSection]) -> list[ExtractedSection]:
    """
    Remove sections that overlap with others, keeping only non-overlapping top-level sections.
    When sections overlap, keep the one that started first (parent section).
    """
    if not sections:
        return sections
    
    sorted_sections = sorted(sections, key=lambda s: (s.start_line, -(s.end_line - s.start_line)))
    filtered = []
    
    for sec in sorted_sections:
        # Check if this section overlaps with any already accepted section
        overlaps = False
        for accepted in filtered:
            # Check if sec is contained within accepted section
            if accepted.start_line <= sec.start_line <= accepted.end_line:
                overlaps = True
                logger.debug("  Filtering out nested section: %s (lines %d-%d) nested in %s (lines %d-%d)",
                           sec.title, sec.start_line, sec.end_line,
                           accepted.title, accepted.start_line, accepted.end_line)
                break
        
        if not overlaps:
            filtered.append(sec)
    
    # Re-sort by start_line
    filtered = sorted(filtered, key=lambda s: s.start_line)
    logger.info("Overlap filtering: %d -> %d sections", len(sections), len(filtered))
    return filtered


def _renumber_sections(sections: list[ExtractedSection]) -> list[ExtractedSection]:
    """
    Renumber sections sequentially based on their position in the document.
    This fixes any duplicate numbering issues from the LLM.
    """
    renumbered = []
    for idx, sec in enumerate(sections, start=1):
        renumbered.append(ExtractedSection(
            number=str(idx),
            title=sec.title,
            content=sec.content,
            start_line=sec.start_line,
            end_line=sec.end_line,
            is_complete=sec.is_complete,
        ))
    logger.info("Renumbered %d sections sequentially", len(renumbered))
    return renumbered


# ──────────────────────────────────────────────
# 5. Orchestrator
# ──────────────────────────────────────────────

def extract_all_sections(
    pdf_path: Path,
    model_name: str = "qwen2.5:1.5b",
    window_size: int = 80,
    overlap: int = 20,
) -> list[ExtractedSection]:
    """
    End-to-end extraction pipeline.

    Tries rule-based heading detection first (fast, accurate, no LLM).
    Falls back to the multi-agent sliding-window LLM pipeline when the
    document lacks recognisable structural markers.
    """
    doc_lines = prepare_document(pdf_path)

    # ── Rule-based fast path ──
    sections = detect_rule_based_sections(doc_lines)
    if len(sections) >= 2:
        logger.info("Using rule-based sections (%d found) — skipping LLM pipeline", len(sections))
        return sections

    logger.info("Rule-based detection insufficient, falling back to LLM pipeline")

    # ── LLM fallback ──
    llm = ChatOllama(model=model_name, temperature=0)
    windows = list(build_windows(doc_lines, window_size, overlap))
    logger.info("Processing %d windows (size=%d, overlap=%d)", len(windows), window_size, overlap)

    all_sections: list[ExtractedSection] = []
    carry_over: IncompleteSection | None = None
    last_section_num = 0  # Global section counter

    for idx, (chunk_text, start, end) in enumerate(windows):
        logger.info("== Window %d/%d (lines %d-%d) ==", idx + 1, len(windows), start, end)
        try:
            result = extract_sections_from_chunk(
                llm, chunk_text, doc_lines,  # Pass full document for content extraction
                start, end, last_section_num, carry_over
            )
        except Exception:
            logger.exception("Failed window %d (lines %d-%d)", idx + 1, start, end)
            carry_over = None
            continue

        all_sections.extend(result.sections)

        # Track section count from actual unique start_lines seen so far,
        # NOT from LLM-assigned numbers (which can hallucinate large jumps).
        last_section_num = len({s.start_line for s in all_sections})
        
        if result.has_incomplete_section and result.incomplete_section:
            carry_over = result.incomplete_section
        else:
            carry_over = None

    all_sections = _dedup_sections(all_sections)
    all_sections = _remove_overlapping_sections(all_sections)  # Remove nested subsections
    all_sections = _renumber_sections(all_sections)  # Ensure sequential numbering
    return all_sections


# ──────────────────────────────────────────────
# 6. Serialisation
# ──────────────────────────────────────────────

def save_sections_json(sections: list[ExtractedSection], output_path: Path) -> None:
    """Persist extracted sections to a JSON file."""
    data = [s.model_dump() for s in sections]
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    logger.info("Saved %d sections to %s", len(data), output_path)


# ──────────────────────────────────────────────
# 7. Master List Generation
# ──────────────────────────────────────────────

def generate_master_list(
    sections: list[ExtractedSection],
    model_name: str = "qwen2.5:1.5b",
) -> list[dict]:
    """
    Generate a master list with summaries for all sections.
    
    Args:
        sections: List of extracted sections
        model_name: LLM model to use for summarization
    
    Returns:
        List of dicts with section metadata and summaries
    """
    from agents.summarizer_agent import run_summarizer
    from models import SectionSummary
    
    llm = ChatOllama(model=model_name, temperature=0)
    master_list = []
    
    logger.info("Generating master list for %d sections", len(sections))
    
    for section in sections:
        try:
            summary = run_summarizer(llm, section)
            
            master_list.append({
                "number": section.number,
                "title": section.title,
                "summary": summary,
                "start_line": section.start_line,
                "end_line": section.end_line,
            })
        except Exception:
            logger.exception("Failed to summarize section %s: %s", section.number, section.title)
            # Add without summary on failure
            master_list.append({
                "number": section.number,
                "title": section.title,
                "summary": "[Summary generation failed]",
                "start_line": section.start_line,
                "end_line": section.end_line,
            })
    
    logger.info("Master list generated with %d entries", len(master_list))
    return master_list


def save_master_list(master_list: list[dict], output_path: Path) -> None:
    """Save the master list to a JSON file."""
    output_path.write_text(json.dumps(master_list, indent=2, ensure_ascii=False))
    logger.info("Saved master list to %s", output_path)

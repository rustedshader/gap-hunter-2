"""
Extractor Agent — identifies and extracts sections from a document chunk.

Takes a line-numbered document chunk and produces a structured list of
all policy sections found, with their titles, content, and line numbers.
"""

from __future__ import annotations

import logging

from langchain_community.chat_models import ChatLlamaCpp

from models import IncompleteSection
from agents.schemas import ExtractionResult
from prompts.extractor_prompt import EXTRACTOR_SYSTEM

logger = logging.getLogger(__name__)


def run_extractor(
    llm: ChatLlamaCpp,
    chunk_text: str,
    start_line: int,
    end_line: int,
    last_section_num: int = 0,
    carry_over: IncompleteSection | None = None,
) -> ExtractionResult:
    """Run the extractor agent on a document chunk."""
    extractor = llm.with_structured_output(ExtractionResult)

    next_section_num = last_section_num + 1
    prompt = f"Identify all MAIN section boundaries in this document chunk (lines {start_line} to {end_line}):\n\n"
    prompt += f"CRITICAL: Start numbering from section {next_section_num}. Number sections sequentially: {next_section_num}, {next_section_num + 1}, {next_section_num + 2}, etc.\n"
    prompt += f"Look for structural patterns (##, ALL CAPS, numbered headings) that divide the document into main sections.\n"
    prompt += f"IGNORE sub-bullets and numbered paragraphs within sections - those are content, not section boundaries.\n\n"
    
    if carry_over:
        prompt += (
            f"IMPORTANT: Section {carry_over.number} \"{carry_over.title}\" was incomplete "
            f"in the previous chunk. It started at line {carry_over.original_start_line}.\n"
            f"Find where it ends in this chunk. This section keeps its number {carry_over.number}.\n"
            f"New sections after it should start from {next_section_num}.\n\n"
        )
    
    prompt += f"<document>\n{chunk_text}\n</document>\n\nIdentify EVERY section boundary. Number them starting from {next_section_num}."

    logger.info("Agent 1 (Extractor): Processing lines %d-%d (start numbering from %d)", start_line, end_line, next_section_num)
    result: ExtractionResult = extractor.invoke([
        {"role": "system", "content": EXTRACTOR_SYSTEM},
        {"role": "user", "content": prompt},
    ])
    logger.info("  -> extracted %d sections", len(result.sections))
    return result

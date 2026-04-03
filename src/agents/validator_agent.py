"""
Validator Agent — checks an extraction against the original document.

Compares extracted sections with the source text to find missing sections,
wrong content, merged sections, or incorrect line boundaries.
"""

from __future__ import annotations

import logging

from langchain_ollama import ChatOllama

from agents.schemas import ExtractionResult, ValidationResult
from prompts.validator_prompt import VALIDATOR_SYSTEM

logger = logging.getLogger(__name__)


def format_extraction_for_review(extraction: ExtractionResult) -> str:
    """Format extracted section boundaries as readable text for review."""
    lines = []
    for s in extraction.sections:
        lines.append(
            f'Section {s.section_num}: "{s.title}" (lines {s.start_line}-{s.end_line})'
        )
    return "\n".join(lines)


def run_validator(
    llm: ChatOllama,
    chunk_text: str,
    extraction: ExtractionResult,
) -> ValidationResult:
    """Run the validator agent to check an extraction."""
    validator = llm.with_structured_output(ValidationResult)

    extraction_summary = format_extraction_for_review(extraction)
    prompt = (
        f"Here is the original document:\n\n"
        f"<document>\n{chunk_text}\n</document>\n\n"
        f"Here are the identified section boundaries:\n\n{extraction_summary}\n\n"
        f"Are these boundaries correct and complete? Check for missing sections, "
        f"wrong boundaries, or incorrect titles. Do NOT validate content."
    )

    logger.info("  Agent 2 (Validator): Checking extraction")
    result: ValidationResult = validator.invoke([
        {"role": "system", "content": VALIDATOR_SYSTEM},
        {"role": "user", "content": prompt},
    ])
    return result

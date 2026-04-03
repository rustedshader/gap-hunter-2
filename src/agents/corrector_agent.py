"""
Corrector Agent — fixes errors flagged by the validator.

Takes the original document, the current extraction, and a list of
specific issues, then produces a corrected extraction.
"""

from __future__ import annotations

import logging

from langchain_ollama import ChatOllama

from agents.schemas import ExtractionResult, ValidationResult
from agents.validator_agent import format_extraction_for_review
from prompts.corrector_prompt import CORRECTOR_SYSTEM

logger = logging.getLogger(__name__)


def run_corrector(
    llm: ChatOllama,
    chunk_text: str,
    extraction: ExtractionResult,
    validation: ValidationResult,
) -> ExtractionResult:
    """Run the corrector agent to fix issues in boundary identification."""
    corrector = llm.with_structured_output(ExtractionResult)

    extraction_summary = format_extraction_for_review(extraction)
    issues_text = "\n".join(f"  - {issue}" for issue in validation.issues)
    missing_text = "\n".join(f"  - {m}" for m in validation.missing_sections)

    prompt = (
        f"The following boundary identification has errors. Fix them.\n\n"
        f"Original document:\n<document>\n{chunk_text}\n</document>\n\n"
        f"Current boundaries:\n{extraction_summary}\n\n"
        f"Issues found:\n{issues_text}\n"
    )
    if validation.missing_sections:
        prompt += f"\nMissing sections:\n{missing_text}\n"
    prompt += "\nProduce corrected section boundaries for ALL sections. Do NOT generate content."

    logger.info("  Agent 3 (Corrector): Fixing issues")
    result: ExtractionResult = corrector.invoke([
        {"role": "system", "content": CORRECTOR_SYSTEM},
        {"role": "user", "content": prompt},
    ])
    logger.info("  -> corrected to %d sections", len(result.sections))
    return result

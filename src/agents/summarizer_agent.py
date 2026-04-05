"""
Summarizer Agent — generates concise summaries for policy sections.

Takes extracted sections and produces a master list with:
- Section number and title
- Brief summary of key points
- Main requirements or obligations
"""

from __future__ import annotations

import logging

from langchain_community.chat_models import ChatLlamaCpp

from models import ExtractedSection
from agents.schemas import SummarizationResult
from prompts.summarizer_prompt import SUMMARIZER_SYSTEM

logger = logging.getLogger(__name__)


def run_summarizer(
    llm: ChatLlamaCpp,
    section: ExtractedSection,
) -> str | None:
    """Run the summarizer agent on a single section."""
    summarizer = llm.with_structured_output(SummarizationResult)

    prompt = f"""Summarize this policy section concisely:

Section {section.number}: {section.title}

<content>
{section.content}
</content>

IMPORTANT: If this section is just a heading/title with no substantive content (e.g., empty, just images, or table of contents), return null for the summary.

Otherwise, provide:
1. A brief 2-3 sentence summary of the main purpose
2. Key requirements or obligations (bullet points)
3. Any critical compliance points

Keep it concise and actionable."""

    logger.info("Summarizing section %s: %s", section.number, section.title)
    result: SummarizationResult = summarizer.invoke([
        {"role": "system", "content": SUMMARIZER_SYSTEM},
        {"role": "user", "content": prompt},
    ])
    
    if result.summary:
        logger.info("  -> summary generated (%d chars)", len(result.summary))
    else:
        logger.info("  -> no summary needed (heading/minimal content)")
    
    return result.summary

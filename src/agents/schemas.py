"""
Pydantic schemas used by the multi-agent extraction system.

These are the structured output schemas that agents fill in,
separate from the pipeline models in models.py.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SectionExtraction(BaseModel):
    """A single extracted section boundary (content extracted separately from source)."""
    section_num: int = Field(
        description="The section number from the document as an integer. For '1. Purpose' this is 1. For '2. Scope' this is 2.",
        examples=[1, 2, 3, 4, 5],
    )
    title: str = Field(
        description="Short heading text only, not body content.",
        examples=["Purpose", "Scope", "Roles and Responsibilities"],
    )
    start_line: int = Field(
        description="LINE number where section heading appears.", examples=[1, 4, 8],
    )
    end_line: int = Field(
        description="LINE number of last line of this section (before next section starts).", examples=[3, 7, 9],
    )


class ExtractionResult(BaseModel):
    """Result from the extractor/corrector agents."""
    sections: list[SectionExtraction] = Field(
        default_factory=list,
        description="All sections found in order.",
    )


class ValidationResult(BaseModel):
    """Result from the validator agent."""
    is_correct: bool = Field(
        description="true if the extraction is complete and accurate, false if there are issues.",
    )
    issues: list[str] = Field(
        default_factory=list,
        description="List of specific issues found. Empty if is_correct is true.",
    )
    missing_sections: list[str] = Field(
        default_factory=list,
        description='Section descriptions that were missed, e.g. "Section 5 Enforcement on LINE 9".',
    )


class SummarizationResult(BaseModel):
    """Result from the summarizer agent."""
    summary: str | None = Field(
        description="Concise summary of the section including main purpose, key requirements, and compliance points. Return null if the section is just a heading/title with no substantive content to summarize.",
    )

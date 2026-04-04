"""
Pydantic models for structured section extraction from policy documents.

Kept deliberately simple so small LLMs (qwen2.5:1.5b) can populate
every field correctly via structured output / function calling.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExtractedSection(BaseModel):
    """A single policy section found in a document chunk."""

    number: str = Field(
        description='The section number from the document, like "1", "2", "3.1", "A.1". Use "N/A" if no number.',
        examples=["1", "2", "3.1", "N/A"],
    )
    title: str = Field(
        description="The heading text of the section, copied exactly from the document.",
        examples=["Purpose", "Scope", "Roles and Responsibilities"],
    )
    content: str = Field(
        description="The body text under this heading, copied verbatim from the document.",
    )
    start_line: int = Field(
        description="The LINE number where this section heading appears. Read it from the LINE prefix.",
        examples=[1, 5, 12],
    )
    end_line: int | None = Field(
        default=None,
        description="The LINE number of the last line of this section in the chunk. null if cut off.",
        examples=[4, 11, None],
    )
    is_complete: bool = Field(
        default=True,
        description="true if the section ends within this chunk. false if it continues beyond.",
    )


class IncompleteSection(BaseModel):
    """Carry-over info for a section that spans across chunks."""

    number: str = Field(description='The section number, e.g. "3".', examples=["3"])
    title: str = Field(description="The section title.")
    partial_content: str = Field(description="Content extracted so far.")
    original_start_line: int = Field(description="Line where the section started.", examples=[5])


class ChunkResult(BaseModel):
    """Result from extracting one document chunk."""

    sections: list[ExtractedSection] = Field(
        default_factory=list,
        description="All sections found in this chunk.",
    )
    has_incomplete_section: bool = Field(
        default=False,
        description="true if the last section continues beyond this chunk.",
    )
    incomplete_section: IncompleteSection | None = Field(
        default=None,
        description="Details of the incomplete section, if any. null otherwise.",
    )


class SectionSummary(BaseModel):
    """Summary of a policy section for master list."""

    number: str = Field(description='Section number like "1", "2", "3.1"')
    title: str = Field(description="Section heading")
    summary: str = Field(description="Concise summary with key requirements")
    start_line: int = Field(description="Starting line number")
    end_line: int = Field(description="Ending line number")

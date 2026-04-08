"""
Unit tests for Pydantic models.

Tests round-trip serialization for ExtractedSection, SubcategoryAssessment,
ChunkResult, and other models.
"""

import pytest
from hypothesis import given
from tests.utils.generators import st_extracted_section, st_assessment

from src.models import (
    ExtractedSection,
    IncompleteSection,
    ChunkResult,
    SectionSummary,
)
from src.agents.nist_gap_agents import SubcategoryAssessment


# ============================================================================
# Unit Tests for ExtractedSection
# ============================================================================

@pytest.mark.unit
def test_extracted_section_basic():
    """Test basic ExtractedSection creation and serialization."""
    section = ExtractedSection(
        number="1",
        title="Purpose",
        content="This policy establishes...",
        start_line=1,
        end_line=10,
        is_complete=True
    )
    
    assert section.number == "1"
    assert section.title == "Purpose"
    assert section.start_line == 1
    assert section.end_line == 10
    assert section.is_complete is True


@pytest.mark.unit
def test_extracted_section_round_trip():
    """Test ExtractedSection serialization round-trip."""
    original = ExtractedSection(
        number="2.1",
        title="Scope and Applicability",
        content="This section defines the scope of the policy.",
        start_line=15,
        end_line=25,
        is_complete=True
    )
    
    # Serialize
    data = original.model_dump()
    
    # Deserialize
    restored = ExtractedSection.model_validate(data)
    
    # Verify equivalence
    assert restored.number == original.number
    assert restored.title == original.title
    assert restored.content == original.content
    assert restored.start_line == original.start_line
    assert restored.end_line == original.end_line
    assert restored.is_complete == original.is_complete


@pytest.mark.unit
def test_extracted_section_incomplete():
    """Test ExtractedSection with incomplete section (end_line=None)."""
    section = ExtractedSection(
        number="3",
        title="Definitions",
        content="Partial content...",
        start_line=30,
        end_line=None,
        is_complete=False
    )
    
    assert section.end_line is None
    assert section.is_complete is False
    
    # Round-trip
    data = section.model_dump()
    restored = ExtractedSection.model_validate(data)
    assert restored.end_line is None
    assert restored.is_complete is False


# ============================================================================
# Unit Tests for IncompleteSection
# ============================================================================

@pytest.mark.unit
def test_incomplete_section_round_trip():
    """Test IncompleteSection serialization round-trip."""
    original = IncompleteSection(
        number="4",
        title="Roles and Responsibilities",
        partial_content="The CISO is responsible for...",
        original_start_line=50
    )
    
    # Serialize
    data = original.model_dump()
    
    # Deserialize
    restored = IncompleteSection.model_validate(data)
    
    # Verify equivalence
    assert restored.number == original.number
    assert restored.title == original.title
    assert restored.partial_content == original.partial_content
    assert restored.original_start_line == original.original_start_line


# ============================================================================
# Unit Tests for ChunkResult
# ============================================================================

@pytest.mark.unit
def test_chunk_result_complete():
    """Test ChunkResult with complete sections."""
    sections = [
        ExtractedSection(
            number="1", title="Purpose", content="Content 1",
            start_line=1, end_line=10, is_complete=True
        ),
        ExtractedSection(
            number="2", title="Scope", content="Content 2",
            start_line=11, end_line=20, is_complete=True
        ),
    ]
    
    chunk = ChunkResult(
        sections=sections,
        has_incomplete_section=False,
        incomplete_section=None
    )
    
    assert len(chunk.sections) == 2
    assert chunk.has_incomplete_section is False
    assert chunk.incomplete_section is None


@pytest.mark.unit
def test_chunk_result_with_incomplete():
    """Test ChunkResult with incomplete section."""
    sections = [
        ExtractedSection(
            number="1", title="Purpose", content="Content 1",
            start_line=1, end_line=10, is_complete=True
        ),
    ]
    
    incomplete = IncompleteSection(
        number="2",
        title="Scope",
        partial_content="Partial...",
        original_start_line=11
    )
    
    chunk = ChunkResult(
        sections=sections,
        has_incomplete_section=True,
        incomplete_section=incomplete
    )
    
    assert chunk.has_incomplete_section is True
    assert chunk.incomplete_section is not None
    assert chunk.incomplete_section.number == "2"


@pytest.mark.unit
def test_chunk_result_round_trip():
    """Test ChunkResult serialization round-trip."""
    sections = [
        ExtractedSection(
            number="1", title="Purpose", content="Content 1",
            start_line=1, end_line=10, is_complete=True
        ),
    ]
    
    incomplete = IncompleteSection(
        number="2",
        title="Scope",
        partial_content="Partial...",
        original_start_line=11
    )
    
    original = ChunkResult(
        sections=sections,
        has_incomplete_section=True,
        incomplete_section=incomplete
    )
    
    # Serialize
    data = original.model_dump()
    
    # Deserialize
    restored = ChunkResult.model_validate(data)
    
    # Verify equivalence
    assert len(restored.sections) == len(original.sections)
    assert restored.sections[0].number == original.sections[0].number
    assert restored.has_incomplete_section == original.has_incomplete_section
    assert restored.incomplete_section.number == original.incomplete_section.number


# ============================================================================
# Unit Tests for SectionSummary
# ============================================================================

@pytest.mark.unit
def test_section_summary_round_trip():
    """Test SectionSummary serialization round-trip."""
    original = SectionSummary(
        number="1",
        title="Purpose",
        summary="This section establishes the purpose of the policy.",
        start_line=1,
        end_line=10
    )
    
    # Serialize
    data = original.model_dump()
    
    # Deserialize
    restored = SectionSummary.model_validate(data)
    
    # Verify equivalence
    assert restored.number == original.number
    assert restored.title == original.title
    assert restored.summary == original.summary
    assert restored.start_line == original.start_line
    assert restored.end_line == original.end_line


# ============================================================================
# Unit Tests for SubcategoryAssessment
# ============================================================================

@pytest.mark.unit
def test_subcategory_assessment_round_trip():
    """Test SubcategoryAssessment serialization round-trip."""
    original = SubcategoryAssessment(
        subcategory_id="GV.OC-01",
        title="Organizational Context",
        status="Addressed",
        evidence="Section 2 states that this policy applies to all employees.",
        gap="None - fully addressed",
        recommendation="No action needed"
    )
    
    # Serialize
    data = original.model_dump()
    
    # Deserialize
    restored = SubcategoryAssessment.model_validate(data)
    
    # Verify equivalence
    assert restored.subcategory_id == original.subcategory_id
    assert restored.title == original.title
    assert restored.status == original.status
    assert restored.evidence == original.evidence
    assert restored.gap == original.gap
    assert restored.recommendation == original.recommendation


@pytest.mark.unit
def test_subcategory_assessment_all_statuses():
    """Test SubcategoryAssessment with all possible status values."""
    statuses = ["Addressed", "Partially Addressed", "Not Addressed", "Out of Scope"]
    
    for status in statuses:
        assessment = SubcategoryAssessment(
            subcategory_id="GV.OC-01",
            title="Test",
            status=status,
            evidence="Test evidence",
            gap="Test gap",
            recommendation="Test recommendation"
        )
        
        # Round-trip
        data = assessment.model_dump()
        restored = SubcategoryAssessment.model_validate(data)
        assert restored.status == status


# ============================================================================
# Property-Based Test for Pydantic Model Serialization
# ============================================================================

@pytest.mark.unit
@given(st_extracted_section())
def test_pydantic_model_serialization_round_trip_extracted_section(section):
    """
    Feature: research-based-testing, Property 7: Pydantic Model Serialization Round-Trip
    
    **Validates: Requirements 1.10, 12.1, 12.2, 12.3, 12.4, 12.5**
    
    For any valid instance of ExtractedSection, serializing via model_dump()
    and deserializing via model_validate() should produce an equivalent object.
    """
    # Serialize
    data = section.model_dump()
    
    # Deserialize
    restored = ExtractedSection.model_validate(data)
    
    # Verify equivalence
    assert restored.number == section.number
    assert restored.title == section.title
    assert restored.content == section.content
    assert restored.start_line == section.start_line
    assert restored.end_line == section.end_line
    assert restored.is_complete == section.is_complete
    
    # Verify complete round-trip equivalence
    assert restored.model_dump() == section.model_dump()


@pytest.mark.unit
@given(st_assessment())
def test_pydantic_model_serialization_round_trip_assessment(assessment):
    """
    Feature: research-based-testing, Property 7: Pydantic Model Serialization Round-Trip
    
    **Validates: Requirements 1.10, 12.1, 12.2, 12.3, 12.4, 12.5**
    
    For any valid instance of SubcategoryAssessment, serializing via model_dump()
    and deserializing via model_validate() should produce an equivalent object.
    """
    # Serialize
    data = assessment.model_dump()
    
    # Deserialize
    restored = SubcategoryAssessment.model_validate(data)
    
    # Verify equivalence
    assert restored.subcategory_id == assessment.subcategory_id
    assert restored.title == assessment.title
    assert restored.status == assessment.status
    assert restored.evidence == assessment.evidence
    assert restored.gap == assessment.gap
    assert restored.recommendation == assessment.recommendation
    
    # Verify complete round-trip equivalence
    assert restored.model_dump() == assessment.model_dump()


@pytest.mark.unit
@given(st_extracted_section())
def test_chunk_result_property_round_trip(section):
    """
    Feature: research-based-testing, Property 7: Pydantic Model Serialization Round-Trip
    
    **Validates: Requirements 12.3**
    
    For any valid ChunkResult instance, serialization round-trip should
    preserve all fields including complete and incomplete sections.
    """
    # Create ChunkResult with the generated section
    incomplete = IncompleteSection(
        number=section.number,
        title=section.title,
        partial_content=section.content[:50],
        original_start_line=section.start_line
    )
    
    original = ChunkResult(
        sections=[section],
        has_incomplete_section=True,
        incomplete_section=incomplete
    )
    
    # Serialize
    data = original.model_dump()
    
    # Deserialize
    restored = ChunkResult.model_validate(data)
    
    # Verify equivalence
    assert len(restored.sections) == len(original.sections)
    assert restored.sections[0].model_dump() == original.sections[0].model_dump()
    assert restored.has_incomplete_section == original.has_incomplete_section
    if original.incomplete_section:
        assert restored.incomplete_section.model_dump() == original.incomplete_section.model_dump()

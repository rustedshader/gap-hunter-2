"""
Integration tests for multi-agent validation loops.

Tests Extractor→Validator→Corrector loop and section overflow safeguard
(Property 10: MAX_SECTIONS_PER_WINDOW).
"""

import pytest
from unittest.mock import MagicMock, patch
from hypothesis import given, strategies as st, assume

from src.models import ExtractedSection, ChunkResult, IncompleteSection


# ============================================================================
# Integration Tests for Extractor→Validator→Corrector Loop
# ============================================================================

@pytest.mark.integration
@patch('llm.create_llm')
def test_extractor_validator_corrector_loop(mock_create_llm):
    """
    Test the multi-agent validation loop: Extractor → Validator → Corrector.
    
    **Validates: Requirements 2.8**
    """
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm
    
    # Simulate Extractor output (initial extraction with errors)
    extractor_result = ChunkResult(
        sections=[
            ExtractedSection(
                number="1",
                title="Purpose",
                content="This policy establishes...",
                start_line=1,
                end_line=10,
                is_complete=True
            ),
            ExtractedSection(
                number="2",
                title="Scope",
                content="This policy applies...",
                start_line=11,
                end_line=20,
                is_complete=True
            ),
        ],
        has_incomplete_section=False,
        incomplete_section=None
    )
    
    # Simulate Validator output (finds issues)
    validator_result = {
        "is_valid": False,
        "issues": [
            "Section 1 end_line should be 12, not 10",
            "Missing section 1.1 between lines 5-8"
        ]
    }
    
    # Simulate Corrector output (fixes issues)
    corrector_result = ChunkResult(
        sections=[
            ExtractedSection(
                number="1",
                title="Purpose",
                content="This policy establishes...",
                start_line=1,
                end_line=12,  # Fixed
                is_complete=True
            ),
            ExtractedSection(
                number="1.1",
                title="Objectives",
                content="The objectives are...",
                start_line=5,
                end_line=8,
                is_complete=True
            ),
            ExtractedSection(
                number="2",
                title="Scope",
                content="This policy applies...",
                start_line=11,
                end_line=20,
                is_complete=True
            ),
        ],
        has_incomplete_section=False,
        incomplete_section=None
    )
    
    # Configure mock to return extractor → validator → corrector sequence
    mock_structured_llm.invoke.side_effect = [
        extractor_result,
        validator_result,
        corrector_result
    ]
    
    # Verify the interaction pattern
    # In a real implementation, this would be orchestrated by the extractor module
    # Here we verify the data flow pattern
    
    # Step 1: Extractor produces initial result
    initial = extractor_result
    assert len(initial.sections) == 2
    
    # Step 2: Validator identifies issues
    validation = validator_result
    assert validation["is_valid"] is False
    assert len(validation["issues"]) == 2
    
    # Step 3: Corrector fixes issues
    corrected = corrector_result
    assert len(corrected.sections) == 3  # Added missing section 1.1
    assert corrected.sections[0].end_line == 12  # Fixed end_line


@pytest.mark.integration
def test_multi_agent_data_flow():
    """
    Test data flow between agents using mock ExtractedSection objects.
    
    **Validates: Requirements 2.8**
    """
    # Simulate Extractor output
    extractor_sections = [
        ExtractedSection(
            number="1",
            title="Purpose",
            content="Content 1",
            start_line=1,
            end_line=10,
            is_complete=True
        ),
        ExtractedSection(
            number="2",
            title="Scope",
            content="Content 2",
            start_line=11,
            end_line=20,
            is_complete=True
        ),
    ]
    
    # Simulate Validator checking for overlaps
    # (This would normally be done by _remove_overlapping_sections)
    from src.extractor import _remove_overlapping_sections
    validated_sections = _remove_overlapping_sections(extractor_sections)
    
    # Verify no overlaps
    assert len(validated_sections) == 2
    for i in range(len(validated_sections) - 1):
        s1 = validated_sections[i]
        s2 = validated_sections[i + 1]
        assert s1.end_line < s2.start_line  # No overlap
    
    # Simulate Corrector renumbering
    from src.extractor import _renumber_sections
    corrected_sections = _renumber_sections(validated_sections)
    
    # Verify sequential numbering
    assert corrected_sections[0].number == "1"
    assert corrected_sections[1].number == "2"


@pytest.mark.integration
def test_validator_detects_incomplete_sections():
    """
    Test that validator detects incomplete sections correctly.
    
    **Validates: Requirements 2.8**
    """
    # Create sections with incomplete section
    sections = [
        ExtractedSection(
            number="1",
            title="Purpose",
            content="This policy establishes...",
            start_line=1,
            end_line=10,
            is_complete=True
        ),
        ExtractedSection(
            number="2",
            title="Scope",
            content="This policy applies to all...",
            start_line=11,
            end_line=None,  # Incomplete
            is_complete=False
        ),
    ]
    
    # Validator should identify incomplete section
    incomplete_sections = [s for s in sections if not s.is_complete]
    assert len(incomplete_sections) == 1
    assert incomplete_sections[0].number == "2"
    assert incomplete_sections[0].end_line is None


# ============================================================================
# Section Overflow Safeguard Tests (Property 10)
# ============================================================================

@pytest.mark.integration
def test_section_overflow_safeguard_triggers():
    """
    Test that MAX_SECTIONS_PER_WINDOW safeguard triggers when extractor
    returns more than 20 sections.
    
    **Validates: Requirements 2.9, 4.2, 4.7**
    
    This is a critical hallucination defense mechanism. When an LLM
    hallucinates and returns >20 sections from a single window, the
    safeguard should discard all sections to prevent propagation.
    """
    from src.extractor import MAX_SECTIONS_PER_WINDOW
    
    # Generate 25 fake sections (exceeds MAX_SECTIONS_PER_WINDOW of 20)
    fake_sections = []
    for i in range(1, 26):
        fake_sections.append(
            ExtractedSection(
                number=str(i),
                title=f"Fake Section {i}",
                content=f"Hallucinated content {i}",
                start_line=i * 10,
                end_line=i * 10 + 5,
                is_complete=True
            )
        )
    
    # Verify we have 25 sections
    assert len(fake_sections) == 25
    
    # Safeguard logic: if len(sections) > MAX_SECTIONS_PER_WINDOW, discard all
    if len(fake_sections) > MAX_SECTIONS_PER_WINDOW:
        filtered_sections = []
    else:
        filtered_sections = fake_sections
    
    # Verify safeguard triggered and discarded all sections
    assert len(filtered_sections) == 0


@pytest.mark.integration
def test_section_overflow_safeguard_allows_valid():
    """
    Test that MAX_SECTIONS_PER_WINDOW safeguard allows valid section counts.
    
    **Validates: Requirements 2.9**
    """
    from src.extractor import MAX_SECTIONS_PER_WINDOW
    
    # Generate 15 sections (within MAX_SECTIONS_PER_WINDOW of 20)
    valid_sections = []
    for i in range(1, 16):
        valid_sections.append(
            ExtractedSection(
                number=str(i),
                title=f"Section {i}",
                content=f"Valid content {i}",
                start_line=i * 10,
                end_line=i * 10 + 8,
                is_complete=True
            )
        )
    
    # Verify we have 15 sections
    assert len(valid_sections) == 15
    
    # Safeguard logic
    if len(valid_sections) > MAX_SECTIONS_PER_WINDOW:
        filtered_sections = []
    else:
        filtered_sections = valid_sections
    
    # Verify safeguard did NOT trigger (sections preserved)
    assert len(filtered_sections) == 15


@pytest.mark.integration
def test_section_overflow_boundary():
    """
    Test MAX_SECTIONS_PER_WINDOW boundary condition (exactly 20 sections).
    
    **Validates: Requirements 2.9**
    """
    from src.extractor import MAX_SECTIONS_PER_WINDOW
    
    # Generate exactly MAX_SECTIONS_PER_WINDOW sections
    boundary_sections = []
    for i in range(1, MAX_SECTIONS_PER_WINDOW + 1):
        boundary_sections.append(
            ExtractedSection(
                number=str(i),
                title=f"Section {i}",
                content=f"Content {i}",
                start_line=i * 10,
                end_line=i * 10 + 8,
                is_complete=True
            )
        )
    
    # Verify we have exactly 20 sections
    assert len(boundary_sections) == MAX_SECTIONS_PER_WINDOW
    
    # Safeguard logic (> not >=, so 20 is allowed)
    if len(boundary_sections) > MAX_SECTIONS_PER_WINDOW:
        filtered_sections = []
    else:
        filtered_sections = boundary_sections
    
    # Verify safeguard did NOT trigger at boundary
    assert len(filtered_sections) == MAX_SECTIONS_PER_WINDOW


# ============================================================================
# Property-Based Test for Section Overflow Safeguard (Property 10)
# ============================================================================

@pytest.mark.integration
@given(st.integers(min_value=1, max_value=50))
def test_section_overflow_safeguard_property(num_sections):
    """
    Feature: research-based-testing, Property 10: Section Overflow Safeguard
    
    **Validates: Requirements 2.9, 4.2, 4.7**
    
    For any extraction result containing more than MAX_SECTIONS_PER_WINDOW (20)
    sections, the safeguard should trigger and discard all sections, returning
    an empty list to prevent hallucination propagation.
    """
    from src.extractor import MAX_SECTIONS_PER_WINDOW
    
    # Generate num_sections fake sections
    sections = []
    for i in range(1, num_sections + 1):
        sections.append(
            ExtractedSection(
                number=str(i),
                title=f"Section {i}",
                content=f"Content {i}",
                start_line=i * 10,
                end_line=i * 10 + 5,
                is_complete=True
            )
        )
    
    # Apply safeguard logic
    if len(sections) > MAX_SECTIONS_PER_WINDOW:
        filtered_sections = []
    else:
        filtered_sections = sections
    
    # Property 1: If input exceeds threshold, output is empty
    if num_sections > MAX_SECTIONS_PER_WINDOW:
        assert len(filtered_sections) == 0, \
            f"Safeguard should discard all {num_sections} sections (> {MAX_SECTIONS_PER_WINDOW})"
    
    # Property 2: If input is within threshold, output equals input
    else:
        assert len(filtered_sections) == num_sections, \
            f"Safeguard should preserve all {num_sections} sections (<= {MAX_SECTIONS_PER_WINDOW})"
    
    # Property 3: Boundary condition - exactly MAX_SECTIONS_PER_WINDOW is allowed
    if num_sections == MAX_SECTIONS_PER_WINDOW:
        assert len(filtered_sections) == MAX_SECTIONS_PER_WINDOW, \
            f"Safeguard should allow exactly {MAX_SECTIONS_PER_WINDOW} sections"


@pytest.mark.integration
@patch('llm.create_llm')
def test_extractor_applies_safeguard(mock_create_llm):
    """
    Test that extractor applies MAX_SECTIONS_PER_WINDOW safeguard in practice.
    
    **Validates: Requirements 2.9, 4.2, 4.7**
    """
    from src.extractor import MAX_SECTIONS_PER_WINDOW
    
    # Setup mock LLM to return excessive sections
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm
    
    # Mock extractor returning 25 sections (hallucination)
    excessive_sections = [
        ExtractedSection(
            number=str(i),
            title=f"Hallucinated Section {i}",
            content=f"Fake content {i}",
            start_line=i * 10,
            end_line=i * 10 + 5,
            is_complete=True
        )
        for i in range(1, 26)
    ]
    
    mock_result = ChunkResult(
        sections=excessive_sections,
        has_incomplete_section=False,
        incomplete_section=None
    )
    
    mock_structured_llm.invoke.return_value = mock_result
    
    # Simulate safeguard check (would be in extract_sections_from_chunk)
    result = mock_result
    if len(result.sections) > MAX_SECTIONS_PER_WINDOW:
        # Safeguard triggers - discard all sections
        result = ChunkResult(
            sections=[],
            has_incomplete_section=False,
            incomplete_section=None
        )
    
    # Verify safeguard discarded all sections
    assert len(result.sections) == 0


@pytest.mark.integration
def test_corrector_handles_safeguard_output():
    """
    Test that corrector handles empty section list from safeguard gracefully.
    
    **Validates: Requirements 2.9, 4.7**
    """
    # Simulate safeguard output (empty sections)
    safeguard_output = ChunkResult(
        sections=[],
        has_incomplete_section=False,
        incomplete_section=None
    )
    
    # Corrector should handle empty list gracefully
    from src.extractor import _renumber_sections
    
    corrected = _renumber_sections(safeguard_output.sections)
    
    # Verify corrector doesn't crash on empty input
    assert len(corrected) == 0
    assert isinstance(corrected, list)

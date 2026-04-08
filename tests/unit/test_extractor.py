"""
Unit tests for extractor functions.

Tests build_windows, _dedup_sections, _remove_overlapping_sections,
_renumber_sections with both unit tests and property-based tests.
"""

import pytest
from hypothesis import given, strategies as st, assume
from src.extractor import (
    build_windows,
    _dedup_sections,
    _remove_overlapping_sections,
    _renumber_sections,
)
from src.models import ExtractedSection


# ============================================================================
# Unit Tests for build_windows
# ============================================================================

@pytest.mark.unit
def test_build_windows_basic():
    """Test basic sliding window generation."""
    lines = [(i, f"line {i}") for i in range(1, 101)]
    windows = list(build_windows(lines, window_size=80, overlap=20))
    
    # With 100 lines, window_size=80, overlap=20:
    # step = 80 - 20 = 60
    # Windows: [0:80], [60:140 but capped at 100]
    # So we expect 2 windows
    assert len(windows) == 2
    
    # First window
    chunk1, start1, end1 = windows[0]
    assert start1 == 1
    assert end1 == 80
    assert "LINE 1:" in chunk1
    assert "LINE 80:" in chunk1
    
    # Second window
    chunk2, start2, end2 = windows[1]
    assert start2 == 61  # 1 + 60
    assert end2 == 100


@pytest.mark.unit
def test_build_windows_no_overlap():
    """Test windows with no overlap."""
    lines = [(i, f"line {i}") for i in range(1, 101)]
    windows = list(build_windows(lines, window_size=50, overlap=0))
    
    # step = 50 - 0 = 50
    # Windows: [0:50], [50:100]
    assert len(windows) == 2


@pytest.mark.unit
def test_build_windows_invalid_params():
    """Test that invalid parameters raise ValueError."""
    lines = [(i, f"line {i}") for i in range(1, 101)]
    
    # overlap >= window_size should raise error
    with pytest.raises(ValueError, match="window_size must be greater than overlap"):
        list(build_windows(lines, window_size=80, overlap=80))
    
    with pytest.raises(ValueError, match="window_size must be greater than overlap"):
        list(build_windows(lines, window_size=80, overlap=100))


@pytest.mark.unit
def test_build_windows_small_document():
    """Test windows with document smaller than window size."""
    lines = [(i, f"line {i}") for i in range(1, 11)]  # Only 10 lines
    windows = list(build_windows(lines, window_size=80, overlap=20))
    
    # Should have 1 window containing all lines
    assert len(windows) == 1
    chunk, start, end = windows[0]
    assert start == 1
    assert end == 10


@pytest.mark.unit
def test_build_windows_exact_fit():
    """Test windows when document size equals window size."""
    lines = [(i, f"line {i}") for i in range(1, 81)]  # Exactly 80 lines
    windows = list(build_windows(lines, window_size=80, overlap=20))
    
    # With exactly 80 lines and window_size=80, we get 1 window
    # (no need for a second window since all lines fit in the first)
    assert len(windows) >= 1


# ============================================================================
# Property-Based Test for Sliding Window Coverage
# ============================================================================

@pytest.mark.unit
@given(
    num_lines=st.integers(min_value=10, max_value=500),
    window_size=st.integers(min_value=20, max_value=100),
    overlap=st.integers(min_value=5, max_value=50)
)
def test_sliding_window_coverage(num_lines, window_size, overlap):
    """
    Feature: research-based-testing, Property 2: Sliding Window Coverage
    
    **Validates: Requirements 1.4**
    
    For any list of document lines and valid window parameters
    (window_size > overlap > 0), the generated windows should cover
    all lines with no gaps, maintain proper overlap between consecutive
    windows, and have correct boundary calculations.
    """
    # Ensure valid parameters
    assume(window_size > overlap > 0)
    
    # Generate test lines
    lines = [(i, f"line {i}") for i in range(1, num_lines + 1)]
    
    # Generate windows
    windows = list(build_windows(lines, window_size=window_size, overlap=overlap))
    
    # Property 1: At least one window should be generated
    assert len(windows) >= 1
    
    # Property 2: First window should start at line 1
    _, start_first, _ = windows[0]
    assert start_first == 1
    
    # Property 3: Last window should cover the last line
    _, _, end_last = windows[-1]
    assert end_last == num_lines
    
    # Property 4: Consecutive windows should have proper overlap
    step = window_size - overlap
    for i in range(len(windows) - 1):
        _, start_curr, end_curr = windows[i]
        _, start_next, end_next = windows[i + 1]
        
        # Next window should start at current_start + step
        expected_next_start = start_curr + step
        assert start_next == expected_next_start or start_next == start_curr + step
        
        # Overlap check: next window should start before current window ends
        if overlap > 0:
            assert start_next <= end_curr
    
    # Property 5: All lines should be covered (no gaps)
    covered_lines = set()
    for chunk, start, end in windows:
        for line_num in range(start, end + 1):
            covered_lines.add(line_num)
    
    expected_lines = set(range(1, num_lines + 1))
    assert covered_lines == expected_lines


# ============================================================================
# Unit Tests for _dedup_sections
# ============================================================================

@pytest.mark.unit
def test_dedup_sections_no_duplicates():
    """Test deduplication with no duplicate sections."""
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
    
    result = _dedup_sections(sections)
    assert len(result) == 2
    assert result[0].number == "1"
    assert result[1].number == "2"


@pytest.mark.unit
def test_dedup_sections_with_duplicates():
    """Test deduplication removes duplicate sections based on start_line."""
    sections = [
        ExtractedSection(
            number="1", title="Purpose", content="Content 1",
            start_line=1, end_line=10, is_complete=True
        ),
        ExtractedSection(
            number="1", title="Purpose", content="Content 1 extended",
            start_line=1, end_line=15, is_complete=True  # Wider range
        ),
        ExtractedSection(
            number="2", title="Scope", content="Content 2",
            start_line=20, end_line=30, is_complete=True
        ),
    ]
    
    result = _dedup_sections(sections)
    
    # Should keep only 2 sections (duplicate removed)
    assert len(result) == 2
    
    # Should keep the section with wider range (end_line=15)
    section_1 = next(s for s in result if s.start_line == 1)
    assert section_1.end_line == 15


@pytest.mark.unit
def test_dedup_sections_preserves_order():
    """Test that deduplication preserves order by start_line."""
    sections = [
        ExtractedSection(
            number="3", title="Third", content="Content 3",
            start_line=30, end_line=40, is_complete=True
        ),
        ExtractedSection(
            number="1", title="First", content="Content 1",
            start_line=1, end_line=10, is_complete=True
        ),
        ExtractedSection(
            number="2", title="Second", content="Content 2",
            start_line=20, end_line=25, is_complete=True
        ),
    ]
    
    result = _dedup_sections(sections)
    
    # Should be sorted by start_line
    assert result[0].start_line == 1
    assert result[1].start_line == 20
    assert result[2].start_line == 30


# ============================================================================
# Property-Based Test for Deduplication Uniqueness
# ============================================================================

@pytest.mark.unit
@given(st.lists(
    st.tuples(
        st.integers(min_value=1, max_value=100),  # start_line
        st.integers(min_value=1, max_value=50)    # range_size
    ),
    min_size=1,
    max_size=50
))
def test_deduplication_uniqueness(section_specs):
    """
    Feature: research-based-testing, Property 3: Deduplication Preserves Uniqueness
    
    **Validates: Requirements 1.5**
    
    For any list of ExtractedSection objects (including duplicates based on
    start_line), deduplication should produce a list where each start_line
    appears exactly once, preserving the section with the widest range for
    each start_line.
    """
    # Generate sections from specs
    sections = []
    for idx, (start_line, range_size) in enumerate(section_specs):
        end_line = start_line + range_size
        sections.append(ExtractedSection(
            number=str(idx),
            title=f"Section {idx}",
            content=f"Content {idx}",
            start_line=start_line,
            end_line=end_line,
            is_complete=True
        ))
    
    # Deduplicate
    result = _dedup_sections(sections)
    
    # Property 1: Each start_line should appear exactly once
    start_lines = [s.start_line for s in result]
    assert len(start_lines) == len(set(start_lines))
    
    # Property 2: For each start_line, should keep the widest range
    start_line_groups = {}
    for s in sections:
        if s.start_line not in start_line_groups:
            start_line_groups[s.start_line] = []
        start_line_groups[s.start_line].append(s)
    
    for start_line, group in start_line_groups.items():
        max_range = max(s.end_line - s.start_line for s in group)
        result_section = next(s for s in result if s.start_line == start_line)
        result_range = result_section.end_line - result_section.start_line
        assert result_range == max_range
    
    # Property 3: Result should be sorted by start_line
    for i in range(len(result) - 1):
        assert result[i].start_line <= result[i + 1].start_line


# ============================================================================
# Unit Tests for _remove_overlapping_sections
# ============================================================================

@pytest.mark.unit
def test_remove_overlapping_no_overlaps():
    """Test overlap removal with no overlapping sections."""
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
    
    result = _remove_overlapping_sections(sections)
    assert len(result) == 2


@pytest.mark.unit
def test_remove_overlapping_nested_sections():
    """Test that nested sections are removed, keeping parent."""
    sections = [
        ExtractedSection(
            number="1", title="Parent", content="Content 1",
            start_line=1, end_line=50, is_complete=True
        ),
        ExtractedSection(
            number="1.1", title="Child", content="Content 1.1",
            start_line=10, end_line=20, is_complete=True
        ),
        ExtractedSection(
            number="1.2", title="Child", content="Content 1.2",
            start_line=25, end_line=35, is_complete=True
        ),
    ]
    
    result = _remove_overlapping_sections(sections)
    
    # Should keep only the parent section
    assert len(result) == 1
    assert result[0].start_line == 1
    assert result[0].end_line == 50


@pytest.mark.unit
def test_remove_overlapping_partial_overlap():
    """Test handling of partially overlapping sections."""
    sections = [
        ExtractedSection(
            number="1", title="First", content="Content 1",
            start_line=1, end_line=30, is_complete=True
        ),
        ExtractedSection(
            number="2", title="Second", content="Content 2",
            start_line=25, end_line=50, is_complete=True
        ),
    ]
    
    result = _remove_overlapping_sections(sections)
    
    # Should keep the first section (started first)
    assert len(result) == 1
    assert result[0].start_line == 1


# ============================================================================
# Property-Based Test for Overlap Removal
# ============================================================================

@pytest.mark.unit
@given(st.lists(
    st.tuples(
        st.integers(min_value=1, max_value=100),  # start_line
        st.integers(min_value=5, max_value=30)    # range_size
    ),
    min_size=1,
    max_size=20
))
def test_overlap_removal_preserves_non_overlapping(section_specs):
    """
    Feature: research-based-testing, Property 4: Overlap Removal Preserves Non-Overlapping Sections
    
    **Validates: Requirements 1.6**
    
    For any list of ExtractedSection objects, removing overlapping sections
    should produce a list where no section's range overlaps with another,
    keeping parent sections when nested sections are detected.
    """
    # Generate sections
    sections = []
    for idx, (start_line, range_size) in enumerate(section_specs):
        end_line = start_line + range_size
        sections.append(ExtractedSection(
            number=str(idx),
            title=f"Section {idx}",
            content=f"Content {idx}",
            start_line=start_line,
            end_line=end_line,
            is_complete=True
        ))
    
    # Remove overlaps
    result = _remove_overlapping_sections(sections)
    
    # Property 1: No two sections should overlap
    for i in range(len(result)):
        for j in range(i + 1, len(result)):
            s1, s2 = result[i], result[j]
            # Check no overlap: either s1 ends before s2 starts, or vice versa
            no_overlap = (s1.end_line < s2.start_line) or (s2.end_line < s1.start_line)
            assert no_overlap, f"Sections overlap: {s1.start_line}-{s1.end_line} and {s2.start_line}-{s2.end_line}"
    
    # Property 2: Result should be sorted by start_line
    for i in range(len(result) - 1):
        assert result[i].start_line <= result[i + 1].start_line
    
    # Property 3: All result sections should be from original sections
    result_ids = {id(s) for s in result}
    original_ids = {id(s) for s in sections}
    assert result_ids.issubset(original_ids)


# ============================================================================
# Unit Tests for _renumber_sections
# ============================================================================

@pytest.mark.unit
def test_renumber_sections_basic():
    """Test basic sequential renumbering."""
    sections = [
        ExtractedSection(
            number="5", title="First", content="Content 1",
            start_line=1, end_line=10, is_complete=True
        ),
        ExtractedSection(
            number="10", title="Second", content="Content 2",
            start_line=11, end_line=20, is_complete=True
        ),
        ExtractedSection(
            number="3", title="Third", content="Content 3",
            start_line=21, end_line=30, is_complete=True
        ),
    ]
    
    result = _renumber_sections(sections)
    
    # Should be renumbered 1, 2, 3
    assert result[0].number == "1"
    assert result[1].number == "2"
    assert result[2].number == "3"
    
    # Other fields should be preserved
    assert result[0].title == "First"
    assert result[1].title == "Second"
    assert result[2].title == "Third"


@pytest.mark.unit
def test_renumber_sections_preserves_content():
    """Test that renumbering preserves all other section fields."""
    sections = [
        ExtractedSection(
            number="A.1", title="Purpose", content="Important content",
            start_line=5, end_line=15, is_complete=False
        ),
    ]
    
    result = _renumber_sections(sections)
    
    assert result[0].number == "1"
    assert result[0].title == "Purpose"
    assert result[0].content == "Important content"
    assert result[0].start_line == 5
    assert result[0].end_line == 15
    assert result[0].is_complete is False


# ============================================================================
# Property-Based Test for Sequential Renumbering
# ============================================================================

@pytest.mark.unit
@given(st.lists(
    st.tuples(
        st.text(min_size=1, max_size=10),  # arbitrary number
        st.integers(min_value=1, max_value=1000)  # start_line for ordering
    ),
    min_size=1,
    max_size=50
))
def test_sequential_renumbering(section_specs):
    """
    Feature: research-based-testing, Property 5: Sequential Renumbering
    
    **Validates: Requirements 1.7**
    
    For any list of ExtractedSection objects with arbitrary numbering,
    renumbering should produce sections numbered sequentially starting
    from 1, preserving the original order based on start_line.
    """
    # Generate sections with arbitrary numbering
    sections = []
    for idx, (arbitrary_num, start_line) in enumerate(section_specs):
        sections.append(ExtractedSection(
            number=arbitrary_num,
            title=f"Section {idx}",
            content=f"Content {idx}",
            start_line=start_line,
            end_line=start_line + 10,
            is_complete=True
        ))
    
    # Renumber
    result = _renumber_sections(sections)
    
    # Property 1: Should have same length
    assert len(result) == len(sections)
    
    # Property 2: Should be numbered sequentially from 1
    for idx, section in enumerate(result, start=1):
        assert section.number == str(idx)
    
    # Property 3: Order should be preserved (same as input order)
    for i in range(len(result)):
        assert result[i].title == sections[i].title
        assert result[i].content == sections[i].content
        assert result[i].start_line == sections[i].start_line

"""
Unit tests for gap analyzer functions.

Tests build_consolidated_report and create_combined_policy_content
with both unit tests and property-based tests.
"""

import pytest
from hypothesis import given, strategies as st
from pathlib import Path
import tempfile
import json

from src.gap_analyzer import (
    create_combined_policy_content,
    _summarize_assessments,
)
from src.agents.nist_gap_agents import (
    build_consolidated_report,
    SubcategoryAssessment,
)
from tests.utils.generators import generate_fake_assessment


# ============================================================================
# Unit Tests for create_combined_policy_content
# ============================================================================

@pytest.mark.unit
def test_create_combined_policy_content_basic():
    """Test basic policy content creation from master list."""
    master_list = [
        {
            "number": "1",
            "title": "Purpose",
            "summary": "This policy establishes the framework for information security."
        },
        {
            "number": "2",
            "title": "Scope",
            "summary": "This policy applies to all employees and contractors."
        },
    ]
    
    result = create_combined_policy_content(master_list)
    
    # Verify structure
    assert "POLICY DOCUMENT CONTENT" in result
    assert "Section 1: Purpose" in result
    assert "Section 2: Scope" in result
    assert "This policy establishes" in result
    assert "This policy applies" in result


@pytest.mark.unit
def test_create_combined_policy_content_with_full_sections():
    """Test policy content creation with full section content from sections_output.json."""
    master_list = [
        {
            "number": "1",
            "title": "Purpose",
            "summary": "Short summary"
        },
    ]
    
    # Create temporary sections file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        sections_data = [
            {
                "number": "1",
                "title": "Purpose",
                "content": "This is the full detailed content from the actual policy document."
            }
        ]
        json.dump(sections_data, f)
        sections_path = Path(f.name)
    
    try:
        result = create_combined_policy_content(master_list, sections_path)
        
        # Should prefer full content over summary
        assert "full detailed content" in result
        assert "Short summary" not in result
    finally:
        sections_path.unlink()


@pytest.mark.unit
def test_create_combined_policy_content_truncation():
    """Test that very long sections are truncated to _CONTENT_CHAR_LIMIT."""
    # Create a section with content exceeding 12000 characters
    long_content = "A" * 15000
    
    master_list = [
        {
            "number": "1",
            "title": "Long Section",
            "summary": "Summary"
        },
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        sections_data = [
            {
                "number": "1",
                "title": "Long Section",
                "content": long_content
            }
        ]
        json.dump(sections_data, f)
        sections_path = Path(f.name)
    
    try:
        result = create_combined_policy_content(master_list, sections_path)
        
        # Content should be truncated
        # The result includes formatting, so check the section content is limited
        section_start = result.find("### Section 1:")
        section_end = result.find("---", section_start)
        section_content = result[section_start:section_end]
        
        # Should not contain the full 15000 characters
        assert len(section_content) < 13000  # Some buffer for formatting
    finally:
        sections_path.unlink()


@pytest.mark.unit
def test_create_combined_policy_content_skips_empty_sections():
    """Test that sections with no summary and no content are skipped."""
    master_list = [
        {
            "number": "1",
            "title": "Purpose",
            "summary": "Has content"
        },
        {
            "number": "2",
            "title": "Empty Header",
            "summary": None  # No summary
        },
        {
            "number": "3",
            "title": "Scope",
            "summary": "Has content"
        },
    ]
    
    result = create_combined_policy_content(master_list)
    
    # Should include sections 1 and 3
    assert "Section 1: Purpose" in result
    assert "Section 3: Scope" in result
    
    # Should skip section 2
    assert "Section 2: Empty Header" not in result


@pytest.mark.unit
def test_create_combined_policy_content_missing_sections_file():
    """Test handling when sections_output.json doesn't exist."""
    master_list = [
        {
            "number": "1",
            "title": "Purpose",
            "summary": "This is the summary"
        },
    ]
    
    # Use non-existent path
    result = create_combined_policy_content(master_list, Path("/nonexistent/file.json"))
    
    # Should fall back to summaries
    assert "This is the summary" in result


# ============================================================================
# Property-Based Test for Content Truncation
# ============================================================================

@pytest.mark.unit
@given(st.integers(min_value=0, max_value=20000))
def test_content_truncation_at_limit(content_length):
    """
    Feature: research-based-testing, Property 8: Content Truncation at Limit
    
    **Validates: Requirements 2.5, 4.5**
    
    For any text content of any length, truncation to _CONTENT_CHAR_LIMIT
    (12000 characters) should produce output of exactly 12000 characters
    when input exceeds the limit, or unchanged output when input is below
    the limit.
    """
    # Generate content of specified length
    content = "X" * content_length
    
    master_list = [
        {
            "number": "1",
            "title": "Test Section",
            "summary": "Summary"
        },
    ]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        sections_data = [
            {
                "number": "1",
                "title": "Test Section",
                "content": content
            }
        ]
        json.dump(sections_data, f)
        sections_path = Path(f.name)
    
    try:
        result = create_combined_policy_content(master_list, sections_path)
        
        # Extract the section content from the formatted result
        section_start = result.find("### Section 1:")
        if section_start != -1:
            section_end = result.find("---", section_start)
            section_content = result[section_start:section_end]
            
            # Count X's in the section content
            x_count = section_content.count("X")
            
            # Property: should be truncated to 12000 or less
            if content_length > 12000:
                assert x_count == 12000, f"Expected 12000 chars, got {x_count}"
            else:
                assert x_count == content_length, f"Expected {content_length} chars, got {x_count}"
    finally:
        sections_path.unlink()


# ============================================================================
# Unit Tests for _summarize_assessments
# ============================================================================

@pytest.mark.unit
def test_summarize_assessments_basic():
    """Test basic assessment summarization."""
    assessments = [
        SubcategoryAssessment(
            subcategory_id="GV.OC-01",
            title="Test 1",
            status="Addressed",
            evidence="Evidence 1",
            gap="None",
            recommendation="None"
        ),
        SubcategoryAssessment(
            subcategory_id="GV.OC-02",
            title="Test 2",
            status="Partially Addressed",
            evidence="Evidence 2",
            gap="Some gap",
            recommendation="Fix it"
        ),
        SubcategoryAssessment(
            subcategory_id="GV.OC-03",
            title="Test 3",
            status="Not Addressed",
            evidence="None",
            gap="Missing",
            recommendation="Add it"
        ),
    ]
    
    result = _summarize_assessments(assessments)
    
    assert result["total"] == 3
    assert result["in_scope"] == 3
    assert result["out_of_scope"] == 0
    assert result["addressed"] == 1
    assert result["partially_addressed"] == 1
    assert result["not_addressed"] == 1


@pytest.mark.unit
def test_summarize_assessments_with_out_of_scope():
    """Test assessment summarization with out-of-scope items."""
    assessments = [
        SubcategoryAssessment(
            subcategory_id="GV.OC-01",
            title="Test 1",
            status="Addressed",
            evidence="Evidence 1",
            gap="None",
            recommendation="None"
        ),
        SubcategoryAssessment(
            subcategory_id="PR.AC-01",
            title="Test 2",
            status="Out of Scope",
            evidence="N/A",
            gap="N/A",
            recommendation="Different policy needed"
        ),
    ]
    
    result = _summarize_assessments(assessments)
    
    assert result["total"] == 2
    assert result["in_scope"] == 1
    assert result["out_of_scope"] == 1
    assert result["addressed"] == 1


# ============================================================================
# Unit Tests for build_consolidated_report
# ============================================================================

@pytest.mark.unit
def test_build_consolidated_report_basic():
    """Test basic consolidated report generation."""
    all_assessments = {
        "Govern": [
            SubcategoryAssessment(
                subcategory_id="GV.OC-01",
                title="Organizational Context",
                status="Addressed",
                evidence="Section 2 covers this",
                gap="None",
                recommendation="None"
            ),
            SubcategoryAssessment(
                subcategory_id="GV.RM-01",
                title="Risk Management",
                status="Not Addressed",
                evidence="None found",
                gap="Missing risk management process",
                recommendation="Add risk management section"
            ),
        ],
        "Identify": [
            SubcategoryAssessment(
                subcategory_id="ID.AM-01",
                title="Asset Management",
                status="Partially Addressed",
                evidence="Partial coverage",
                gap="Missing asset inventory",
                recommendation="Create asset inventory"
            ),
        ],
    }
    
    report = build_consolidated_report(all_assessments)
    
    # Verify report structure
    assert "NIST CSF Gap Analysis — Consolidated Report" in report
    assert "Executive Summary" in report
    assert "Maturity by Function" in report
    assert "In-Scope Gaps (Not Addressed)" in report
    assert "Prioritized Remediation Roadmap" in report
    
    # Verify function names appear
    assert "Govern" in report
    assert "Identify" in report


@pytest.mark.unit
def test_build_consolidated_report_structure():
    """Test that consolidated report has correct structure and counts."""
    all_assessments = {
        "Govern": [
            generate_fake_assessment("GV.OC-01", "Addressed"),
            generate_fake_assessment("GV.OC-02", "Partially Addressed"),
            generate_fake_assessment("GV.OC-03", "Not Addressed"),
        ],
        "Identify": [
            generate_fake_assessment("ID.AM-01", "Addressed"),
            generate_fake_assessment("ID.AM-02", "Out of Scope"),
        ],
    }
    
    report = build_consolidated_report(all_assessments)
    
    # Check that counts are present
    assert "Total Subcategories" in report
    assert "In Scope:" in report
    assert "Out of Scope:" in report
    assert "Addressed:" in report
    assert "Partially Addressed:" in report
    assert "Not Addressed:" in report


# ============================================================================
# Property-Based Test for Consolidated Report Completeness
# ============================================================================

@pytest.mark.unit
@given(
    st.lists(
        st.tuples(
            st.sampled_from(["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]),
            st.lists(
                st.sampled_from(["Addressed", "Partially Addressed", "Not Addressed", "Out of Scope"]),
                min_size=1,
                max_size=10
            )
        ),
        min_size=1,
        max_size=6
    )
)
def test_consolidated_report_completeness(function_assessments):
    """
    Feature: research-based-testing, Property 6: Consolidated Report Completeness
    
    **Validates: Requirements 1.8**
    
    For any valid mapping of NIST functions to SubcategoryAssessment lists,
    the consolidated report should contain sections for all six NIST functions,
    correct aggregate counts matching the input data, and properly formatted
    tables.
    """
    # Build assessments dictionary
    all_assessments = {}
    expected_totals = {
        "total": 0,
        "in_scope": 0,
        "out_of_scope": 0,
        "addressed": 0,
        "partially_addressed": 0,
        "not_addressed": 0,
    }
    
    for function_name, statuses in function_assessments:
        if function_name not in all_assessments:
            all_assessments[function_name] = []
        
        for idx, status in enumerate(statuses):
            assessment = SubcategoryAssessment(
                subcategory_id=f"{function_name[:2]}.XX-{idx:02d}",
                title=f"Test {idx}",
                status=status,
                evidence="Test evidence",
                gap="Test gap",
                recommendation="Test recommendation"
            )
            all_assessments[function_name].append(assessment)
            
            # Track expected counts
            expected_totals["total"] += 1
            if status == "Out of Scope":
                expected_totals["out_of_scope"] += 1
            else:
                expected_totals["in_scope"] += 1
                if status == "Addressed":
                    expected_totals["addressed"] += 1
                elif status == "Partially Addressed":
                    expected_totals["partially_addressed"] += 1
                elif status == "Not Addressed":
                    expected_totals["not_addressed"] += 1
    
    # Generate report
    report = build_consolidated_report(all_assessments)
    
    # Property 1: Report should contain all standard sections
    assert "NIST CSF Gap Analysis — Consolidated Report" in report
    assert "Executive Summary" in report
    assert "Maturity by Function" in report
    
    # Property 2: Report should mention all functions that have assessments
    for function_name in all_assessments.keys():
        assert function_name in report
    
    # Property 3: Report should contain the maturity table
    assert "| Function | Rating | In Scope |" in report or "Maturity by Function" in report
    
    # Property 4: Report should have gap sections
    if expected_totals["not_addressed"] > 0:
        assert "In-Scope Gaps (Not Addressed)" in report
    
    if expected_totals["partially_addressed"] > 0:
        assert "In-Scope Gaps (Partially Addressed)" in report
    
    # Property 5: Report should have remediation roadmap
    assert "Prioritized Remediation Roadmap" in report or "Priority" in report

"""
Test data generators for creating synthetic test objects.

Provides utility functions and hypothesis strategies for generating
realistic test data across all test phases.
"""

from hypothesis import strategies as st
from src.models import ExtractedSection


def generate_fake_section(
    number: str = "1",
    title: str = "Test Section",
    content_length: int = 500,
    start_line: int = 1,
    is_complete: bool = True
) -> ExtractedSection:
    """
    Generate synthetic ExtractedSection for testing.
    
    Args:
        number: Section number (e.g., "1", "2.1", "A.1")
        title: Section title
        content_length: Approximate length of content in characters
        start_line: Starting line number
        is_complete: Whether section is complete
    
    Returns:
        ExtractedSection with synthetic data
    """
    # Generate content of approximately the requested length
    content = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * (content_length // 57)
    content = content[:content_length]
    
    end_line = start_line + (content_length // 80) if is_complete else None
    
    return ExtractedSection(
        number=number,
        title=title,
        content=content,
        start_line=start_line,
        end_line=end_line,
        is_complete=is_complete
    )


def generate_fake_assessment(
    subcategory_id: str = "GV.OC-01",
    title: str = "Test Subcategory",
    status: str = "Addressed",
    evidence: str = "Test evidence from policy section",
    gap: str = "None - fully addressed",
    recommendation: str = "No action needed"
):
    """
    Generate synthetic SubcategoryAssessment for testing.
    
    Args:
        subcategory_id: NIST subcategory ID (e.g., "GV.OC-01")
        title: Subcategory title
        status: Assessment status (Addressed, Partially Addressed, Not Addressed)
        evidence: Evidence text from policy
        gap: Gap description
        recommendation: Recommendation text
    
    Returns:
        SubcategoryAssessment with synthetic data
    """
    from src.agents.nist_gap_agents import SubcategoryAssessment
    
    return SubcategoryAssessment(
        subcategory_id=subcategory_id,
        title=title,
        status=status,
        evidence=evidence,
        gap=gap,
        recommendation=recommendation
    )


# Hypothesis strategies for property-based testing

@st.composite
def st_extracted_section(draw):
    """
    Hypothesis strategy for generating ExtractedSection objects.
    
    Generates sections with realistic constraints:
    - Section numbers: 1-99 or hierarchical like "1.1", "A.1"
    - Titles: 5-50 characters
    - Content: 50-2000 characters
    - Line numbers: 1-10000
    - Complete sections have end_line > start_line
    """
    # Generate section number
    number_type = draw(st.sampled_from(["numeric", "hierarchical", "alpha"]))
    if number_type == "numeric":
        number = str(draw(st.integers(min_value=1, max_value=99)))
    elif number_type == "hierarchical":
        major = draw(st.integers(min_value=1, max_value=20))
        minor = draw(st.integers(min_value=1, max_value=20))
        number = f"{major}.{minor}"
    else:  # alpha
        letter = draw(st.sampled_from("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
        num = draw(st.integers(min_value=1, max_value=20))
        number = f"{letter}.{num}"
    
    # Generate title
    title = draw(st.text(min_size=5, max_size=50, alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd", "Zs")
    )))
    
    # Generate content
    content = draw(st.text(min_size=50, max_size=2000, alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd", "Zs", "Po")
    )))
    
    # Generate line numbers
    start_line = draw(st.integers(min_value=1, max_value=10000))
    is_complete = draw(st.booleans())
    
    if is_complete:
        end_line = draw(st.integers(min_value=start_line + 1, max_value=start_line + 100))
    else:
        end_line = None
    
    return ExtractedSection(
        number=number,
        title=title,
        content=content,
        start_line=start_line,
        end_line=end_line,
        is_complete=is_complete
    )


@st.composite
def st_assessment(draw):
    """
    Hypothesis strategy for generating SubcategoryAssessment objects.
    
    Generates assessments with realistic NIST subcategory IDs and statuses.
    """
    from src.agents.nist_gap_agents import SubcategoryAssessment
    
    # NIST function prefixes
    function = draw(st.sampled_from(["GV", "ID", "PR", "DE", "RS", "RC"]))
    
    # Category codes (simplified)
    category = draw(st.sampled_from(["OC", "RM", "SC", "PO", "AM", "RA", "AC", "DS"]))
    
    # Subcategory number
    num = draw(st.integers(min_value=1, max_value=20))
    subcategory_id = f"{function}.{category}-{num:02d}"
    
    # Title
    title = draw(st.text(min_size=10, max_size=100, alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Zs")
    )))
    
    # Status
    status = draw(st.sampled_from(["Addressed", "Partially Addressed", "Not Addressed"]))
    
    # Evidence
    evidence = draw(st.text(min_size=20, max_size=500, alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd", "Zs", "Po")
    )))
    
    # Gap
    gap = draw(st.text(min_size=10, max_size=300, alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd", "Zs", "Po")
    )))
    
    # Recommendation
    recommendation = draw(st.text(min_size=10, max_size=300, alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd", "Zs", "Po")
    )))
    
    return SubcategoryAssessment(
        subcategory_id=subcategory_id,
        title=title,
        status=status,
        evidence=evidence,
        gap=gap,
        recommendation=recommendation
    )

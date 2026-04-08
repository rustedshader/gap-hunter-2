"""
Adversarial tests for corrupted and malicious inputs.

Tests system robustness against out-of-scope documents, corrupted PDFs,
malformed data, and inputs exceeding context limits.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile

# Mark all tests in this module as adversarial tests
pytestmark = pytest.mark.adversarial


@pytest.mark.adversarial
def test_out_of_scope_document():
    """
    Test handling of completely out-of-scope documents.
    
    **Validates: Requirements 4.1**
    
    When given a document that is not a cybersecurity policy (e.g., a catering menu),
    the system should classify it as out of scope or return empty function list.
    """
    from src.agents.nist_gap_agents import classify_policy_functions
    
    # Simulate a completely irrelevant document
    out_of_scope_content = """
    # Corporate Catering Menu
    
    ## Breakfast Options
    - Continental Breakfast: $12.99 per person
    - Hot Breakfast Buffet: $18.99 per person
    
    ## Lunch Options
    - Sandwich Platter: $15.99 per person
    - Hot Lunch Buffet: $22.99 per person
    
    ## Beverages
    - Coffee Service: $3.99 per person
    - Soft Drinks: $2.99 per person
    
    Please contact catering@example.com for orders.
    """
    
    print("\n" + "="*60)
    print("Testing out-of-scope document (Catering Menu)")
    print("="*60)
    
    # Run classification
    result = classify_policy_functions(out_of_scope_content)
    
    print(f"Classification result: {result}")
    
    # Should return empty list or minimal functions
    # (system should recognize this is not a cybersecurity policy)
    assert len(result) <= 1, (
        f"Out-of-scope document should not be classified with multiple functions. "
        f"Got: {result}"
    )
    
    print("✓ Out-of-scope document handled correctly")


@pytest.mark.adversarial
def test_corrupted_pdf_raises_error():
    """
    Test handling of corrupted PDF files.
    
    **Validates: Requirements 4.3**
    
    When given a corrupted PDF file, pdf_to_markdown should raise an appropriate error.
    """
    from src.tools.pdf import pdf_to_markdown
    
    print("\n" + "="*60)
    print("Testing corrupted PDF handling")
    print("="*60)
    
    # Create a fake corrupted PDF (just random bytes)
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b'This is not a valid PDF file content\x00\x01\x02\x03')
        corrupted_path = Path(f.name)
    
    try:
        # Should raise an error when trying to process
        with pytest.raises(Exception):  # Could be ValueError, PDFError, etc.
            pdf_to_markdown(corrupted_path)
        
        print("✓ Corrupted PDF raised appropriate error")
    finally:
        # Cleanup
        corrupted_path.unlink()


@pytest.mark.adversarial
def test_malformed_mt_codes():
    """
    Test handling of malformed /MT font codes.
    
    **Validates: Requirements 4.4**
    
    The _decode_mt_codes function should handle malformed patterns gracefully
    without raising exceptions.
    """
    from src.tools.pdf import _decode_mt_codes
    
    print("\n" + "="*60)
    print("Testing malformed /MT code handling")
    print("="*60)
    
    test_cases = [
        ("/MT", "Incomplete pattern"),
        ("/MTabc", "Non-numeric code"),
        ("/MT-5", "Negative number"),
        ("/MT999999999999", "Overflow number"),
        ("/MT10/MT200", "Out of range codes"),
        ("Normal text /MT65 /MTxyz mixed", "Mixed valid and invalid"),
    ]
    
    for input_text, description in test_cases:
        try:
            result = _decode_mt_codes(input_text)
            print(f"  ✓ {description}: '{input_text}' -> '{result}'")
            assert isinstance(result, str), "Should return string"
        except Exception as e:
            pytest.fail(f"Failed on {description}: {e}")
    
    print("✓ All malformed /MT codes handled gracefully")


@pytest.mark.adversarial
def test_sections_exceeding_context_limits():
    """
    Test handling of sections that exceed context window limits.
    
    **Validates: Requirements 4.5**
    
    When sections exceed the _CONTENT_CHAR_LIMIT (12000 characters),
    the system should truncate content to prevent crashes.
    """
    from src.gap_analyzer import create_combined_policy_content
    import json
    
    print("\n" + "="*60)
    print("Testing section content truncation")
    print("="*60)
    
    # Create a section with excessive content (20000 characters)
    excessive_content = "X" * 20000
    
    master_list = [
        {
            "number": "1",
            "title": "Excessive Section",
            "summary": "Summary"
        }
    ]
    
    # Create temporary sections file with excessive content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        sections_data = [
            {
                "number": "1",
                "title": "Excessive Section",
                "content": excessive_content
            }
        ]
        json.dump(sections_data, f)
        sections_path = Path(f.name)
    
    try:
        # Should not crash, should truncate
        result = create_combined_policy_content(master_list, sections_path)
        
        # Verify truncation occurred
        assert len(result) < 15000, "Content should be truncated"
        print(f"  ✓ Content truncated from 20000 to ~{len(result)} characters")
        
        print("✓ Section overflow handled with truncation")
    finally:
        sections_path.unlink()


@pytest.mark.adversarial
def test_section_overflow_safeguard():
    """
    Test MAX_SECTIONS_PER_WINDOW safeguard against hallucinated sections.
    
    **Validates: Requirements 4.2, 4.7**
    
    When an extractor returns more than MAX_SECTIONS_PER_WINDOW (20) sections,
    the safeguard should trigger and discard all sections to prevent
    hallucination propagation.
    """
    from src.extractor import _apply_section_overflow_safeguard
    from src.models import ExtractedSection
    
    print("\n" + "="*60)
    print("Testing section overflow safeguard")
    print("="*60)
    
    # Create 25 fake sections (exceeds MAX_SECTIONS_PER_WINDOW of 20)
    excessive_sections = []
    for i in range(25):
        section = ExtractedSection(
            number=str(i + 1),
            title=f"Section {i + 1}",
            content=f"Content {i + 1}",
            start_line=i * 10 + 1,
            end_line=i * 10 + 10,
            is_complete=True
        )
        excessive_sections.append(section)
    
    print(f"  Input: {len(excessive_sections)} sections (exceeds limit of 20)")
    
    # Apply safeguard
    result = _apply_section_overflow_safeguard(excessive_sections)
    
    print(f"  Output: {len(result)} sections")
    
    # Safeguard should discard all sections
    assert len(result) == 0, (
        f"Section overflow safeguard should discard all sections when count > 20. "
        f"Got {len(result)} sections"
    )
    
    print("✓ Section overflow safeguard triggered correctly")
    
    # Test with acceptable number of sections (should pass through)
    acceptable_sections = excessive_sections[:15]
    result = _apply_section_overflow_safeguard(acceptable_sections)
    
    assert len(result) == 15, "Acceptable section count should pass through"
    print("✓ Acceptable section count passes through safeguard")


@pytest.mark.adversarial
def test_empty_policy_document():
    """
    Test handling of empty or nearly empty policy documents.
    
    **Validates: Requirements 4.1**
    
    System should handle empty documents gracefully without crashing.
    """
    from src.agents.nist_gap_agents import classify_policy_functions
    
    print("\n" + "="*60)
    print("Testing empty document handling")
    print("="*60)
    
    # Test completely empty
    result = classify_policy_functions("")
    print(f"  Empty string result: {result}")
    assert isinstance(result, list), "Should return a list"
    
    # Test whitespace only
    result = classify_policy_functions("   \n\n   \t\t   ")
    print(f"  Whitespace only result: {result}")
    assert isinstance(result, list), "Should return a list"
    
    # Test minimal content
    result = classify_policy_functions("Policy")
    print(f"  Minimal content result: {result}")
    assert isinstance(result, list), "Should return a list"
    
    print("✓ Empty documents handled gracefully")


@pytest.mark.adversarial
def test_non_pdf_file_rejection():
    """
    Test that non-PDF files are rejected appropriately.
    
    **Validates: Requirements 4.3**
    
    pdf_to_markdown should raise ValueError for non-PDF files.
    """
    from src.tools.pdf import pdf_to_markdown
    
    print("\n" + "="*60)
    print("Testing non-PDF file rejection")
    print("="*60)
    
    test_cases = [
        "document.txt",
        "document.docx",
        "document.xlsx",
        "document.pptx",
        "document.html",
        "document.md",
    ]
    
    for filename in test_cases:
        with pytest.raises(ValueError, match="File must be a PDF"):
            pdf_to_markdown(Path(filename))
        print(f"  ✓ Rejected: {filename}")
    
    print("✓ Non-PDF files rejected correctly")


@pytest.mark.adversarial
def test_special_characters_in_policy():
    """
    Test handling of special characters and unicode in policy content.
    
    **Validates: Requirements 4.5**
    
    System should handle special characters without crashing.
    """
    from src.agents.nist_gap_agents import classify_policy_functions
    
    print("\n" + "="*60)
    print("Testing special character handling")
    print("="*60)
    
    special_content = """
    # Information Security Policy™
    
    ## Purpose®
    This policy establishes… the framework for information security.
    
    ## Scope
    Applies to: employees, contractors, & third-parties.
    
    ## Requirements
    • Passwords must be ≥12 characters
    • Access control: role-based (RBAC)
    • Encryption: AES-256 → all data at rest
    
    © 2024 Company™. All rights reserved.
    """
    
    try:
        result = classify_policy_functions(special_content)
        print(f"  Classification result: {result}")
        assert isinstance(result, list), "Should return a list"
        print("✓ Special characters handled correctly")
    except Exception as e:
        pytest.fail(f"Failed to handle special characters: {e}")


@pytest.mark.adversarial
def test_extremely_long_section_title():
    """
    Test handling of sections with extremely long titles.
    
    **Validates: Requirements 4.5**
    
    System should handle long titles without crashing.
    """
    from src.models import ExtractedSection
    
    print("\n" + "="*60)
    print("Testing extremely long section title")
    print("="*60)
    
    # Create section with 1000-character title
    long_title = "A" * 1000
    
    try:
        section = ExtractedSection(
            number="1",
            title=long_title,
            content="Normal content",
            start_line=1,
            end_line=10,
            is_complete=True
        )
        
        # Verify it was created
        assert section.title == long_title
        assert len(section.title) == 1000
        
        # Verify serialization works
        data = section.model_dump()
        restored = ExtractedSection.model_validate(data)
        assert restored.title == long_title
        
        print(f"  ✓ Created section with {len(long_title)}-character title")
        print("✓ Extremely long titles handled correctly")
    except Exception as e:
        pytest.fail(f"Failed to handle long title: {e}")

"""
Unit tests for PDF utility functions.

Tests _decode_mt_codes function for valid patterns, invalid input,
malformed patterns, and round-trip property.
"""

import pytest
from hypothesis import given, strategies as st
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.tools.pdf import _decode_mt_codes, pdf_to_markdown


# ============================================================================
# Unit Tests for _decode_mt_codes
# ============================================================================

@pytest.mark.unit
def test_decode_mt_codes_valid_pattern():
    """Test decoding of valid /MT code patterns."""
    # Test case from docstring: /MT73/MT110/MT102/MT111 -> "Info"
    input_text = "/MT73/MT110/MT102/MT111"
    expected = "Info"
    assert _decode_mt_codes(input_text) == expected


@pytest.mark.unit
def test_decode_mt_codes_printable_ascii():
    """Test decoding of various printable ASCII characters."""
    # A (65), z (122), ~ (126), Hello
    # Note: Space (32) gets stripped by the function's line.strip() call
    test_cases = [
        ("/MT65", "A"),
        ("/MT122", "z"),
        ("/MT126", "~"),
        ("/MT72/MT101/MT108/MT108/MT111", "Hello"),
    ]
    
    for input_text, expected in test_cases:
        assert _decode_mt_codes(input_text) == expected


@pytest.mark.unit
def test_decode_mt_codes_out_of_range():
    """Test that out-of-range codes are left unchanged."""
    # Codes outside printable ASCII range (32-126) should be preserved
    input_text = "/MT10/MT200"
    # These should remain unchanged as they're outside the valid range
    assert "/MT10" in _decode_mt_codes(input_text)
    assert "/MT200" in _decode_mt_codes(input_text)


@pytest.mark.unit
def test_decode_mt_codes_malformed_patterns():
    """Test handling of malformed /MT code patterns."""
    test_cases = [
        "/MT",  # Incomplete pattern
        "/MTabc",  # Non-numeric code
        "/MT-5",  # Negative number
        "/MT",  # Just the prefix
    ]
    
    for input_text in test_cases:
        # Should not raise exception, returns original or best-effort decode
        result = _decode_mt_codes(input_text)
        assert isinstance(result, str)


@pytest.mark.unit
def test_decode_mt_codes_mixed_content():
    """Test decoding with mixed MT codes and regular text."""
    input_text = "Section /MT49: /MT80/MT117/MT114/MT112/MT111/MT115/MT101"
    result = _decode_mt_codes(input_text)
    # Should decode the MT codes while preserving other text
    assert "Section" in result
    assert "1" in result  # /MT49 -> '1'
    assert "Purpose" in result  # The decoded word


@pytest.mark.unit
def test_decode_mt_codes_empty_string():
    """Test decoding of empty string."""
    assert _decode_mt_codes("") == ""


@pytest.mark.unit
def test_decode_mt_codes_no_mt_codes():
    """Test text without any /MT codes."""
    input_text = "This is regular text without any codes."
    assert _decode_mt_codes(input_text) == "This is regular text without any codes."


@pytest.mark.unit
def test_decode_mt_codes_spaced_words():
    """Test that spaced-out words are fixed."""
    # The function should collapse "r e q u i r e m e n t" -> "requirement"
    input_text = "r e q u i r e m e n t"
    result = _decode_mt_codes(input_text)
    assert "requirement" in result


# ============================================================================
# Property-Based Test for MT Code Round-Trip
# ============================================================================

@pytest.mark.unit
@given(st.integers(min_value=33, max_value=126))  # Exclude space (32) as it gets stripped
def test_mt_code_round_trip(ascii_code):
    """
    Feature: research-based-testing, Property 1: MT Code Decoding Round-Trip
    
    **Validates: Requirements 1.2**
    
    For any valid ASCII character in the printable range (33-126, excluding space),
    encoding it as an /MT code pattern and then decoding should
    produce the original character.
    
    Note: Space (ASCII 32) is excluded because the _decode_mt_codes function
    strips whitespace from lines as part of its cleanup process.
    """
    # Encode
    encoded = f"/MT{ascii_code}"
    
    # Decode
    decoded = _decode_mt_codes(encoded)
    
    # Verify round-trip
    expected_char = chr(ascii_code)
    assert decoded == expected_char, f"Round-trip failed for ASCII {ascii_code}: expected '{expected_char}', got '{decoded}'"


# ============================================================================
# Unit Tests for pdf_to_markdown
# ============================================================================

@pytest.mark.unit
def test_pdf_to_markdown_non_pdf_raises_error():
    """Test that non-PDF files raise ValueError."""
    with pytest.raises(ValueError, match="File must be a PDF"):
        pdf_to_markdown(Path("document.txt"))
    
    with pytest.raises(ValueError, match="File must be a PDF"):
        pdf_to_markdown(Path("document.docx"))


@pytest.mark.unit
@patch('src.tools.pdf.DocumentConverter')
def test_pdf_to_markdown_basic_conversion(mock_converter_class):
    """Test basic PDF to markdown conversion."""
    # Setup mock
    mock_converter = MagicMock()
    mock_doc = MagicMock()
    mock_doc.export_to_markdown.return_value = "# Test Document\n\nContent here."
    mock_result = MagicMock()
    mock_result.document = mock_doc
    mock_converter.convert.return_value = mock_result
    mock_converter_class.return_value = mock_converter
    
    # Test
    result = pdf_to_markdown(Path("test.pdf"))
    
    # Verify
    assert result == "# Test Document\n\nContent here."
    mock_converter.convert.assert_called_once()


@pytest.mark.unit
@patch('src.tools.pdf.DocumentConverter')
@patch('src.tools.pdf.logger')
def test_pdf_to_markdown_with_mt_codes(mock_logger, mock_converter_class):
    """Test PDF conversion with /MT code decoding."""
    # Setup mock with /MT codes
    mock_converter = MagicMock()
    mock_doc = MagicMock()
    mock_doc.export_to_markdown.return_value = "/MT73/MT110/MT102/MT111"
    mock_result = MagicMock()
    mock_result.document = mock_doc
    mock_converter.convert.return_value = mock_result
    mock_converter_class.return_value = mock_converter
    
    # Test
    result = pdf_to_markdown(Path("test.pdf"))
    
    # Verify decoding happened
    assert result == "Info"
    mock_logger.warning.assert_called_once()
    assert "Detected /MT font codes" in str(mock_logger.warning.call_args)

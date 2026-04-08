"""
Infrastructure verification tests.

Simple tests to verify the test framework is set up correctly.
"""

import pytest
from src.models import ExtractedSection
from tests.utils.generators import generate_fake_section, generate_fake_assessment


@pytest.mark.unit
def test_infrastructure_setup():
    """Verify basic test infrastructure is working."""
    assert True


@pytest.mark.unit
def test_sample_sections_fixture(sample_sections):
    """Verify sample_sections fixture works correctly."""
    assert len(sample_sections) == 3
    assert all(isinstance(s, ExtractedSection) for s in sample_sections)
    assert sample_sections[0].title == "Purpose"


@pytest.mark.unit
def test_generate_fake_section():
    """Verify generate_fake_section utility works correctly."""
    section = generate_fake_section(
        number="1.1",
        title="Test Section",
        content_length=100,
        start_line=5
    )
    
    assert section.number == "1.1"
    assert section.title == "Test Section"
    assert section.start_line == 5
    assert len(section.content) <= 100
    assert section.is_complete is True


@pytest.mark.unit
def test_pydantic_model_round_trip():
    """
    Verify ExtractedSection serialization round-trip.
    
    Feature: research-based-testing, Property 7: Pydantic Model Serialization Round-Trip
    
    For any valid instance of ExtractedSection, serializing via model_dump()
    and deserializing via model_validate() should produce an equivalent object.
    """
    original = ExtractedSection(
        number="1",
        title="Test",
        content="Test content",
        start_line=1,
        end_line=10,
        is_complete=True
    )
    
    # Serialize
    dumped = original.model_dump()
    
    # Deserialize
    restored = ExtractedSection.model_validate(dumped)
    
    # Verify equivalence
    assert restored == original
    assert restored.number == original.number
    assert restored.title == original.title
    assert restored.content == original.content
    assert restored.start_line == original.start_line
    assert restored.end_line == original.end_line
    assert restored.is_complete == original.is_complete

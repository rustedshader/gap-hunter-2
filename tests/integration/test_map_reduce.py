"""
Integration tests for map-reduce architecture in gap analysis.

Tests map phase sequential calls, reduce phase evidence concatenation,
and complete map-reduce data flow using mocked LLM responses.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.agents.nist_gap_agents import (
    _map_sections_for_subcategory,
    _reduce_to_assessment,
    SectionEvidenceResult,
    SubcategoryAssessment,
)


# ============================================================================
# Integration Tests for Map Phase
# ============================================================================

@pytest.mark.integration
@patch('agents.nist_gap_agents.create_llm')
def test_map_phase_sequential_calls(mock_create_llm):
    """
    Test that map phase makes N sequential LLM calls for N sections.
    
    **Validates: Requirements 2.2, 2.4**
    """
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm
    
    # Mock responses for each section
    mock_structured_llm.invoke.side_effect = [
        SectionEvidenceResult(
            has_evidence=True,
            evidence_snippet="Section 1 mentions risk assessment procedures."
        ),
        SectionEvidenceResult(
            has_evidence=False,
            evidence_snippet="None found"
        ),
        SectionEvidenceResult(
            has_evidence=True,
            evidence_snippet="Section 3 defines risk management roles."
        ),
    ]
    
    # Test data: 3 policy sections
    policy_sections = [
        {
            "number": "1",
            "title": "Risk Management",
            "content": "This section establishes risk assessment procedures for the organization."
        },
        {
            "number": "2",
            "title": "Scope",
            "content": "This policy applies to all employees."
        },
        {
            "number": "3",
            "title": "Roles",
            "content": "The CISO is responsible for risk management oversight."
        },
    ]
    
    # Execute map phase
    evidence_snippets = _map_sections_for_subcategory(
        policy_sections=policy_sections,
        sub_id="GV.RM-01",
        sub_description="Risk management strategy is established"
    )
    
    # Verify: Should have made 3 sequential LLM calls (one per section)
    assert mock_structured_llm.invoke.call_count == 3
    
    # Verify: Should return only snippets with evidence (2 out of 3)
    assert len(evidence_snippets) == 2
    assert "Section 1 mentions risk assessment procedures." in evidence_snippets
    assert "Section 3 defines risk management roles." in evidence_snippets
    assert "None found" not in evidence_snippets


@pytest.mark.integration
@patch('agents.nist_gap_agents.create_llm')
def test_map_phase_skips_short_sections(mock_create_llm):
    """
    Test that map phase skips sections shorter than _MIN_SECTION_CHARS.
    
    **Validates: Requirements 2.4**
    """
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm
    
    mock_structured_llm.invoke.return_value = SectionEvidenceResult(
        has_evidence=True,
        evidence_snippet="Evidence found"
    )
    
    # Test data: 1 meaningful section + 2 short sections (headers/TOC)
    policy_sections = [
        {
            "number": "1",
            "title": "Purpose",
            "content": "Short"  # Only 5 chars - below _MIN_SECTION_CHARS (80)
        },
        {
            "number": "2",
            "title": "Risk Management",
            "content": "This section establishes comprehensive risk assessment procedures for the organization."
        },
        {
            "number": "3",
            "title": "TOC",
            "content": "Table of Contents"  # Only 17 chars
        },
    ]
    
    # Execute map phase
    evidence_snippets = _map_sections_for_subcategory(
        policy_sections=policy_sections,
        sub_id="GV.RM-01",
        sub_description="Risk management strategy"
    )
    
    # Verify: Should have made only 1 LLM call (skipped 2 short sections)
    assert mock_structured_llm.invoke.call_count == 1


@pytest.mark.integration
@patch('agents.nist_gap_agents.create_llm')
def test_map_phase_handles_empty_sections(mock_create_llm):
    """
    Test that map phase handles empty or None content gracefully.
    
    **Validates: Requirements 2.4**
    """
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm
    
    # Test data: sections with empty/None content
    policy_sections = [
        {"number": "1", "title": "Empty", "content": ""},
        {"number": "2", "title": "None", "content": None},
        {"number": "3", "title": "Whitespace", "content": "   \n\n   "},
    ]
    
    # Execute map phase
    evidence_snippets = _map_sections_for_subcategory(
        policy_sections=policy_sections,
        sub_id="GV.RM-01",
        sub_description="Risk management"
    )
    
    # Verify: Should make no LLM calls (all sections too short)
    assert mock_structured_llm.invoke.call_count == 0
    assert len(evidence_snippets) == 0


# ============================================================================
# Integration Tests for Reduce Phase
# ============================================================================

@pytest.mark.integration
@patch('src.agents.nist_gap_agents.get_framework_excerpt')
def test_reduce_phase_evidence_concatenation(mock_framework):
    """
    Test that reduce phase receives concatenated evidence snippets from map phase.
    
    **Validates: Requirements 2.2, 2.3**
    """
    # Setup mock
    mock_framework.return_value = "Framework guidance for risk management..."
    
    # Mock LLM
    mock_structured_llm = MagicMock()
    mock_structured_llm.invoke.return_value = SubcategoryAssessment(
        subcategory_id="GV.RM-01",
        title="Risk Management Strategy",
        status="Addressed",
        evidence="Combined evidence from multiple sections",
        gap="None - fully addressed",
        recommendation="No action needed"
    )
    
    # Test data: subcategory config and evidence snippets
    sub = {
        "id": "GV.RM-01",
        "category": "Risk Management",
        "description": "Risk management strategy is established",
        "guidance": "Organizations should establish a risk management strategy",
        "questions": ["Is there a risk management strategy?"],
        "policies": ["Risk Management Policy"]
    }
    
    evidence_snippets = [
        "Section 1 mentions risk assessment procedures.",
        "Section 3 defines risk management roles.",
        "Section 5 establishes risk appetite and tolerance levels."
    ]
    
    # Execute reduce phase
    result = _reduce_to_assessment(
        sub=sub,
        evidence_snippets=evidence_snippets,
        framework_excerpt="Framework guidance...",
        structured_llm=mock_structured_llm
    )
    
    # Verify: LLM was called
    assert mock_structured_llm.invoke.call_count == 1
    
    # Verify: Prompt contains all evidence snippets
    call_args = mock_structured_llm.invoke.call_args[0][0]
    assert "Snippet 1: Section 1 mentions risk assessment procedures." in call_args
    assert "Snippet 2: Section 3 defines risk management roles." in call_args
    assert "Snippet 3: Section 5 establishes risk appetite and tolerance levels." in call_args
    
    # Verify: Result is a SubcategoryAssessment
    assert isinstance(result, SubcategoryAssessment)
    assert result.subcategory_id == "GV.RM-01"


@pytest.mark.integration
@patch('src.agents.nist_gap_agents.get_framework_excerpt')
def test_reduce_phase_no_evidence(mock_framework):
    """
    Test reduce phase when no evidence snippets are found.
    
    **Validates: Requirements 2.3**
    """
    # Setup mock
    mock_framework.return_value = "Framework guidance..."
    
    # Mock LLM
    mock_structured_llm = MagicMock()
    mock_structured_llm.invoke.return_value = SubcategoryAssessment(
        subcategory_id="GV.RM-02",
        title="Risk Appetite",
        status="Not Addressed",
        evidence="None found",
        gap="No risk appetite statement found in policy",
        recommendation="Add risk appetite section"
    )
    
    # Test data: subcategory with no evidence
    sub = {
        "id": "GV.RM-02",
        "category": "Risk Appetite",
        "description": "Risk appetite is defined",
        "guidance": "Organizations should define risk appetite",
        "questions": ["Is risk appetite defined?"],
        "policies": ["Risk Management Policy"]
    }
    
    evidence_snippets = []  # No evidence found
    
    # Execute reduce phase
    result = _reduce_to_assessment(
        sub=sub,
        evidence_snippets=evidence_snippets,
        framework_excerpt="Framework guidance...",
        structured_llm=mock_structured_llm
    )
    
    # Verify: Prompt indicates no evidence found
    call_args = mock_structured_llm.invoke.call_args[0][0]
    assert "No relevant passages were found" in call_args
    
    # Verify: Result indicates not addressed
    assert result.status == "Not Addressed"
    assert result.evidence == "None found"


# ============================================================================
# Integration Tests for Complete Map-Reduce Flow
# ============================================================================

@pytest.mark.integration
@patch('agents.nist_gap_agents.create_llm')
@patch('src.agents.nist_gap_agents.get_framework_excerpt')
def test_complete_map_reduce_flow(mock_framework, mock_create_llm):
    """
    Test complete map-reduce data flow from sections to assessment.
    
    **Validates: Requirements 2.2, 2.3, 2.4**
    """
    # Setup mocks
    mock_framework.return_value = "Framework guidance for access control..."
    
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm
    
    # Map phase responses (3 sections)
    map_responses = [
        SectionEvidenceResult(
            has_evidence=True,
            evidence_snippet="Section 2 requires MFA for all users."
        ),
        SectionEvidenceResult(
            has_evidence=False,
            evidence_snippet="None found"
        ),
        SectionEvidenceResult(
            has_evidence=True,
            evidence_snippet="Section 4 mandates role-based access control."
        ),
    ]
    
    # Reduce phase response
    reduce_response = SubcategoryAssessment(
        subcategory_id="PR.AA-01",
        title="Identity Management",
        status="Partially Addressed",
        evidence="MFA and RBAC are mentioned but not fully detailed",
        gap="Missing identity lifecycle management procedures",
        recommendation="Add identity provisioning and deprovisioning procedures"
    )
    
    # Configure mock to return map responses first, then reduce response
    mock_structured_llm.invoke.side_effect = map_responses + [reduce_response]
    
    # Test data
    policy_sections = [
        {
            "number": "2",
            "title": "Authentication",
            "content": "All users must use multi-factor authentication for system access."
        },
        {
            "number": "3",
            "title": "Scope",
            "content": "This policy applies to all employees and contractors."
        },
        {
            "number": "4",
            "title": "Access Control",
            "content": "Role-based access control must be implemented for all systems."
        },
    ]
    
    sub = {
        "id": "PR.AA-01",
        "category": "Identity Management",
        "description": "Identities and credentials are managed",
        "guidance": "Organizations should manage identity lifecycle",
        "questions": ["Are identities managed?"],
        "policies": ["Access Control Policy"]
    }
    
    # Execute map phase
    evidence_snippets = _map_sections_for_subcategory(
        policy_sections=policy_sections,
        sub_id=sub["id"],
        sub_description=sub["description"]
    )
    
    # Verify map phase results
    assert len(evidence_snippets) == 2
    assert "Section 2 requires MFA for all users." in evidence_snippets
    assert "Section 4 mandates role-based access control." in evidence_snippets
    
    # Execute reduce phase
    result = _reduce_to_assessment(
        sub=sub,
        evidence_snippets=evidence_snippets,
        framework_excerpt="Framework guidance...",
        structured_llm=mock_structured_llm
    )
    
    # Verify reduce phase results
    assert result.subcategory_id == "PR.AA-01"
    assert result.status == "Partially Addressed"
    assert "MFA and RBAC" in result.evidence
    
    # Verify total LLM calls: 3 map + 1 reduce = 4
    assert mock_structured_llm.invoke.call_count == 4


@pytest.mark.integration
@patch('agents.nist_gap_agents.create_llm')
@patch('src.agents.nist_gap_agents.get_framework_excerpt')
def test_map_reduce_with_mocked_models(mock_framework, mock_create_llm):
    """
    Test map-reduce flow using mocked SectionEvidenceResult and SubcategoryAssessment.
    
    **Validates: Requirements 2.2, 2.3**
    """
    # Setup mocks
    mock_framework.return_value = "Framework excerpt..."
    
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm
    
    # Create mock responses using actual Pydantic models
    map_result_1 = SectionEvidenceResult(
        has_evidence=True,
        evidence_snippet="Evidence from section 1"
    )
    map_result_2 = SectionEvidenceResult(
        has_evidence=True,
        evidence_snippet="Evidence from section 2"
    )
    
    reduce_result = SubcategoryAssessment(
        subcategory_id="GV.OC-01",
        title="Organizational Context",
        status="Addressed",
        evidence="Combined evidence from sections 1 and 2",
        gap="None - fully addressed",
        recommendation="No action needed"
    )
    
    mock_structured_llm.invoke.side_effect = [map_result_1, map_result_2, reduce_result]
    
    # Test data
    policy_sections = [
        {
            "number": "1",
            "title": "Purpose",
            "content": "This policy establishes the organizational context for information security."
        },
        {
            "number": "2",
            "title": "Scope",
            "content": "This policy applies to all organizational units and stakeholders."
        },
    ]
    
    sub = {
        "id": "GV.OC-01",
        "category": "Organizational Context",
        "description": "Organizational context is understood",
        "guidance": "Organizations should understand their context",
        "questions": ["Is organizational context defined?"],
        "policies": ["Governance Policy"]
    }
    
    # Execute map-reduce
    evidence = _map_sections_for_subcategory(
        policy_sections=policy_sections,
        sub_id=sub["id"],
        sub_description=sub["description"]
    )
    
    assessment = _reduce_to_assessment(
        sub=sub,
        evidence_snippets=evidence,
        framework_excerpt="Framework...",
        structured_llm=mock_structured_llm
    )
    
    # Verify results
    assert len(evidence) == 2
    assert assessment.subcategory_id == "GV.OC-01"
    assert assessment.status == "Addressed"
    assert mock_structured_llm.invoke.call_count == 3

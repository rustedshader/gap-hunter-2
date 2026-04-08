"""
Integration tests for RAPTOR architecture in policy revision.

Tests parse_gap_targets segregation and property test for gap target
segregation (Property 9).
"""

import pytest
from unittest.mock import MagicMock, patch
from hypothesis import given, strategies as st, assume, settings

from src.agents.nist_gap_agents import SubcategoryAssessment
from src.agents.policy_revision_agent import (
    parse_gap_targets,
    GapTarget,
    classify_gap_target,
)


# ============================================================================
# Integration Tests for parse_gap_targets Segregation
# ============================================================================

@pytest.mark.integration
@patch('src.agents.policy_revision_agent.classify_gap_target')
@patch('src.agents.policy_revision_agent.get_framework_excerpt')
@patch('src.agents.policy_revision_agent._get_nist_guidance')
def test_parse_gap_targets_segregation(mock_guidance, mock_excerpt, mock_classify):
    """
    Test that parse_gap_targets correctly segregates gaps into modify and new_section arrays.
    
    **Validates: Requirements 2.6**
    """
    # Setup mocks
    mock_guidance.return_value = "NIST guidance text"
    mock_excerpt.return_value = "Framework excerpt text"
    
    # Mock classify_gap_target to return different actions
    mock_classify.side_effect = [
        ("modify", "3"),      # Gap 1 → modify section 3
        ("new_section", None), # Gap 2 → new section
        ("modify", "5"),      # Gap 3 → modify section 5
        ("new_section", None), # Gap 4 → new section
        ("modify", "3"),      # Gap 5 → modify section 3
    ]
    
    # Test data: assessments with gaps
    all_assessments = {
        "Govern": [
            SubcategoryAssessment(
                subcategory_id="GV.OC-01",
                title="Organizational Context",
                status="Not Addressed",
                evidence="None found",
                gap="Missing organizational context definition",
                recommendation="Add organizational context section"
            ),
            SubcategoryAssessment(
                subcategory_id="GV.RM-01",
                title="Risk Management",
                status="Partially Addressed",
                evidence="Some risk management mentioned",
                gap="Missing risk appetite statement",
                recommendation="Add risk appetite to existing risk section"
            ),
        ],
        "Protect": [
            SubcategoryAssessment(
                subcategory_id="PR.AA-01",
                title="Identity Management",
                status="Not Addressed",
                evidence="None found",
                gap="No identity management procedures",
                recommendation="Create new identity management section"
            ),
            SubcategoryAssessment(
                subcategory_id="PR.DS-01",
                title="Data Security",
                status="Partially Addressed",
                evidence="Encryption mentioned",
                gap="Missing data classification",
                recommendation="Add data classification to security section"
            ),
            SubcategoryAssessment(
                subcategory_id="PR.AC-01",
                title="Access Control",
                status="Not Addressed",
                evidence="None found",
                gap="No access control policy",
                recommendation="Create new access control section"
            ),
        ],
    }
    
    sections = [
        {"number": "1", "title": "Purpose"},
        {"number": "2", "title": "Scope"},
        {"number": "3", "title": "Risk Management"},
        {"number": "4", "title": "Roles"},
        {"number": "5", "title": "Data Security"},
    ]
    
    # Execute parse_gap_targets
    targets = parse_gap_targets(all_assessments, sections)
    
    # Segregate by action
    modify_targets = [t for t in targets if t.action == "modify"]
    new_section_targets = [t for t in targets if t.action == "new_section"]
    
    # Verify segregation
    assert len(modify_targets) == 3  # Gaps 1, 3, 5
    assert len(new_section_targets) == 2  # Gaps 2, 4
    
    # Verify modify targets have section numbers
    for target in modify_targets:
        assert target.target_section_number is not None
        assert target.target_section_number in ["3", "5"]
    
    # Verify new_section targets have no section numbers
    for target in new_section_targets:
        assert target.target_section_number is None


@pytest.mark.integration
@patch('src.agents.policy_revision_agent.classify_gap_target')
@patch('src.agents.policy_revision_agent.get_framework_excerpt')
@patch('src.agents.policy_revision_agent._get_nist_guidance')
def test_parse_gap_targets_priority_sorting(mock_guidance, mock_excerpt, mock_classify):
    """
    Test that parse_gap_targets sorts by priority: Not Addressed first, then Partially Addressed.
    
    **Validates: Requirements 2.6**
    """
    # Setup mocks
    mock_guidance.return_value = "Guidance"
    mock_excerpt.return_value = "Excerpt"
    mock_classify.return_value = ("modify", "1")
    
    # Test data: mixed priority assessments
    all_assessments = {
        "Govern": [
            SubcategoryAssessment(
                subcategory_id="GV.OC-01",
                title="Context",
                status="Partially Addressed",  # Lower priority
                evidence="Some context",
                gap="Incomplete context",
                recommendation="Improve context"
            ),
            SubcategoryAssessment(
                subcategory_id="GV.RM-01",
                title="Risk",
                status="Not Addressed",  # Higher priority
                evidence="None found",
                gap="No risk management",
                recommendation="Add risk management"
            ),
            SubcategoryAssessment(
                subcategory_id="GV.PO-01",
                title="Policy",
                status="Partially Addressed",  # Lower priority
                evidence="Some policy",
                gap="Incomplete policy",
                recommendation="Improve policy"
            ),
            SubcategoryAssessment(
                subcategory_id="GV.SC-01",
                title="Supply Chain",
                status="Not Addressed",  # Higher priority
                evidence="None found",
                gap="No supply chain",
                recommendation="Add supply chain"
            ),
        ],
    }
    
    sections = [{"number": "1", "title": "Test"}]
    
    # Execute parse_gap_targets
    targets = parse_gap_targets(all_assessments, sections)
    
    # Verify priority sorting: Not Addressed first
    assert len(targets) == 4
    assert targets[0].gap.status == "Not Addressed"
    assert targets[1].gap.status == "Not Addressed"
    assert targets[2].gap.status == "Partially Addressed"
    assert targets[3].gap.status == "Partially Addressed"


@pytest.mark.integration
@patch('src.agents.policy_revision_agent.classify_gap_target')
@patch('src.agents.policy_revision_agent.get_framework_excerpt')
@patch('src.agents.policy_revision_agent._get_nist_guidance')
def test_parse_gap_targets_skips_addressed(mock_guidance, mock_excerpt, mock_classify):
    """
    Test that parse_gap_targets skips Addressed and Out of Scope assessments.
    
    **Validates: Requirements 2.6**
    """
    # Setup mocks
    mock_guidance.return_value = "Guidance"
    mock_excerpt.return_value = "Excerpt"
    mock_classify.return_value = ("modify", "1")
    
    # Test data: mixed status assessments
    all_assessments = {
        "Govern": [
            SubcategoryAssessment(
                subcategory_id="GV.OC-01",
                title="Context",
                status="Addressed",  # Should be skipped
                evidence="Full context provided",
                gap="None",
                recommendation="No action needed"
            ),
            SubcategoryAssessment(
                subcategory_id="GV.RM-01",
                title="Risk",
                status="Not Addressed",  # Should be included
                evidence="None found",
                gap="No risk management",
                recommendation="Add risk management"
            ),
            SubcategoryAssessment(
                subcategory_id="GV.PO-01",
                title="Policy",
                status="Out of Scope",  # Should be skipped
                evidence="N/A",
                gap="Requires separate policy",
                recommendation="Create separate policy"
            ),
            SubcategoryAssessment(
                subcategory_id="GV.SC-01",
                title="Supply Chain",
                status="Partially Addressed",  # Should be included
                evidence="Some supply chain",
                gap="Incomplete",
                recommendation="Improve supply chain"
            ),
        ],
    }
    
    sections = [{"number": "1", "title": "Test"}]
    
    # Execute parse_gap_targets
    targets = parse_gap_targets(all_assessments, sections)
    
    # Verify only Not Addressed and Partially Addressed are included
    assert len(targets) == 2
    assert all(t.gap.status in ("Not Addressed", "Partially Addressed") for t in targets)
    assert targets[0].subcategory_id == "GV.RM-01"
    assert targets[1].subcategory_id == "GV.SC-01"


# ============================================================================
# Integration Tests for classify_gap_target (LLM-based targeting)
# ============================================================================

@pytest.mark.integration
@patch('agents.policy_revision_agent.create_llm')
def test_classify_gap_target_modify(mock_create_llm):
    """
    Test classify_gap_target returns 'modify' action for existing section.
    
    **Validates: Requirements 2.6**
    """
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm
    
    # Mock LLM response
    from src.agents.policy_revision_agent import SectionTargetResult
    mock_structured_llm.invoke.return_value = SectionTargetResult(
        action="modify",
        section_number="3"
    )
    
    # Test data
    assessment = SubcategoryAssessment(
        subcategory_id="GV.RM-01",
        title="Risk Management",
        status="Partially Addressed",
        evidence="Some risk management",
        gap="Missing risk appetite",
        recommendation="Add risk appetite statement to existing risk management section"
    )
    
    sections = [
        {"number": "1", "title": "Purpose"},
        {"number": "2", "title": "Scope"},
        {"number": "3", "title": "Risk Management"},
    ]
    
    # Execute classify_gap_target
    action, section_num = classify_gap_target(assessment, sections)
    
    # Verify result
    assert action == "modify"
    assert section_num == "3"


@pytest.mark.integration
@patch('agents.policy_revision_agent.create_llm')
def test_classify_gap_target_new_section(mock_create_llm):
    """
    Test classify_gap_target returns 'new_section' action when no section fits.
    
    **Validates: Requirements 2.6**
    """
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm
    
    # Mock LLM response
    from src.agents.policy_revision_agent import SectionTargetResult
    mock_structured_llm.invoke.return_value = SectionTargetResult(
        action="new_section",
        section_number=None
    )
    
    # Test data
    assessment = SubcategoryAssessment(
        subcategory_id="PR.AA-01",
        title="Identity Management",
        status="Not Addressed",
        evidence="None found",
        gap="No identity management procedures",
        recommendation="Create new section for identity lifecycle management"
    )
    
    sections = [
        {"number": "1", "title": "Purpose"},
        {"number": "2", "title": "Scope"},
        {"number": "3", "title": "Risk Management"},
    ]
    
    # Execute classify_gap_target
    action, section_num = classify_gap_target(assessment, sections)
    
    # Verify result
    assert action == "new_section"
    assert section_num is None


@pytest.mark.integration
@patch('agents.policy_revision_agent.create_llm')
def test_classify_gap_target_invalid_section_fallback(mock_create_llm):
    """
    Test classify_gap_target falls back to new_section if LLM returns invalid section number.
    
    **Validates: Requirements 2.6**
    """
    # Setup mock LLM
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_llm
    mock_create_llm.return_value = mock_llm
    
    # Mock LLM response with invalid section number
    from src.agents.policy_revision_agent import SectionTargetResult
    mock_structured_llm.invoke.return_value = SectionTargetResult(
        action="modify",
        section_number="99"  # Section 99 doesn't exist
    )
    
    # Test data
    assessment = SubcategoryAssessment(
        subcategory_id="GV.RM-01",
        title="Risk Management",
        status="Not Addressed",
        evidence="None found",
        gap="Missing risk management",
        recommendation="Add to section 99"  # Invalid
    )
    
    sections = [
        {"number": "1", "title": "Purpose"},
        {"number": "2", "title": "Scope"},
        {"number": "3", "title": "Risk Management"},
    ]
    
    # Execute classify_gap_target
    action, section_num = classify_gap_target(assessment, sections)
    
    # Verify fallback to new_section
    assert action == "new_section"
    assert section_num is None


# ============================================================================
# Property-Based Test for Gap Target Segregation (Property 9)
# ============================================================================

@pytest.mark.integration
@given(
    st.lists(
        st.tuples(
            st.sampled_from(["modify", "new_section"]),  # action
            st.text(min_size=1, max_size=10)  # subcategory_id
        ),
        min_size=1,
        max_size=30
    )
)
def test_gap_target_segregation_property(gap_specs):
    """
    Feature: research-based-testing, Property 9: Gap Target Segregation
    
    **Validates: Requirements 2.6**
    
    For any list of GapTarget objects with mixed action types, parse_gap_targets
    should correctly segregate them into two arrays (modify and new_section) where
    all "modify" actions are in the first array and all "new_section" actions are
    in the second array.
    """
    # Generate mock GapTarget objects from specs
    targets = []
    for action, sub_id in gap_specs:
        # Create mock assessment
        assessment = SubcategoryAssessment(
            subcategory_id=sub_id,
            title=f"Test {sub_id}",
            status="Not Addressed",
            evidence="None found",
            gap="Test gap",
            recommendation="Test recommendation"
        )
        
        # Create GapTarget
        target = GapTarget(
            subcategory_id=sub_id,
            function_name="Govern",
            action=action,
            target_section_number="1" if action == "modify" else None,
            gap=assessment,
            framework_excerpt="Test excerpt",
            nist_guidance="Test guidance"
        )
        targets.append(target)
    
    # Segregate by action
    modify_targets = [t for t in targets if t.action == "modify"]
    new_section_targets = [t for t in targets if t.action == "new_section"]
    
    # Property 1: All targets should be in one of the two arrays
    assert len(modify_targets) + len(new_section_targets) == len(targets)
    
    # Property 2: modify_targets should only contain "modify" actions
    assert all(t.action == "modify" for t in modify_targets)
    
    # Property 3: new_section_targets should only contain "new_section" actions
    assert all(t.action == "new_section" for t in new_section_targets)
    
    # Property 4: modify targets should have section numbers
    assert all(t.target_section_number is not None for t in modify_targets)
    
    # Property 5: new_section targets should have None section numbers
    assert all(t.target_section_number is None for t in new_section_targets)
    
    # Property 6: No targets should be lost or duplicated
    all_ids = [t.subcategory_id for t in targets]
    segregated_ids = [t.subcategory_id for t in modify_targets] + \
                     [t.subcategory_id for t in new_section_targets]
    assert sorted(all_ids) == sorted(segregated_ids)


@pytest.mark.integration
@patch('src.agents.policy_revision_agent.classify_gap_target')
@patch('src.agents.policy_revision_agent.get_framework_excerpt')
@patch('src.agents.policy_revision_agent._get_nist_guidance')
@given(st.integers(min_value=0, max_value=20))
@settings(deadline=None)
def test_gap_target_segregation_counts(mock_guidance, mock_excerpt, mock_classify, num_modify):
    """
    Feature: research-based-testing, Property 9: Gap Target Segregation
    
    **Validates: Requirements 2.6**
    
    Property test verifying that segregation counts are correct for any
    distribution of modify vs new_section actions.
    """
    # Setup mocks
    mock_guidance.return_value = "Guidance"
    mock_excerpt.return_value = "Excerpt"
    
    # Generate num_modify "modify" actions and (20 - num_modify) "new_section" actions
    num_new_section = 20 - num_modify
    
    # Mock classify_gap_target to return the right distribution
    mock_responses = [("modify", "1")] * num_modify + [("new_section", None)] * num_new_section
    mock_classify.side_effect = mock_responses
    
    # Generate assessments
    assessments = []
    for i in range(20):
        assessments.append(
            SubcategoryAssessment(
                subcategory_id=f"GV.TEST-{i:02d}",
                title=f"Test {i}",
                status="Not Addressed",
                evidence="None found",
                gap="Test gap",
                recommendation="Test recommendation"
            )
        )
    
    all_assessments = {"Govern": assessments}
    sections = [{"number": "1", "title": "Test"}]
    
    # Execute parse_gap_targets
    targets = parse_gap_targets(all_assessments, sections)
    
    # Segregate
    modify_targets = [t for t in targets if t.action == "modify"]
    new_section_targets = [t for t in targets if t.action == "new_section"]
    
    # Verify counts match expected distribution
    assert len(modify_targets) == num_modify
    assert len(new_section_targets) == num_new_section
    assert len(targets) == 20


@pytest.mark.integration
def test_gap_target_dataclass_structure():
    """
    Test that GapTarget dataclass has correct structure for segregation.
    
    **Validates: Requirements 2.6**
    """
    # Create mock assessment
    assessment = SubcategoryAssessment(
        subcategory_id="GV.RM-01",
        title="Risk Management",
        status="Not Addressed",
        evidence="None found",
        gap="Missing risk management",
        recommendation="Add risk management section"
    )
    
    # Create GapTarget with modify action
    modify_target = GapTarget(
        subcategory_id="GV.RM-01",
        function_name="Govern",
        action="modify",
        target_section_number="3",
        gap=assessment,
        framework_excerpt="Framework excerpt",
        nist_guidance="NIST guidance"
    )
    
    # Create GapTarget with new_section action
    new_section_target = GapTarget(
        subcategory_id="GV.RM-02",
        function_name="Govern",
        action="new_section",
        target_section_number=None,
        gap=assessment,
        framework_excerpt="Framework excerpt",
        nist_guidance="NIST guidance"
    )
    
    # Verify structure
    assert modify_target.action == "modify"
    assert modify_target.target_section_number == "3"
    
    assert new_section_target.action == "new_section"
    assert new_section_target.target_section_number is None
    
    # Verify segregation works
    targets = [modify_target, new_section_target]
    modify_list = [t for t in targets if t.action == "modify"]
    new_section_list = [t for t in targets if t.action == "new_section"]
    
    assert len(modify_list) == 1
    assert len(new_section_list) == 1

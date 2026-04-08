"""
Shared pytest fixtures for all test phases.

Provides reusable fixtures for mocking LLMs, generating test data,
and loading golden dataset policies.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import json
import pytest

# Add src directory to Python path so imports work correctly
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.models import ExtractedSection, IncompleteSection


class GoldenPolicy:
    """Golden dataset policy with ground truth annotations."""
    
    def __init__(self, path: Path, content: str, ground_truth: dict):
        self.path = path
        self.content = content
        self.policy_type = ground_truth.get("type", "Unknown")
        self.expected_functions = ground_truth.get("expected_functions", [])
        self.ground_truth_gaps = ground_truth.get("ground_truth_gaps", {})


@pytest.fixture
def mock_llm():
    """Configurable mock LLM for integration tests."""
    with patch('src.llm.create_llm') as mock:
        yield mock


@pytest.fixture
def sample_sections():
    """Representative ExtractedSection objects for testing."""
    return [
        ExtractedSection(
            number="1",
            title="Purpose",
            content="This policy establishes the framework for information security management.",
            start_line=1,
            end_line=10,
            is_complete=True
        ),
        ExtractedSection(
            number="2",
            title="Scope",
            content="This policy applies to all employees, contractors, and third-party users.",
            start_line=11,
            end_line=20,
            is_complete=True
        ),
        ExtractedSection(
            number="3",
            title="Roles and Responsibilities",
            content="The CISO is responsible for overall information security governance.",
            start_line=21,
            end_line=35,
            is_complete=True
        ),
    ]


@pytest.fixture
def sample_assessments():
    """Representative SubcategoryAssessment objects for testing."""
    # Import here to avoid circular dependencies
    from src.agents.schemas import SubcategoryAssessment
    
    return [
        SubcategoryAssessment(
            subcategory_id="GV.OC-01",
            title="Organizational Context",
            status="Addressed",
            evidence="Section 2 states that this policy applies to all employees and contractors.",
            gap="None - fully addressed",
            recommendation="No action needed"
        ),
        SubcategoryAssessment(
            subcategory_id="GV.RM-02",
            title="Risk Management Strategy",
            status="Partially Addressed",
            evidence="Section 3 mentions CISO responsibilities but lacks detail on risk assessment.",
            gap="Missing formal risk assessment process",
            recommendation="Add detailed risk assessment procedures"
        ),
    ]


@pytest.fixture
def golden_policy_loader():
    """Load golden dataset PDFs with ground truth annotations."""
    def loader(filename: str):
        path = Path("tests/golden_dataset") / filename
        ground_truth_path = Path("tests/golden_dataset") / "ground_truth.json"
        
        if not path.exists():
            raise FileNotFoundError(f"Golden dataset policy not found: {path}")
        
        if not ground_truth_path.exists():
            raise FileNotFoundError(f"Ground truth file not found: {ground_truth_path}")
        
        # Load ground truth
        ground_truth_data = json.loads(ground_truth_path.read_text())
        policy_ground_truth = ground_truth_data.get(filename, {})
        
        # Load policy content using pdf_to_markdown
        try:
            from src.tools.pdf import pdf_to_markdown
            content = pdf_to_markdown(path)
        except Exception as e:
            # Fallback to mock content if PDF extraction fails
            content = f"Mock content for {filename}"
        
        return GoldenPolicy(
            path=path,
            content=content,
            ground_truth=policy_ground_truth
        )
    
    return loader

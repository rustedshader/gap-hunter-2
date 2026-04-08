# Research-Based Testing Framework

This directory contains the comprehensive 4-phase testing framework for the gap-hunter-2 policy analysis system.

## Overview

The testing framework implements a pyramid approach with four distinct test phases:

1. **Unit Tests** - Fast deterministic tests (<5s total) for core logic validation
2. **Integration Tests** - Tests (<30s) validating multi-agent architecture with mocked LLMs
3. **E2E Tests** - End-to-end tests with golden dataset using real LLM calls
4. **Adversarial Tests** - Robustness tests validating system behavior under corrupted/malicious inputs

## Directory Structure

```
tests/
├── unit/                    # Fast deterministic tests
├── integration/             # Mocked LLM tests
├── e2e/                     # Real LLM tests (nightly)
├── adversarial/             # Robustness tests (nightly)
├── golden_dataset/          # Curated test policies
├── utils/                   # Test utilities and generators
├── reports/                 # Generated test reports (gitignored)
├── conftest.py             # Shared pytest fixtures
└── README.md               # This file
```

## Quick Start

### Running All Unit Tests

```bash
PYTHONPATH=. uv run pytest -m "unit" tests/
```

### Running All Integration Tests

```bash
PYTHONPATH=. uv run pytest -m "integration" tests/
```

### Running Fast CI Tests (Unit + Integration)

```bash
PYTHONPATH=. uv run pytest -m "unit or integration" tests/ \
  --cov=src \
  --cov-report=html:tests/reports/coverage/fast-ci \
  --html=tests/reports/pytest/fast-ci.html
```

### Running E2E Tests (Expensive - Real LLM Calls)

```bash
PYTHONPATH=. uv run pytest -m "golden or adversarial" tests/ \
  --cov=src \
  --cov-report=html:tests/reports/coverage/nightly \
  --html=tests/reports/pytest/nightly.html
```

### Running All Tests

```bash
PYTHONPATH=. uv run pytest tests/ \
  --cov=src \
  --cov-report=html:tests/reports/coverage/full \
  --cov-report=xml:tests/reports/coverage/coverage.xml \
  --html=tests/reports/pytest/full.html
```

## Test Markers

The framework uses pytest markers to categorize tests:

- `@pytest.mark.unit` - Fast deterministic unit tests without external dependencies
- `@pytest.mark.integration` - Integration tests with mocked LLM responses
- `@pytest.mark.llm` - Tests that make real LLM calls (expensive)
- `@pytest.mark.golden` - Golden dataset E2E tests
- `@pytest.mark.adversarial` - Adversarial and resilience tests

## Writing Tests

### Unit Test Example

```python
import pytest
from src.models import ExtractedSection

@pytest.mark.unit
def test_section_creation():
    """Test ExtractedSection creation."""
    section = ExtractedSection(
        number="1",
        title="Purpose",
        content="Test content",
        start_line=1,
        end_line=10,
        is_complete=True
    )
    
    assert section.number == "1"
    assert section.title == "Purpose"
```

### Integration Test Example

```python
import pytest
from unittest.mock import MagicMock

@pytest.mark.integration
def test_map_reduce_flow(mock_llm):
    """Test map-reduce evidence collection."""
    # Configure mock
    mock_llm.return_value = MagicMock(
        has_evidence=True,
        evidence_snippet="Test evidence"
    )
    
    # Test logic here
    assert True
```

### Property-Based Test Example

```python
import pytest
from hypothesis import given, strategies as st

@pytest.mark.unit
@given(st.integers(min_value=1, max_value=100))
def test_section_numbering_property(section_count):
    """
    Feature: research-based-testing, Property 5: Sequential Renumbering
    
    For any list of ExtractedSection objects, renumbering should
    produce sections numbered sequentially starting from 1.
    """
    # Test logic here
    assert True
```

## Using Fixtures

The framework provides several shared fixtures in `conftest.py`:

### mock_llm

Configurable mock LLM for integration tests:

```python
@pytest.mark.integration
def test_with_mock_llm(mock_llm):
    mock_llm.return_value = "Mocked response"
    # Test logic
```

### sample_sections

Representative ExtractedSection objects:

```python
@pytest.mark.unit
def test_with_sample_sections(sample_sections):
    assert len(sample_sections) == 3
    # Test logic
```

### sample_assessments

Representative SubcategoryAssessment objects:

```python
@pytest.mark.unit
def test_with_sample_assessments(sample_assessments):
    assert len(sample_assessments) == 2
    # Test logic
```

### golden_policy_loader

Load golden dataset policies with ground truth:

```python
@pytest.mark.golden
@pytest.mark.llm
def test_with_golden_policy(golden_policy_loader):
    policy = golden_policy_loader("policy_1.pdf")
    # Test logic
```

## Test Utilities

The `tests/utils/generators.py` module provides utilities for generating synthetic test data:

### generate_fake_section

```python
from tests.utils.generators import generate_fake_section

section = generate_fake_section(
    number="1.1",
    title="Test Section",
    content_length=500,
    start_line=5
)
```

### generate_fake_assessment

```python
from tests.utils.generators import generate_fake_assessment

assessment = generate_fake_assessment(
    subcategory_id="GV.OC-01",
    status="Addressed"
)
```

### Hypothesis Strategies

```python
from hypothesis import given
from tests.utils.generators import st_extracted_section, st_assessment

@given(st_extracted_section())
def test_with_random_section(section):
    # Test logic with randomly generated section
    pass
```

## Test Reports

All test reports are generated in `tests/reports/` and are excluded from version control.

See `tests/reports/README.md` for detailed information about:
- Coverage reports
- E2E test reports
- Metrics reports
- Pytest HTML reports

## CI/CD Integration

The framework integrates with GitHub Actions through three workflows:

1. **Fast CI Pipeline** (`.github/workflows/test-fast.yml`)
   - Runs on every push and PR
   - Executes unit + integration tests only
   - Duration: <2 minutes

2. **Nightly E2E Pipeline** (`.github/workflows/test-nightly.yml`)
   - Runs on schedule (2 AM UTC)
   - Executes golden dataset + adversarial tests
   - Duration: 30-60 minutes

3. **Manual Full Test Pipeline** (`.github/workflows/test-full.yml`)
   - Manually triggered via workflow_dispatch
   - Executes all test phases
   - Duration: 45-75 minutes

## Dependencies

All test dependencies are managed via `uv` and defined in `pyproject.toml`:

- `pytest` - Testing framework
- `pytest-cov` - Coverage measurement
- `pytest-mock` - Mocking utilities
- `pytest-html` - HTML report generation
- `hypothesis` - Property-based testing
- `deepeval` - LLM-as-a-judge evaluation

To install test dependencies:

```bash
uv add --optional test pytest pytest-cov pytest-mock pytest-html hypothesis deepeval
```

## Coverage Requirements

- **Fast CI Pipeline**: Minimum 70% coverage for unit + integration tests
- **Full Test Pipeline**: Minimum 80% coverage for all tests

## Best Practices

1. **Write both unit tests and property tests** - They complement each other
2. **Use descriptive test names** - Explain what is being tested
3. **Keep unit tests fast** - No file I/O, no LLM calls, no network requests
4. **Mock external dependencies** - Use fixtures and mocks for integration tests
5. **Tag tests appropriately** - Use pytest markers for selective execution
6. **Document property tests** - Reference design document properties in comments
7. **Use hypothesis for randomized testing** - Minimum 100 iterations per property

## Troubleshooting

### Import Errors

If you encounter `ModuleNotFoundError: No module named 'src'`, run tests with:

```bash
PYTHONPATH=. uv run pytest tests/
```

### Marker Warnings

If you see "Unknown pytest.mark.X" warnings, ensure markers are registered in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "unit: Fast deterministic unit tests",
    "integration: Integration tests with mocked LLMs",
    # ... other markers
]
```

### Coverage Too Low

Review the coverage report to identify untested code:

```bash
open tests/reports/coverage/fast-ci/index.html
```

## Related Documentation

- **Requirements**: `.kiro/specs/research-based-testing/requirements.md`
- **Design**: `.kiro/specs/research-based-testing/design.md`
- **Tasks**: `.kiro/specs/research-based-testing/tasks.md`
- **Reports**: `tests/reports/README.md`
- **Golden Dataset**: `tests/golden_dataset/README.md` (to be created)

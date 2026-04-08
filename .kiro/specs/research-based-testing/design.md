# Design Document: Research-Based Testing Framework

## Overview

This design specifies a comprehensive 4-phase testing framework for the gap-hunter-2 policy analysis system. The framework implements deterministic unit tests, integration tests with mocked LLMs, golden dataset E2E tests with LLM-as-a-judge evaluation, and adversarial resilience testing, all integrated with GitHub Actions CI/CD pipelines.

The testing strategy follows a pyramid approach:
- **Base layer**: Fast deterministic unit tests (<5s total) for core logic validation
- **Middle layer**: Integration tests (<30s) validating multi-agent architecture with mocked LLMs
- **Upper layer**: E2E tests with golden dataset using real LLM calls and LLM-judge evaluation
- **Top layer**: Adversarial tests validating robustness against corrupted/malicious inputs

The framework uses pytest as the testing foundation with custom markers for selective test execution across different CI/CD pipelines (fast CI on every commit, nightly E2E tests, manual full test runs).

## Architecture

### System Context

Gap-hunter-2 is a policy engine that performs gap analysis on cybersecurity policies aligned with ISO, NIST, or other industry frameworks against the CIS MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024). The system consists of three main phases:

1. **Phase 1: Policy Extraction** - Multi-agent sliding-window extraction with validation loops
2. **Phase 2: Gap Analysis** - Map-reduce architecture with scope classification and evidence collection
3. **Phase 3: Policy Revision** - RAPTOR + CoVe architecture for gap remediation

### Testing Architecture

The testing framework mirrors the system's three-phase architecture with specialized test suites for each phase:

```
tests/
├── unit/                    # Fast deterministic tests (<5s total)
│   ├── test_pdf_utils.py   # PDF parsing utilities
│   ├── test_extractor.py   # Section extraction logic
│   ├── test_models.py      # Pydantic model serialization
│   └── test_gap_analyzer.py # Gap analysis utilities
├── integration/             # Mocked LLM tests (<30s total)
│   ├── test_map_reduce.py  # Map-reduce flow validation
│   ├── test_multi_agent.py # Agent interaction patterns
│   └── test_raptor.py      # RAPTOR data flow
├── e2e/                     # Real LLM tests (nightly)
│   ├── test_golden_dataset.py
│   └── test_llm_judge.py
├── adversarial/             # Robustness tests (nightly)
│   ├── test_corrupted_inputs.py
│   └── test_hallucination_defense.py
├── golden_dataset/          # Curated test policies
│   ├── policy_1.pdf
│   ├── policy_2.pdf
│   ├── ...
│   ├── ground_truth.json
│   └── README.md
├── reports/                 # Generated test reports (gitignored)
│   ├── coverage/           # HTML coverage reports
│   ├── e2e/                # E2E test result reports
│   ├── metrics/            # Metrics JSON files
│   ├── pytest/             # Pytest HTML reports
│   ├── index.html          # Summary dashboard
│   └── README.md           # Report documentation
├── utils/                   # Test utilities
│   └── generators.py       # Synthetic data generators
└── conftest.py             # Shared fixtures
```

### CI/CD Pipeline Architecture

Three GitHub Actions workflows provide different testing coverage:

1. **Fast CI Pipeline** (`.github/workflows/test-fast.yml`)
   - Triggers: Every push and pull request
   - Runs: Unit tests + Integration tests only
   - Duration: <2 minutes
   - Markers: `pytest -m "unit or integration"`

2. **Nightly E2E Pipeline** (`.github/workflows/test-nightly.yml`)
   - Triggers: Scheduled cron (2 AM UTC)
   - Runs: Golden dataset E2E + Adversarial tests
   - Duration: ~30-60 minutes
   - Markers: `pytest -m "golden or adversarial"`
   - Uses: Local gemma-4-E2B-it-Q8_0.gguf model

3. **Manual Full Test Pipeline** (`.github/workflows/test-full.yml`)
   - Triggers: Manual workflow_dispatch
   - Runs: All test phases
   - Duration: ~45-75 minutes
   - Markers: `pytest tests/` (no filter)

## Components and Interfaces

### Test Phase Components

#### 1. Unit Test Suite

**Purpose**: Validate core logic without external dependencies (no LLM calls, no file I/O)

**Key Components**:
- `test_pdf_utils.py`: Tests for `_decode_mt_codes`, PDF validation
- `test_extractor.py`: Tests for `build_windows`, `_dedup_sections`, `_remove_overlapping_sections`, `_renumber_sections`
- `test_models.py`: Pydantic model serialization round-trip tests
- `test_gap_analyzer.py`: Tests for `build_consolidated_report`, `create_combined_policy_content`

**Mocking Strategy**:
- Mock `docling.DocumentConverter` to avoid file I/O
- Use synthetic `ExtractedSection` and `SubcategoryAssessment` objects
- No LLM mocking needed (pure logic tests)

**Interface**:
```python
# Example unit test structure
@pytest.mark.unit
def test_decode_mt_codes():
    """Test /MT font code decoding."""
    input_text = "/MT73/MT110/MT102/MT111"
    expected = "Info"
    assert _decode_mt_codes(input_text) == expected

@pytest.mark.unit
def test_build_windows():
    """Test sliding window generation."""
    lines = [(i, f"line {i}") for i in range(1, 101)]
    windows = list(build_windows(lines, window_size=80, overlap=20))
    assert len(windows) == 2  # (100 - 80) / (80 - 20) + 1
```

#### 2. Integration Test Suite

**Purpose**: Validate multi-agent architecture plumbing with mocked LLM responses

**Key Components**:
- `test_map_reduce.py`: Map-reduce flow validation
- `test_multi_agent.py`: Extractor → Validator → Corrector interaction
- `test_raptor.py`: RAPTOR data flow in Policy_Reviser

**Mocking Strategy**:
- Use `unittest.mock` to mock LLM responses
- Mock `SectionEvidenceResult` for map phase
- Mock `SubcategoryAssessment` for reduce phase
- Verify correct data flow between agents

**Interface**:
```python
# Example integration test structure
@pytest.mark.integration
def test_map_reduce_flow(mock_llm):
    """Test map-reduce evidence collection and assessment."""
    # Mock map phase responses
    mock_llm.return_value = SectionEvidenceResult(
        has_evidence=True,
        evidence_snippet="Test evidence"
    )
    
    # Execute map phase
    evidence = _map_sections_for_subcategory(sections, "GV.OC-01", "desc")
    
    # Verify reduce receives concatenated evidence
    assert len(evidence) > 0
    assert "Test evidence" in evidence[0]
```

#### 3. Golden Dataset E2E Test Suite

**Purpose**: End-to-end validation with real LLM calls and statistical rigor

**Key Components**:
- `test_golden_dataset.py`: Full pipeline tests on curated policies
- `test_llm_judge.py`: LLM-as-a-judge evaluation

**Golden Dataset Structure**:
```json
{
  "policies": [
    {
      "filename": "policy_1.pdf",
      "type": "Risk Management Policy",
      "expected_functions": ["Govern", "Identify"],
      "ground_truth_gaps": {
        "GV.OC-01": "Not Addressed",
        "GV.RM-02": "Partially Addressed",
        "ID.RA-01": "Addressed"
      }
    }
  ]
}
```

**LLM Judge Evaluation**:
- **Faithfulness Score**: Evidence quotes exist in original policy
- **Framework Alignment Score**: Revised policy aligns with CIS MS-ISAC templates
- **Completeness Score**: Roadmap covers all identified gaps

**Interface**:
```python
@pytest.mark.golden
@pytest.mark.llm
def test_golden_policy_classification(golden_policy_loader):
    """Test function classification on golden dataset."""
    policy = golden_policy_loader("policy_1.pdf")
    result = classify_policy_functions(policy.content)
    
    # Calculate F1-Score against ground truth
    f1 = calculate_f1_score(result, policy.expected_functions)
    assert f1 >= 0.85  # 85% accuracy threshold
```

#### 4. Adversarial Test Suite

**Purpose**: Validate system robustness against corrupted or malicious inputs

**Key Components**:
- `test_corrupted_inputs.py`: Corrupted PDFs, malformed data
- `test_hallucination_defense.py`: Safeguards against LLM hallucinations

**Test Scenarios**:
- Out-of-scope documents (e.g., "Corporate Catering Menu.pdf")
- Extractor returning >20 sections (hallucination trigger)
- Corrupted PDF files
- Malformed /MT codes
- Sections exceeding context limits

**Interface**:
```python
@pytest.mark.adversarial
def test_max_sections_safeguard(mock_llm):
    """Test MAX_SECTIONS_PER_WINDOW safeguard."""
    # Force extractor to return 25 fake sections
    mock_llm.return_value = ExtractionResult(
        sections=[fake_section() for _ in range(25)]
    )
    
    result = extract_sections_from_chunk(...)
    
    # Verify safeguard triggers and discards hallucinated sections
    assert len(result.sections) == 0
```

### Shared Test Infrastructure

#### Fixtures (conftest.py)

```python
@pytest.fixture
def mock_llm():
    """Configurable mock LLM for integration tests."""
    with patch('llm.create_llm') as mock:
        yield mock

@pytest.fixture
def sample_sections():
    """Representative ExtractedSection objects."""
    return [
        ExtractedSection(
            number="1",
            title="Purpose",
            content="This policy establishes...",
            start_line=1,
            end_line=10,
            is_complete=True
        ),
        # ... more sections
    ]

@pytest.fixture
def sample_assessments():
    """Representative SubcategoryAssessment objects."""
    return [
        SubcategoryAssessment(
            subcategory_id="GV.OC-01",
            title="Organizational Context",
            status="Addressed",
            evidence="Section 2 states...",
            gap="None - fully addressed",
            recommendation="No action needed"
        ),
        # ... more assessments
    ]

@pytest.fixture
def golden_policy_loader():
    """Load golden dataset PDFs with ground truth."""
    def loader(filename: str):
        path = Path("tests/golden_dataset") / filename
        ground_truth = json.loads(
            (Path("tests/golden_dataset") / "ground_truth.json").read_text()
        )
        return GoldenPolicy(
            path=path,
            content=pdf_to_markdown(path),
            ground_truth=ground_truth[filename]
        )
    return loader
```

#### Test Utilities (utils/generators.py)

```python
def generate_fake_section(
    number: str = "1",
    title: str = "Test Section",
    content_length: int = 500
) -> ExtractedSection:
    """Generate synthetic ExtractedSection for testing."""
    return ExtractedSection(
        number=number,
        title=title,
        content="Lorem ipsum " * (content_length // 12),
        start_line=1,
        end_line=20,
        is_complete=True
    )

def generate_fake_assessment(
    subcategory_id: str = "GV.OC-01",
    status: str = "Addressed"
) -> SubcategoryAssessment:
    """Generate synthetic SubcategoryAssessment for testing."""
    return SubcategoryAssessment(
        subcategory_id=subcategory_id,
        title="Test Subcategory",
        status=status,
        evidence="Test evidence",
        gap="Test gap",
        recommendation="Test recommendation"
    )
```

## Data Models

### Test Data Models

```python
class GoldenPolicy(BaseModel):
    """Golden dataset policy with ground truth annotations."""
    path: Path
    content: str
    policy_type: str
    expected_functions: list[str]
    ground_truth_gaps: dict[str, str]  # subcategory_id → status

class TestMetrics(BaseModel):
    """Test execution metrics."""
    timestamp: datetime
    test_phase: str  # "unit", "integration", "e2e", "adversarial"
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration_seconds: float
    coverage_percent: float | None = None

class E2EMetrics(BaseModel):
    """E2E test quality metrics."""
    timestamp: datetime
    policy_name: str
    f1_score: float  # Classification accuracy
    faithfulness_score: float  # Evidence groundedness
    alignment_score: float  # Framework alignment
    completeness_score: float  # Roadmap completeness
```

### Existing System Models (Tested)

The framework tests these existing Pydantic models:

- `ExtractedSection`: Policy section with boundaries
- `IncompleteSection`: Carry-over for spanning sections
- `ChunkResult`: Extraction result from one window
- `SectionSummary`: Master list summary
- `SubcategoryAssessment`: Gap analysis result
- `GapTarget`: Policy revision target
- `AdditionBlock`: RAPTOR addition block
- `ClusterSummary`: RAPTOR cluster summary
- `IntegrationResult`: Section integration result
- `SectionRevision`: New section creation result


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: MT Code Decoding Round-Trip

*For any* valid ASCII character in the printable range (32-126), encoding it as an /MT code pattern and then decoding should produce the original character.

**Validates: Requirements 1.2**

### Property 2: Sliding Window Coverage

*For any* list of document lines and valid window parameters (window_size > overlap > 0), the generated windows should cover all lines with no gaps, maintain proper overlap between consecutive windows, and have correct boundary calculations.

**Validates: Requirements 1.4**

### Property 3: Deduplication Preserves Uniqueness

*For any* list of ExtractedSection objects (including duplicates based on start_line), deduplication should produce a list where each start_line appears exactly once, preserving the section with the widest range for each start_line.

**Validates: Requirements 1.5**

### Property 4: Overlap Removal Preserves Non-Overlapping Sections

*For any* list of ExtractedSection objects, removing overlapping sections should produce a list where no section's range overlaps with another, keeping parent sections when nested sections are detected.

**Validates: Requirements 1.6**

### Property 5: Sequential Renumbering

*For any* list of ExtractedSection objects with arbitrary numbering, renumbering should produce sections numbered sequentially starting from 1, preserving the original order based on start_line.

**Validates: Requirements 1.7**

### Property 6: Consolidated Report Completeness

*For any* valid mapping of NIST functions to SubcategoryAssessment lists, the consolidated report should contain sections for all six NIST functions, correct aggregate counts matching the input data, and properly formatted tables.

**Validates: Requirements 1.8**

### Property 7: Pydantic Model Serialization Round-Trip

*For any* valid instance of any Pydantic model in the system (ExtractedSection, SubcategoryAssessment, ChunkResult, GapTarget, etc.), serializing via model_dump() and deserializing via parse_obj() should produce an equivalent object.

**Validates: Requirements 1.10, 12.1, 12.2, 12.3, 12.4, 12.5**

### Property 8: Content Truncation at Limit

*For any* text content of any length, truncation to _CONTENT_CHAR_LIMIT (12000 characters) should produce output of exactly 12000 characters when input exceeds the limit, or unchanged output when input is below the limit.

**Validates: Requirements 2.5, 4.5**

### Property 9: Gap Target Segregation

*For any* list of GapTarget objects with mixed action types, parse_gap_targets should correctly segregate them into two arrays (modify and new_section) where all "modify" actions are in the first array and all "new_section" actions are in the second array.

**Validates: Requirements 2.6**

### Property 10: Section Overflow Safeguard

*For any* extraction result containing more than MAX_SECTIONS_PER_WINDOW (20) sections, the safeguard should trigger and discard all sections, returning an empty list to prevent hallucination propagation.

**Validates: Requirements 2.9, 4.2, 4.7**

### Property 11: Evidence Grounding

*For any* SubcategoryAssessment with a non-empty evidence field (not "None found" or "N/A"), the evidence text should exist as a substring in the original policy document markdown.

**Validates: Requirements 3.4, 4.6**

### Property 12: MT Code Error Handling

*For any* malformed /MT code pattern (invalid format, out-of-range codes, incomplete patterns), the _decode_mt_codes function should handle it gracefully without raising exceptions, returning either the original text or a best-effort decode.

**Validates: Requirements 4.4**

## Error Handling

### Unit Test Error Handling

- **Invalid Inputs**: Unit tests should verify that functions raise appropriate exceptions (ValueError, TypeError) for invalid inputs
- **Boundary Conditions**: Tests should cover edge cases like empty lists, single-element lists, maximum values
- **Mock Failures**: Tests should handle mock setup failures gracefully with clear error messages

### Integration Test Error Handling

- **LLM Mock Failures**: Integration tests should handle mock LLM failures and verify error propagation
- **Agent Communication Failures**: Tests should verify proper error handling when agents fail to communicate
- **Data Flow Interruptions**: Tests should verify system behavior when data flow is interrupted

### E2E Test Error Handling

- **LLM Call Failures**: E2E tests should implement retry logic for transient LLM failures
- **Golden Dataset Issues**: Tests should fail fast with clear messages if golden dataset is corrupted
- **Metric Calculation Failures**: Tests should log warnings but not fail if optional metrics cannot be calculated

### Adversarial Test Error Handling

- **Graceful Degradation**: System should degrade gracefully under adversarial inputs, not crash
- **Error Logging**: All adversarial test failures should be logged with detailed context
- **Recovery Mechanisms**: Tests should verify system can recover from adversarial inputs

## Testing Strategy

### Dual Testing Approach

The framework implements both unit tests and property-based tests as complementary strategies:

- **Unit tests**: Verify specific examples, edge cases, and error conditions with concrete test cases
- **Property tests**: Verify universal properties across all inputs using randomized test generation
- **Together**: Provide comprehensive coverage where unit tests catch concrete bugs and property tests verify general correctness

### Property-Based Testing Configuration

**Library Selection**: Use `hypothesis` for Python property-based testing

**Test Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must reference its design document property via comment tag
- Tag format: `# Feature: research-based-testing, Property {number}: {property_text}`

**Example Property Test Structure**:
```python
from hypothesis import given, strategies as st

@pytest.mark.unit
@given(st.integers(min_value=32, max_value=126))
def test_mt_code_round_trip(ascii_code):
    """
    Feature: research-based-testing, Property 1: MT Code Decoding Round-Trip
    
    For any valid ASCII character in the printable range (32-126),
    encoding it as an /MT code pattern and then decoding should
    produce the original character.
    """
    # Encode
    encoded = f"/MT{ascii_code}"
    
    # Decode
    decoded = _decode_mt_codes(encoded)
    
    # Verify round-trip
    assert decoded == chr(ascii_code)
```

### Unit Testing Balance

- Unit tests focus on specific examples that demonstrate correct behavior
- Property tests handle comprehensive input coverage through randomization
- Unit tests should NOT duplicate property test coverage
- Unit tests should focus on:
  - Integration points between components
  - Specific edge cases not easily generated
  - Error conditions with specific error messages
  - Mock verification and call patterns

### Test Execution Strategy

**Fast CI Pipeline** (every commit):
- Runs: Unit tests + Integration tests
- Duration: <2 minutes
- Purpose: Immediate feedback on code changes
- Command: `pytest -m "unit or integration" --cov=src --cov-report=html:tests/reports/coverage/fast-ci --html=tests/reports/pytest/fast-ci.html`

**Nightly E2E Pipeline** (scheduled):
- Runs: Golden dataset E2E + Adversarial tests
- Duration: 30-60 minutes
- Purpose: Comprehensive quality validation
- Command: `pytest -m "golden or adversarial" --cov=src --cov-report=html:tests/reports/coverage/nightly --html=tests/reports/pytest/nightly.html`
- Uses: Local gemma-4-E2B-it-Q8_0.gguf model

**Manual Full Test Pipeline** (on-demand):
- Runs: All test phases
- Duration: 45-75 minutes
- Purpose: Pre-release validation
- Command: `pytest tests/ --cov=src --cov-report=html:tests/reports/coverage/full --cov-report=xml:tests/reports/coverage/coverage.xml --html=tests/reports/pytest/full.html`

### Report Generation Strategy

**Coverage Reports**:
- Generated in `tests/reports/coverage/` with subdirectories per pipeline type
- HTML format for human review, XML format for CI integration
- Includes line-by-line coverage highlighting and summary statistics

**Pytest HTML Reports**:
- Generated using pytest-html plugin in `tests/reports/pytest/`
- Includes test execution times, pass/fail status, and error details
- Self-contained HTML files for easy sharing

**E2E Test Reports**:
- Generated in `tests/reports/e2e/` with timestamp-based subdirectories
- Includes LLM judge scores, F1 metrics, and detailed test results
- JSON format for programmatic access, HTML for human review

**Metrics Reports**:
- Saved to `tests/reports/metrics/` with timestamp-based filenames
- Includes historical trends and degradation alerts
- Generated charts saved as PNG images

**Summary Dashboard**:
- `tests/reports/index.html` provides overview of all reports
- Links to latest coverage, pytest, E2E, and metrics reports
- Auto-generated after each test run

### Coverage Requirements

- **Fast CI Pipeline**: Minimum 70% coverage for unit + integration tests
- **Full Test Pipeline**: Minimum 80% coverage for all tests
- **Coverage Exclusions**: Test files, `__pycache__`, migration scripts

### Test Data Strategy

**Synthetic Data Generation**:
- Use `hypothesis` strategies for property test data generation
- Use `tests/utils/generators.py` for complex object generation
- Ensure generated data is realistic and covers edge cases

**Golden Dataset Management**:
- Maintain 5 curated PDF policies representing different policy types
- Update ground_truth.json when policies are added/modified
- Document policy selection criteria in `tests/golden_dataset/README.md`

**Mock Data Strategy**:
- Use `unittest.mock` for LLM mocking in integration tests
- Create reusable mock fixtures in `conftest.py`
- Ensure mocks return realistic data structures

### Continuous Improvement

**Metrics Tracking**:
- Save test metrics to `metrics.json` after each nightly run
- Append metrics with timestamp to historical log file
- Track trends: F1-Score, Faithfulness Score, Alignment Score, Coverage

**Metric Analysis**:
- Use `scripts/analyze_metrics.py` to visualize metric trends
- Generate metric trend charts as CI artifacts
- Alert if any metric degrades by >5% compared to 7-day average

**Test Maintenance**:
- Review and update golden dataset quarterly
- Add new property tests when bugs are discovered
- Refactor tests to reduce duplication and improve clarity


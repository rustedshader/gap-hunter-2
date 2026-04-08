# Requirements Document

## Introduction

This document specifies requirements for a comprehensive research-based testing framework for the gap-hunter-2 policy analysis system. The framework implements a 4-phase testing approach (deterministic unit tests, integration tests with mocked LLMs, golden dataset E2E tests with LLM-as-a-judge evaluation, and adversarial resilience testing) integrated with GitHub Actions CI/CD pipelines.

Gap-hunter-2 is a policy engine that performs gap analysis on cybersecurity policies aligned with ISO, NIST, or other industry frameworks against the CIS MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024).

## Glossary

- **Test_Framework**: The complete testing system including all test phases, fixtures, and utilities
- **Unit_Test**: Fast, deterministic test that executes in milliseconds without LLM calls
- **Integration_Test**: Test that validates multi-agent architecture with mocked LLM responses
- **E2E_Test**: End-to-end test using real LLM calls against golden dataset
- **LLM_Judge**: LLM-based evaluation system (DeepEval or Ragas) that assesses output quality
- **Golden_Dataset**: Curated collection of 5 PDF policies with ground truth annotations
- **Adversarial_Test**: Test that validates system robustness against corrupted or malicious inputs
- **CI_Pipeline**: GitHub Actions workflow that runs on every commit/PR
- **Nightly_Pipeline**: GitHub Actions workflow scheduled to run expensive tests overnight
- **Pytest**: Python testing framework used for all test execution
- **Coverage_Report**: Test coverage analysis showing code execution percentage
- **Map_Phase**: Sequential LLM calls scanning policy sections for evidence
- **Reduce_Phase**: LLM call that assesses subcategory using collected evidence
- **RAPTOR**: Recursive Abstractive Processing for Tree-Organized Retrieval architecture
- **CoVe**: Chain-of-Verification validation pattern
- **Extractor_Agent**: Agent that identifies section boundaries from policy documents
- **Validator_Agent**: Agent that verifies extraction correctness
- **Corrector_Agent**: Agent that fixes extraction errors
- **Gap_Analyzer**: Orchestrator that runs NIST function agents for gap analysis
- **Policy_Reviser**: Phase 3 orchestrator using RAPTOR + CoVe for policy revision

## Requirements

### Requirement 1: Deterministic Unit Testing Foundation

**User Story:** As a developer, I want fast deterministic unit tests that execute without LLM calls, so that I can validate core logic in milliseconds during development.

#### Acceptance Criteria

1. THE Test_Framework SHALL execute all Unit_Tests in less than 5 seconds total
2. WHEN testing _decode_mt_codes function, THE Test_Framework SHALL verify correct decoding of anomalous /MT string patterns
3. WHEN testing _decode_mt_codes with non-PDF inputs, THE Test_Framework SHALL verify ValueError is raised
4. WHEN testing build_windows function, THE Test_Framework SHALL verify sliding window logic with window_size=80 and overlap=20
5. WHEN testing _dedup_sections function, THE Test_Framework SHALL verify duplicate removal using mock ExtractedSection data
6. WHEN testing _remove_overlapping_sections function, THE Test_Framework SHALL verify nested section filtering with mock data
7. WHEN testing _renumber_sections function, THE Test_Framework SHALL verify sequential renumbering with mock data
8. WHEN testing build_consolidated_report function, THE Test_Framework SHALL verify report generation using synthetic SubcategoryAssessment objects
9. THE Test_Framework SHALL mock docling DocumentConverter to avoid file I/O in Unit_Tests
10. FOR ALL Unit_Tests, parsing then printing then parsing SHALL produce equivalent objects (round-trip property)

### Requirement 2: Integration Testing with Mocked LLMs

**User Story:** As a developer, I want integration tests that validate multi-agent architecture plumbing without expensive LLM calls, so that I can verify handoffs and data flow quickly.

#### Acceptance Criteria

1. THE Test_Framework SHALL complete all Integration_Tests in less than 30 seconds
2. WHEN testing map-reduce flow, THE Test_Framework SHALL mock SectionEvidenceResult responses
3. WHEN testing map-reduce flow, THE Test_Framework SHALL verify _reduce_to_assessment receives concatenated evidence snippets
4. WHEN testing Map_Phase, THE Test_Framework SHALL verify N sections result in N sequential LLM calls
5. WHEN testing create_combined_policy_content with sections exceeding 12000 characters, THE Test_Framework SHALL verify truncation to _CONTENT_CHAR_LIMIT
6. WHEN testing RAPTOR data flow in Policy_Reviser, THE Test_Framework SHALL verify parse_gap_targets segregates into modify and new_section arrays
7. THE Test_Framework SHALL use unittest.mock for all LLM mocking in Integration_Tests
8. WHEN testing multi-agent validation loops, THE Test_Framework SHALL verify Extractor_Agent, Validator_Agent, and Corrector_Agent interaction patterns
9. THE Test_Framework SHALL verify MAX_SECTIONS_PER_WINDOW safeguard triggers when Extractor_Agent returns more than 20 sections

### Requirement 3: Golden Dataset E2E Testing

**User Story:** As a QA engineer, I want end-to-end tests with statistical rigor using a curated golden dataset, so that I can measure system accuracy and groundedness objectively.

#### Acceptance Criteria

1. THE Test_Framework SHALL maintain a golden dataset directory at tests/golden_dataset/ containing 5 curated PDF policies
2. THE Test_Framework SHALL maintain ground_truth.json mapping exact NIST gaps for each golden dataset policy
3. WHEN running classify_policy_functions on golden dataset, THE Test_Framework SHALL calculate F1-Score for scope classification accuracy
4. WHEN running E2E_Tests, THE LLM_Judge SHALL verify evidence field in SubcategoryAssessment exists in original policy Markdown
5. WHEN evaluating revised_policy.md, THE LLM_Judge SHALL grade Framework Alignment Score against CIS MS-ISAC templates
6. WHEN evaluating improvement_roadmap.md, THE LLM_Judge SHALL verify completeness and actionability
7. THE Test_Framework SHALL use DeepEval or Ragas for LLM_Judge evaluation
8. THE Test_Framework SHALL generate statistical metrics including F1-Score, Faithfulness Score, and Alignment Score
9. THE Test_Framework SHALL use local gemma-4-E2B-it-Q8_0.gguf model for nightly E2E_Tests

### Requirement 4: Adversarial and Resilience Testing

**User Story:** As a security engineer, I want adversarial tests that validate system robustness against corrupted or malicious inputs, so that I can ensure the system fails gracefully.

#### Acceptance Criteria

1. WHEN injecting out-of-scope document like "Corporate Catering Menu.pdf", THE Test_Framework SHALL verify classify_policy_functions returns empty or Out of Scope
2. WHEN forcing Extractor_Agent to return 25 fake sections, THE Test_Framework SHALL verify MAX_SECTIONS_PER_WINDOW safeguard triggers
3. WHEN testing with corrupted PDF files, THE Test_Framework SHALL verify pdf_to_markdown raises ValueError
4. WHEN testing with malformed /MT codes, THE Test_Framework SHALL verify _decode_mt_codes handles errors gracefully
5. WHEN testing with sections exceeding context limits, THE Test_Framework SHALL verify truncation prevents system crashes
6. THE Test_Framework SHALL verify hallucination defense mechanisms catch fabricated evidence
7. THE Test_Framework SHALL verify section overflow safeguards prevent memory exhaustion

### Requirement 5: Test Organization and Structure

**User Story:** As a developer, I want a well-organized test directory structure with clear separation of concerns, so that I can easily locate and maintain tests.

#### Acceptance Criteria

1. THE Test_Framework SHALL organize tests into tests/unit/, tests/integration/, tests/e2e/, tests/adversarial/, and tests/golden_dataset/ directories
2. THE Test_Framework SHALL use pytest as the testing framework
3. THE Test_Framework SHALL tag Unit_Tests with @pytest.mark.unit marker
4. THE Test_Framework SHALL tag Integration_Tests with @pytest.mark.integration marker
5. THE Test_Framework SHALL tag E2E_Tests with @pytest.mark.llm marker
6. THE Test_Framework SHALL tag Golden_Dataset tests with @pytest.mark.golden marker
7. THE Test_Framework SHALL tag Adversarial_Tests with @pytest.mark.adversarial marker
8. THE Test_Framework SHALL provide conftest.py with shared fixtures for all test phases

### Requirement 6: GitHub Actions Fast CI Pipeline

**User Story:** As a developer, I want a fast CI pipeline that runs on every commit, so that I get immediate feedback on code changes without waiting for expensive LLM tests.

#### Acceptance Criteria

1. THE CI_Pipeline SHALL execute on every push and pull request event
2. THE CI_Pipeline SHALL run only Unit_Tests and Integration_Tests (excluding LLM-based tests)
3. THE CI_Pipeline SHALL fail if any Unit_Test or Integration_Test fails
4. THE CI_Pipeline SHALL generate Coverage_Report and upload to CI artifacts
5. THE CI_Pipeline SHALL complete in less than 2 minutes
6. THE CI_Pipeline SHALL use uv package manager for dependency installation
7. THE CI_Pipeline SHALL be defined in .github/workflows/test-fast.yml
8. THE CI_Pipeline SHALL run pytest with markers: pytest -m "unit or integration"

### Requirement 7: GitHub Actions Nightly E2E Pipeline

**User Story:** As a QA engineer, I want a nightly pipeline that runs expensive LLM-based tests against the golden dataset, so that I can detect regressions without slowing down development.

#### Acceptance Criteria

1. THE Nightly_Pipeline SHALL execute on a scheduled cron trigger (nightly at 2 AM UTC)
2. THE Nightly_Pipeline SHALL run Golden_Dataset E2E_Tests and Adversarial_Tests
3. THE Nightly_Pipeline SHALL use local gemma-4-E2B-it-Q8_0.gguf model for LLM calls
4. THE Nightly_Pipeline SHALL generate statistical metrics (F1-Score, Faithfulness Score, Alignment Score)
5. THE Nightly_Pipeline SHALL upload test results and metrics as CI artifacts
6. THE Nightly_Pipeline SHALL send notifications on test failures
7. THE Nightly_Pipeline SHALL be defined in .github/workflows/test-nightly.yml
8. THE Nightly_Pipeline SHALL run pytest with markers: pytest -m "golden or adversarial"

### Requirement 8: GitHub Actions Manual Full Test Pipeline

**User Story:** As a release manager, I want a manually triggered workflow that runs all test phases, so that I can validate the complete system before releases.

#### Acceptance Criteria

1. THE Test_Framework SHALL provide a manual workflow trigger via workflow_dispatch
2. WHEN manually triggered, THE Test_Framework SHALL run all Unit_Tests, Integration_Tests, E2E_Tests, and Adversarial_Tests
3. THE Test_Framework SHALL generate comprehensive Coverage_Report for all test phases
4. THE Test_Framework SHALL upload all test results, metrics, and coverage reports as CI artifacts
5. THE Test_Framework SHALL be defined in .github/workflows/test-full.yml
6. THE Test_Framework SHALL run pytest without marker filters: pytest tests/

### Requirement 9: Test Coverage and Reporting

**User Story:** As a tech lead, I want comprehensive test coverage reports, so that I can identify untested code paths and improve test quality.

#### Acceptance Criteria

1. THE Test_Framework SHALL use pytest-cov for coverage measurement
2. THE Test_Framework SHALL generate Coverage_Report in HTML and XML formats
3. THE Test_Framework SHALL measure coverage for src/ directory excluding __pycache__ and test files
4. THE Test_Framework SHALL upload Coverage_Report to CI artifacts for all pipeline runs
5. THE Test_Framework SHALL display coverage summary in CI logs
6. THE Test_Framework SHALL fail CI_Pipeline if coverage drops below 70% for Unit_Tests and Integration_Tests

### Requirement 10: Dependency Management with uv

**User Story:** As a developer, I want all test dependencies managed through uv package manager, so that I maintain consistency with the project's dependency management approach.

#### Acceptance Criteria

1. THE Test_Framework SHALL use uv for installing pytest and all test dependencies
2. THE Test_Framework SHALL add pytest, pytest-cov, pytest-mock, and unittest.mock to pyproject.toml via uv
3. THE Test_Framework SHALL add DeepEval or Ragas to pyproject.toml via uv for LLM_Judge functionality
4. THE Test_Framework SHALL document all test dependencies in pyproject.toml [project.optional-dependencies] under "test" group
5. THE CI_Pipeline SHALL install test dependencies using: uv pip install -e ".[test]"

### Requirement 11: Test Fixtures and Utilities

**User Story:** As a developer, I want reusable test fixtures and utilities, so that I can write tests efficiently without duplicating setup code.

#### Acceptance Criteria

1. THE Test_Framework SHALL provide mock_llm fixture that returns configurable mock LLM responses
2. THE Test_Framework SHALL provide sample_sections fixture with representative ExtractedSection objects
3. THE Test_Framework SHALL provide sample_assessments fixture with representative SubcategoryAssessment objects
4. THE Test_Framework SHALL provide golden_policy_loader fixture that loads golden dataset PDFs
5. THE Test_Framework SHALL provide ground_truth_loader fixture that loads ground_truth.json annotations
6. THE Test_Framework SHALL define all shared fixtures in tests/conftest.py
7. THE Test_Framework SHALL provide utility functions for generating synthetic test data in tests/utils/generators.py

### Requirement 12: Parser and Serializer Round-Trip Testing

**User Story:** As a developer, I want round-trip property tests for all parsers and serializers, so that I can ensure data integrity through serialization cycles.

#### Acceptance Criteria

1. WHEN testing ExtractedSection serialization, THE Test_Framework SHALL verify model_dump then parse produces equivalent object
2. WHEN testing SubcategoryAssessment serialization, THE Test_Framework SHALL verify JSON serialization round-trip preserves all fields
3. WHEN testing ChunkResult serialization, THE Test_Framework SHALL verify round-trip property for complete and incomplete sections
4. WHEN testing GapTarget parsing, THE Test_Framework SHALL verify parse_gap_targets output can be serialized and deserialized without loss
5. FOR ALL Pydantic models, THE Test_Framework SHALL verify round-trip property: parse(dump(obj)) == obj

### Requirement 13: Test Documentation and Examples

**User Story:** As a new contributor, I want clear test documentation and examples, so that I can understand the testing approach and write new tests correctly.

#### Acceptance Criteria

1. THE Test_Framework SHALL provide tests/README.md documenting the 4-phase testing approach
2. THE Test_Framework SHALL document how to run each test phase independently in tests/README.md
3. THE Test_Framework SHALL provide example tests for each test phase in tests/README.md
4. THE Test_Framework SHALL document pytest markers and their usage in tests/README.md
5. THE Test_Framework SHALL document how to add new golden dataset policies in tests/golden_dataset/README.md
6. THE Test_Framework SHALL document LLM_Judge evaluation metrics and thresholds in tests/e2e/README.md

### Requirement 14: Continuous Improvement and Metrics Tracking

**User Story:** As a product manager, I want historical tracking of test metrics, so that I can monitor quality trends over time.

#### Acceptance Criteria

1. THE Nightly_Pipeline SHALL save test metrics (F1-Score, Faithfulness Score, Alignment Score) to metrics.json
2. THE Nightly_Pipeline SHALL append metrics with timestamp to historical log file
3. THE Test_Framework SHALL provide scripts/analyze_metrics.py to visualize metric trends
4. THE Test_Framework SHALL generate metric trend charts as CI artifacts
5. THE Nightly_Pipeline SHALL alert if any metric degrades by more than 5% compared to 7-day average

### Requirement 15: Test Reports and Documentation

**User Story:** As a developer or QA engineer, I want comprehensive test reports and documentation generated after test runs, so that I can easily review test results, coverage, and quality metrics.

#### Acceptance Criteria

1. THE Test_Framework SHALL create tests/reports/ directory for storing all generated test reports
2. WHEN running any test phase, THE Test_Framework SHALL generate HTML coverage reports in tests/reports/coverage/
3. WHEN running E2E tests, THE Test_Framework SHALL generate detailed test result reports in tests/reports/e2e/
4. WHEN running nightly tests, THE Test_Framework SHALL save metrics.json to tests/reports/metrics/
5. THE Test_Framework SHALL generate pytest HTML reports using pytest-html plugin in tests/reports/pytest/
6. THE Test_Framework SHALL create tests/reports/README.md documenting report structure and how to interpret results
7. THE Test_Framework SHALL include .gitignore entries to exclude generated reports from version control
8. THE CI_Pipeline SHALL archive tests/reports/ directory as artifacts for download
9. THE Test_Framework SHALL generate timestamp-based subdirectories for each test run to preserve history
10. THE Test_Framework SHALL provide a summary dashboard in tests/reports/index.html linking to all report types


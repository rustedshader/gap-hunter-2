# Implementation Plan: Research-Based Testing Framework

## Overview

This plan implements a comprehensive 4-phase testing framework for gap-hunter-2 using pytest. Tasks are condensed to maximize implementation efficiency while maintaining full coverage.

## Tasks

- [x] 1. Set up complete test infrastructure
  - Create tests/ directory structure: unit/, integration/, e2e/, adversarial/, golden_dataset/, utils/, reports/
  - Create tests/reports/ subdirectories: coverage/, e2e/, metrics/, pytest/
  - Add test dependencies to pyproject.toml: pytest, pytest-cov, pytest-mock, pytest-html, hypothesis, deepeval
  - Install dependencies via: `uv add --optional test pytest pytest-cov pytest-mock pytest-html hypothesis deepeval`
  - Create tests/conftest.py with all shared fixtures: mock_llm, sample_sections, sample_assessments, golden_policy_loader
  - Create tests/utils/generators.py with: generate_fake_section, generate_fake_assessment, hypothesis strategies (st_extracted_section, st_assessment)
  - Create tests/reports/.gitignore to exclude generated reports from version control
  - Create tests/reports/README.md documenting report structure and interpretation
  - _Requirements: 5.1, 5.8, 10.2, 10.3, 10.4, 10.5, 11.1-11.7, 15.1, 15.6, 15.7_


- [x] 2. Implement Phase 1: Complete unit test suite
  - Create tests/unit/test_pdf_utils.py with tests for _decode_mt_codes (valid patterns, invalid input, malformed patterns) + property test for MT code round-trip (Property 1)
  - Create tests/unit/test_extractor.py with tests for build_windows, _dedup_sections, _remove_overlapping_sections, _renumber_sections + property tests for sliding window coverage (Property 2), deduplication uniqueness (Property 3), overlap removal (Property 4), sequential renumbering (Property 5)
  - Create tests/unit/test_models.py with round-trip tests for ExtractedSection, SubcategoryAssessment, ChunkResult, GapTarget + property test for Pydantic model serialization (Property 7)
  - Create tests/unit/test_gap_analyzer.py with tests for build_consolidated_report (structure, counts), create_combined_policy_content (truncation) + property tests for consolidated report completeness (Property 6) and content truncation (Property 8)
  - _Requirements: 1.2-1.10, 2.5, 4.4, 12.1-12.5_

- [x] 3. Implement Phase 2: Complete integration test suite
  - Create tests/integration/test_map_reduce.py with tests for map phase sequential calls, reduce phase evidence concatenation, complete map-reduce data flow using mocked SectionEvidenceResult and SubcategoryAssessment
  - Create tests/integration/test_multi_agent.py with tests for Extractor→Validator→Corrector loop + section overflow safeguard test (Property 10: force 25 sections, verify MAX_SECTIONS_PER_WINDOW triggers)
  - Create tests/integration/test_raptor.py with tests for parse_gap_targets segregation + property test for gap target segregation (Property 9)
  - _Requirements: 2.2-2.4, 2.6, 2.8, 2.9, 4.2, 4.7_

- [x] 4. Set up golden dataset and implement Phase 3: E2E test suite
  - Create tests/golden_dataset/ directory with 5 curated PDF policies (Risk Management, ISMS, Patch Management, etc.)
  - Create ground_truth.json with NIST gap mappings, expected_functions, and ground_truth_gaps for each policy
  - Create tests/golden_dataset/README.md documenting dataset structure, how to add policies, and ground_truth.json schema
  - Create tests/e2e/test_golden_dataset.py with test_classify_policy_functions_accuracy (F1-Score >= 0.85) + full pipeline E2E test
  - Create tests/e2e/test_llm_judge.py with test_evidence_faithfulness (Property 11: evidence grounding) + LLM judge tests for framework alignment and roadmap completeness using DeepEval/Ragas
  - Create tests/e2e/README.md documenting LLM judge metrics and thresholds
  - _Requirements: 3.1-3.8, 4.6, 13.5, 13.6_

- [x] 5. Implement Phase 4: Complete adversarial test suite
  - Create tests/adversarial/test_corrupted_inputs.py with tests for out-of-scope documents, corrupted PDFs, malformed /MT codes, sections exceeding context limits + section overflow test
  - Create tests/adversarial/test_hallucination_defense.py with tests for fabricated evidence detection + graceful degradation under multiple adversarial conditions
  - _Requirements: 4.1-4.7_

- [x] 6. Implement all GitHub Actions CI/CD workflows
  - Create .github/workflows/test-fast.yml: trigger on push/PR, run unit+integration tests, generate coverage report in tests/reports/coverage/fast-ci, generate pytest HTML report, fail if <70% coverage, archive tests/reports/ as artifacts, complete in <2 min
  - Create .github/workflows/test-nightly.yml: cron at 2 AM UTC, run golden+adversarial tests with local gemma-4-E2B-it-Q8_0.gguf, generate metrics (F1, Faithfulness, Alignment), save to tests/reports/metrics/metrics-{timestamp}.json, generate coverage and pytest HTML reports, upload tests/reports/ artifacts, send notifications on failure
  - Create .github/workflows/test-full.yml: manual workflow_dispatch, run all test phases, generate comprehensive coverage report in tests/reports/coverage/full, generate pytest HTML report, upload all tests/reports/ artifacts
  - _Requirements: 6.1-6.8, 7.1-7.8, 8.1-8.6, 9.6, 14.1, 14.2, 15.2, 15.3, 15.4, 15.5, 15.8_

- [x] 7. Implement metrics tracking and create all documentation
  - Create scripts/analyze_metrics.py: load metrics from tests/reports/metrics/, calculate 7-day rolling averages, generate trend charts with matplotlib, detect >5% degradations, save charts to tests/reports/metrics/
  - Create scripts/generate_report_dashboard.py: generate tests/reports/index.html with links to latest coverage, pytest, E2E, and metrics reports
  - Integrate analyze_metrics.py and generate_report_dashboard.py into nightly pipeline to upload trend charts and dashboard as artifacts
  - Create tests/README.md: document 4-phase approach, how to run each phase, pytest markers, example commands, report locations
  - Update project README.md: add Testing section, link to tests/README.md, add CI/CD badges, document tests/reports/ structure
  - _Requirements: 13.1-13.4, 14.3-14.5, 15.9, 15.10_

- [x] 8. Final validation - Run complete test suite
  - Execute: `pytest tests/ --cov=src --cov-report=html:tests/reports/coverage/full --cov-report=xml:tests/reports/coverage/coverage.xml --html=tests/reports/pytest/full.html`
  - Verify all tests pass across all phases
  - Verify coverage meets thresholds (70% for fast CI, 80% for full)
  - Verify all GitHub Actions workflows execute successfully
  - Verify tests/reports/ directory contains all expected reports (coverage, pytest HTML, metrics, dashboard)
  - Verify tests/reports/index.html dashboard is accessible and links work
  - _Requirements: All_


## Notes

- All 12 correctness properties are included in the condensed tasks
- Each task combines related work to maximize implementation efficiency
- Task 1: Complete infrastructure (fixtures, generators, dependencies, reports directory)
- Task 2: All unit tests including 8 property tests (Properties 1-8)
- Task 3: All integration tests including 2 property tests (Properties 9-10)
- Task 4: Golden dataset setup + all E2E tests including Property 11
- Task 5: All adversarial tests
- Task 6: All 3 GitHub Actions workflows with report generation and archiving
- Task 7: Metrics tracking + report dashboard generation + all documentation
- Task 8: Final validation with report verification
- All test dependencies managed via uv package manager
- Property tests use hypothesis with 100+ iterations for statistical rigor
- CI/CD pipelines: Fast CI (<2 min), Nightly E2E (30-60 min), Manual Full (45-75 min)
- All generated reports stored in tests/reports/ and excluded from version control
- pytest-html plugin generates self-contained HTML reports for easy sharing
- Report dashboard (tests/reports/index.html) provides centralized access to all reports

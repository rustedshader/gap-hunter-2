# End-to-End (E2E) Tests

## Overview

This directory contains end-to-end tests that validate the complete gap-hunter-2 pipeline using real LLM calls against the golden dataset. These tests measure system accuracy, evidence faithfulness, and output quality using both deterministic metrics and LLM-as-a-judge evaluation.

## Test Files

### test_golden_dataset.py

Tests the full pipeline execution on curated policies with ground truth annotations.

**Key Tests:**
- `test_classify_policy_functions_accuracy`: Validates function classification accuracy (F1-Score >= 0.85)
- `test_full_pipeline_e2e`: Complete pipeline test from PDF to final reports
- `test_golden_dataset_gap_accuracy`: Gap assessment accuracy against ground truth

**Markers:** `@pytest.mark.golden`, `@pytest.mark.llm`

**Runtime:** ~5-10 minutes per policy (depends on LLM speed)

### test_llm_judge.py

Tests using LLM-as-a-judge evaluation with DeepEval for quality metrics.

**Key Tests:**
- `test_evidence_faithfulness`: Property 11 - Evidence grounding validation
- `test_framework_alignment_with_llm_judge`: Recommendation alignment with CIS MS-ISAC templates
- `test_roadmap_completeness`: Consolidated report structure and completeness
- `test_evidence_faithfulness_with_deepeval`: Alternative faithfulness test using DeepEval

**Markers:** `@pytest.mark.golden`, `@pytest.mark.llm`, `@pytest.mark.slow`

**Runtime:** ~10-15 minutes (includes LLM judge calls)

## LLM Judge Metrics

### 1. Faithfulness Score (Property 11)

**Purpose:** Verify that evidence quotes exist in the original policy document

**Implementation:** Two approaches:
1. **Deterministic (Primary)**: Check if evidence text appears as substring in policy markdown
   - Uses 3-word phrase matching with 70% overlap threshold
   - Accounts for whitespace normalization and quote extraction
   - Threshold: 90% of evidence snippets must be grounded

2. **LLM Judge (Secondary)**: DeepEval's `FaithfulnessMetric`
   - Uses GPT-4 to evaluate if evidence is faithful to source
   - Threshold: 0.70 (70% faithfulness score)

**Why It Matters:** Prevents hallucinated evidence that could mislead compliance assessments

**Threshold:** 90% (deterministic) or 0.70 (LLM judge)

**Example:**
```python
# Evidence from assessment
evidence = "Section 2 states that this policy applies to all employees"

# Must exist in policy markdown (with minor variations allowed)
assert evidence_exists_in_policy(evidence, policy_content)
```

### 2. Framework Alignment Score

**Purpose:** Evaluate whether recommendations align with CIS MS-ISAC NIST CSF Policy Template Guide (2024)

**Implementation:** DeepEval's `AnswerRelevancyMetric`
- Evaluates if recommendations are relevant to identified gaps
- Uses GPT-4 to assess alignment with framework guidance
- Considers gap description, current status, and evidence

**Threshold:** 0.70 (70% relevancy score)

**Why It Matters:** Ensures recommendations are actionable and aligned with industry best practices

**Example:**
```python
test_case = LLMTestCase(
    input="NIST Subcategory GV.RM-02: Risk Management Strategy",
    actual_output="Add formal risk assessment procedures aligned with NIST 800-30",
    retrieval_context=["Gap: Missing formal risk assessment process"]
)
metric = AnswerRelevancyMetric(threshold=0.7, model="gpt-4")
metric.measure(test_case)
```

### 3. Roadmap Completeness Score

**Purpose:** Verify that the consolidated report includes a complete prioritized remediation roadmap

**Implementation:** Deterministic checks for:
- Required sections (Executive Summary, Maturity by Function, Gaps, Roadmap)
- Priority levels (Immediate, Short-term, Medium-term)
- Specific subcategory references in roadmap
- Coverage of all identified gaps

**Threshold:** All required sections present + at least 2 priority levels

**Why It Matters:** Ensures the output is actionable and provides clear next steps

**Example Structure:**
```markdown
## 6. Prioritized Remediation Roadmap

| Priority | Action | Details |
|----------|--------|---------|
| **1 — Immediate (0–30 days)** | Address critical gaps | GV.RM-02, ID.RA-01 |
| **2 — Short-term (30–90 days)** | Strengthen partial coverage | PR.AA-03, PR.DS-11 |
| **3 — Medium-term (90–180 days)** | Create missing policies | Incident Response Policy |
```

## Running E2E Tests

### Run All E2E Tests
```bash
pytest tests/e2e/ -v
```

### Run Only Golden Dataset Tests
```bash
pytest tests/e2e/test_golden_dataset.py -v
```

### Run Only LLM Judge Tests
```bash
pytest tests/e2e/test_llm_judge.py -v
```

### Run Specific Test
```bash
pytest tests/e2e/test_llm_judge.py::test_evidence_faithfulness -v
```

### Skip Slow Tests
```bash
pytest tests/e2e/ -v -m "not slow"
```

## Test Markers

- `@pytest.mark.golden`: Tests using golden dataset
- `@pytest.mark.llm`: Tests requiring real LLM calls
- `@pytest.mark.slow`: Tests that take >5 minutes

## Configuration

### LLM Model

E2E tests use the model specified in the test code (default: `gemma4:e2b`). For nightly CI, the local `gemma-4-E2B-it-Q8_0.gguf` model is used.

### DeepEval Configuration

LLM judge tests use DeepEval with GPT-4 for evaluation. Configure your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key"
```

Alternatively, DeepEval can use other models. See [DeepEval documentation](https://docs.confident-ai.com/) for configuration options.

### Timeout Settings

E2E tests may take significant time due to LLM calls. Adjust pytest timeout if needed:

```bash
pytest tests/e2e/ -v --timeout=1800  # 30 minute timeout
```

## Interpreting Results

### Function Classification (F1-Score)

- **F1 >= 0.85**: Excellent - System correctly identifies policy scope
- **0.70 <= F1 < 0.85**: Good - Minor classification errors
- **F1 < 0.70**: Poor - Significant classification issues

### Evidence Faithfulness

- **>= 90%**: Excellent - Evidence is well-grounded
- **70-90%**: Acceptable - Some evidence may be paraphrased
- **< 70%**: Poor - Risk of hallucinated evidence

### Framework Alignment

- **>= 0.80**: Excellent - Recommendations are highly relevant
- **0.70-0.80**: Good - Recommendations are generally relevant
- **< 0.70**: Poor - Recommendations may not align with framework

## Troubleshooting

### DeepEval Import Errors

If you encounter import errors with DeepEval:

```bash
uv add deepeval
```

### LLM Timeout Errors

If LLM calls timeout, increase the timeout in the test code or use a faster model.

### Golden Dataset Not Found

Ensure the golden dataset is properly set up:

```bash
ls tests/golden_dataset/*.pdf
cat tests/golden_dataset/ground_truth.json
```

### GPT-4 API Errors

If GPT-4 is unavailable, LLM judge tests will log warnings but not fail. The deterministic faithfulness test (Property 11) will still run.

## Metrics Tracking

E2E test results are saved to `tests/reports/e2e/` with timestamps:

```
tests/reports/e2e/
├── 2024-04-09_01-30-00/
│   ├── metrics.json
│   ├── function_classification.json
│   └── faithfulness_results.json
└── latest -> 2024-04-09_01-30-00/
```

### Metrics JSON Schema

```json
{
  "timestamp": "2024-04-09T01:30:00Z",
  "test_run": "nightly",
  "metrics": {
    "function_classification_f1": 0.87,
    "evidence_faithfulness": 0.92,
    "framework_alignment": 0.75,
    "roadmap_completeness": true
  },
  "policy_results": [
    {
      "filename": "information_security_iwu.pdf",
      "f1_score": 0.85,
      "faithfulness": 0.90
    }
  ]
}
```

## Best Practices

1. **Run E2E tests before releases**: Validate system quality on real policies
2. **Monitor metric trends**: Track F1-Score and faithfulness over time
3. **Update ground truth**: Review and update annotations quarterly
4. **Add new policies**: Expand golden dataset to cover more policy types
5. **Investigate failures**: When tests fail, examine the specific policy and assessment

## References

- DeepEval Documentation: https://docs.confident-ai.com/
- NIST CSF 2.0: https://www.nist.gov/cyberframework
- CIS MS-ISAC Policy Templates: https://www.cisecurity.org/
- Golden Dataset: `tests/golden_dataset/README.md`
- Design Document: `.kiro/specs/research-based-testing/design.md`

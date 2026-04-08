# Golden Dataset for E2E Testing

## Overview

This directory contains a curated collection of 5 real-world cybersecurity policy documents with ground truth annotations for end-to-end testing of the gap-hunter-2 system. Each policy has been manually analyzed and annotated with expected NIST CSF function classifications and gap assessment results.

## Dataset Structure

```
tests/golden_dataset/
├── README.md                                          # This file
├── ground_truth.json                                  # Ground truth annotations
├── data_protection_and_security_bandweaver.pdf       # Data Protection Policy
├── information_security_iwu.pdf                       # Information Security Policy (IWU)
├── information_security_tatasteel.pdf                 # Information Security Policy (Tata Steel)
├── isms_lupin.pdf                                     # ISMS Policy (Lupin)
└── patch_management_cse.pdf                           # Patch Management Policy
```

## Policies Included

### 1. Data Protection and Security Policy (Bandweaver)
- **Type**: Data Protection and Security Policy
- **Expected Functions**: Govern, Protect
- **Characteristics**: Focused on data protection, privacy, and security controls
- **Coverage**: Strong on access control and data security, limited governance depth

### 2. Information Security Policy (IWU)
- **Type**: Information Security Policy
- **Expected Functions**: Govern, Identify, Protect
- **Characteristics**: Comprehensive information security framework
- **Coverage**: Broad coverage across governance, asset management, and protection

### 3. Information Security Policy (Tata Steel)
- **Type**: Information Security Policy
- **Expected Functions**: Govern, Identify, Protect
- **Characteristics**: Enterprise-grade information security policy
- **Coverage**: Extensive coverage with strong governance and risk management

### 4. ISMS Policy (Lupin)
- **Type**: Information Security Management System (ISMS) Policy
- **Expected Functions**: Govern, Identify, Protect, Detect
- **Characteristics**: ISO 27001-aligned ISMS framework
- **Coverage**: Most comprehensive policy with detection capabilities

### 5. Patch Management Policy (CSE)
- **Type**: Patch Management Policy
- **Expected Functions**: Protect, Detect
- **Characteristics**: Specialized technical policy for vulnerability management
- **Coverage**: Strong on platform security and monitoring, limited governance

## Ground Truth Schema

The `ground_truth.json` file contains annotations for each policy with the following structure:

```json
{
  "policy_filename.pdf": {
    "type": "Policy Type Description",
    "expected_functions": ["Function1", "Function2"],
    "ground_truth_gaps": {
      "SUBCATEGORY_ID": "Status"
    }
  }
}
```

### Fields

- **type**: Human-readable description of the policy type
- **expected_functions**: List of NIST CSF functions that should be classified as relevant to this policy
  - Valid values: `"Govern"`, `"Identify"`, `"Protect"`, `"Detect"`, `"Respond"`, `"Recover"`
- **ground_truth_gaps**: Mapping of NIST subcategory IDs to their expected assessment status
  - Valid statuses:
    - `"Addressed"`: Policy fully addresses this subcategory
    - `"Partially Addressed"`: Policy addresses some aspects but has gaps
    - `"Not Addressed"`: Policy does not address this subcategory at all
    - `"Out of Scope"`: Subcategory is not relevant to this policy type

### Example

```json
{
  "information_security_iwu.pdf": {
    "type": "Information Security Policy",
    "expected_functions": ["Govern", "Identify", "Protect"],
    "ground_truth_gaps": {
      "GV.OC-01": "Addressed",
      "GV.RM-02": "Partially Addressed",
      "ID.RA-01": "Addressed",
      "DE.CM-01": "Out of Scope"
    }
  }
}
```

## How to Add New Policies

To add a new policy to the golden dataset:

1. **Select a Policy**: Choose a real-world cybersecurity policy document that represents a distinct policy type not already covered

2. **Copy the PDF**: Place the PDF file in `tests/golden_dataset/`
   ```bash
   cp path/to/new_policy.pdf tests/golden_dataset/
   ```

3. **Analyze the Policy**: Manually review the policy to determine:
   - Policy type and purpose
   - Which NIST CSF functions are relevant
   - Assessment status for key NIST subcategories (minimum 10-15 subcategories)

4. **Add Ground Truth**: Update `ground_truth.json` with the new policy's annotations:
   ```json
   {
     "new_policy.pdf": {
       "type": "Policy Type",
       "expected_functions": ["Function1", "Function2"],
       "ground_truth_gaps": {
         "GV.OC-01": "Addressed",
         "GV.RM-01": "Partially Addressed",
         ...
       }
     }
   }
   ```

5. **Validate**: Run the golden dataset tests to ensure the new policy is properly integrated:
   ```bash
   pytest tests/e2e/test_golden_dataset.py -v
   ```

## Quality Guidelines

When creating ground truth annotations:

- **Be Conservative**: If unsure between "Addressed" and "Partially Addressed", choose "Partially Addressed"
- **Focus on Evidence**: Base assessments on actual policy text, not assumptions
- **Document Rationale**: Keep notes on why each subcategory was assessed a certain way
- **Include Edge Cases**: Annotate subcategories that are borderline or ambiguous
- **Minimum Coverage**: Annotate at least 10-15 subcategories per policy across different functions
- **Balance Statuses**: Include a mix of all four statuses (Addressed, Partially Addressed, Not Addressed, Out of Scope)

## Usage in Tests

The golden dataset is used by:

- **test_golden_dataset.py**: Tests function classification accuracy (F1-Score >= 0.85) and full pipeline E2E validation
- **test_llm_judge.py**: Tests evidence faithfulness (Property 11) and LLM judge evaluation metrics

Example test usage:

```python
@pytest.mark.golden
def test_policy_classification(golden_policy_loader):
    policy = golden_policy_loader("information_security_iwu.pdf")
    result = classify_policy_functions(policy.content)
    
    # Verify against ground truth
    assert set(result) == set(policy.expected_functions)
```

## Maintenance

- **Review Quarterly**: Re-validate ground truth annotations every 3 months
- **Update on Framework Changes**: When NIST CSF or CIS MS-ISAC templates are updated, review and update annotations
- **Track Metrics**: Monitor E2E test metrics over time to detect annotation drift or system regressions

## References

- NIST Cybersecurity Framework 2.0
- CIS MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024)
- Gap-hunter-2 Design Document: `.kiro/specs/research-based-testing/design.md`

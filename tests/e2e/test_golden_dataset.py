"""
E2E tests using the golden dataset with real LLM calls.

Tests full pipeline execution on curated policies with ground truth annotations.
Validates function classification accuracy and end-to-end gap analysis quality.
"""

import json
import pytest
from pathlib import Path

# Mark all tests in this module as golden dataset tests
pytestmark = [pytest.mark.golden, pytest.mark.llm]


def calculate_f1_score(predicted: list[str], expected: list[str]) -> float:
    """
    Calculate F1-Score for function classification.
    
    Args:
        predicted: List of predicted function names
        expected: List of expected function names (ground truth)
    
    Returns:
        F1-Score between 0.0 and 1.0
    """
    if not expected:
        return 1.0 if not predicted else 0.0
    
    predicted_set = set(predicted)
    expected_set = set(expected)
    
    # True positives: functions correctly identified
    tp = len(predicted_set & expected_set)
    
    # False positives: functions incorrectly identified
    fp = len(predicted_set - expected_set)
    
    # False negatives: functions missed
    fn = len(expected_set - predicted_set)
    
    # Calculate precision and recall
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    # Calculate F1-Score
    if precision + recall == 0:
        return 0.0
    
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1


@pytest.mark.golden
@pytest.mark.llm
def test_classify_policy_functions_accuracy(golden_policy_loader):
    """
    Test function classification accuracy on golden dataset.
    
    **Validates: Requirements 3.3**
    
    Measures F1-Score for policy function classification against ground truth.
    Threshold: F1-Score >= 0.85 (85% accuracy).
    """
    from src.agents.nist_gap_agents import classify_policy_functions
    from src.tools.pdf import pdf_to_markdown
    
    # Load ground truth
    ground_truth_path = Path("tests/golden_dataset/ground_truth.json")
    ground_truth_data = json.loads(ground_truth_path.read_text())
    
    results = []
    
    for filename in ground_truth_data.keys():
        print(f"\n{'='*60}")
        print(f"Testing: {filename}")
        print(f"{'='*60}")
        
        # Load policy
        policy_path = Path("tests/golden_dataset") / filename
        policy_content = pdf_to_markdown(policy_path)
        
        # Get ground truth
        expected_functions = ground_truth_data[filename]["expected_functions"]
        
        # Run classification
        predicted_functions = classify_policy_functions(policy_content)
        
        # Calculate F1-Score
        f1 = calculate_f1_score(predicted_functions, expected_functions)
        
        results.append({
            "filename": filename,
            "expected": expected_functions,
            "predicted": predicted_functions,
            "f1_score": f1
        })
        
        print(f"Expected:  {expected_functions}")
        print(f"Predicted: {predicted_functions}")
        print(f"F1-Score:  {f1:.3f}")
    
    # Calculate average F1-Score
    avg_f1 = sum(r["f1_score"] for r in results) / len(results)
    
    print(f"\n{'='*60}")
    print(f"OVERALL RESULTS")
    print(f"{'='*60}")
    print(f"Average F1-Score: {avg_f1:.3f}")
    print(f"Threshold: 0.85")
    
    # Assert threshold
    assert avg_f1 >= 0.85, (
        f"Function classification F1-Score ({avg_f1:.3f}) is below threshold (0.85). "
        f"Results: {results}"
    )


@pytest.mark.golden
@pytest.mark.llm
@pytest.mark.slow
def test_full_pipeline_e2e():
    """
    Full end-to-end pipeline test on one golden dataset policy.
    
    **Validates: Requirements 3.1, 3.2, 3.8**
    
    Tests the complete gap analysis pipeline from PDF input to final reports:
    1. PDF extraction
    2. Section summarization
    3. Function classification
    4. Gap analysis (all 6 functions)
    5. Report generation
    """
    from src.tools.pdf import pdf_to_markdown
    from src.extractor import extract_sections
    from src.gap_analyzer import run_gap_analysis
    from pathlib import Path
    import tempfile
    import json
    
    # Use the ISMS policy (most comprehensive)
    policy_path = Path("tests/golden_dataset/isms_lupin.pdf")
    
    print(f"\n{'='*60}")
    print(f"Full Pipeline E2E Test: {policy_path.name}")
    print(f"{'='*60}")
    
    # Step 1: Extract policy content
    print("\nStep 1: Extracting policy content...")
    policy_markdown = pdf_to_markdown(policy_path)
    assert len(policy_markdown) > 0, "Policy extraction failed"
    print(f"  ✓ Extracted {len(policy_markdown)} characters")
    
    # Step 2: Extract sections
    print("\nStep 2: Extracting sections...")
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Save markdown temporarily
        md_path = tmpdir_path / "policy.md"
        md_path.write_text(policy_markdown)
        
        # Extract sections
        sections_output_path = tmpdir_path / "sections_output.json"
        master_list_path = tmpdir_path / "master_list.json"
        
        extract_sections(
            policy_path,
            sections_output_path,
            master_list_path,
            model_name="gemma4:e2b"
        )
        
        assert sections_output_path.exists(), "Sections extraction failed"
        assert master_list_path.exists(), "Master list generation failed"
        
        sections = json.loads(sections_output_path.read_text())
        master_list = json.loads(master_list_path.read_text())
        
        print(f"  ✓ Extracted {len(sections)} sections")
        print(f"  ✓ Generated master list with {len(master_list)} entries")
        
        # Step 3: Run gap analysis
        print("\nStep 3: Running gap analysis...")
        run_output_dir = tmpdir_path / "gap_analysis"
        run_output_dir.mkdir()
        
        reports = run_gap_analysis(
            master_list_path,
            run_output_dir,
            model_name="gemma4:e2b",
            sections_path=sections_output_path
        )
        
        # Verify reports were generated
        assert len(reports) == 6, f"Expected 6 function reports, got {len(reports)}"
        print(f"  ✓ Generated {len(reports)} function reports")
        
        # Verify key output files exist
        expected_files = [
            "combined_gap_analysis.md",
            "consolidated_gap_analysis.md",
            "master_gap_summary.md",
            "assessments.json"
        ]
        
        for filename in expected_files:
            filepath = run_output_dir / filename
            assert filepath.exists(), f"Missing expected file: {filename}"
            print(f"  ✓ Generated {filename}")
        
        # Verify assessments structure
        assessments_path = run_output_dir / "assessments.json"
        assessments_data = json.loads(assessments_path.read_text())
        
        assert len(assessments_data) == 6, "Expected assessments for all 6 functions"
        
        for function, assessments in assessments_data.items():
            assert isinstance(assessments, list), f"{function} assessments should be a list"
            assert len(assessments) > 0, f"{function} should have at least one assessment"
            
            # Verify assessment structure
            for assessment in assessments:
                required_fields = [
                    "subcategory_id",
                    "title",
                    "status",
                    "evidence",
                    "gap",
                    "recommendation"
                ]
                for field in required_fields:
                    assert field in assessment, f"Missing field '{field}' in assessment"
        
        print(f"  ✓ Validated assessments structure")
        
        print(f"\n{'='*60}")
        print("Full Pipeline E2E Test: PASSED")
        print(f"{'='*60}")


@pytest.mark.golden
@pytest.mark.llm
def test_golden_dataset_gap_accuracy():
    """
    Test gap assessment accuracy against ground truth for key subcategories.
    
    **Validates: Requirements 3.2**
    
    Compares system-generated gap assessments against manually annotated
    ground truth for a subset of subcategories.
    """
    from src.tools.pdf import pdf_to_markdown
    from src.agents.nist_gap_agents import run_nist_gap_agent
    from pathlib import Path
    import json
    
    # Test on a single policy with detailed ground truth
    policy_filename = "information_security_tatasteel.pdf"
    policy_path = Path("tests/golden_dataset") / policy_filename
    
    # Load ground truth
    ground_truth_path = Path("tests/golden_dataset/ground_truth.json")
    ground_truth_data = json.loads(ground_truth_path.read_text())
    ground_truth_gaps = ground_truth_data[policy_filename]["ground_truth_gaps"]
    
    print(f"\n{'='*60}")
    print(f"Gap Accuracy Test: {policy_filename}")
    print(f"{'='*60}")
    
    # Extract policy content
    policy_content = pdf_to_markdown(policy_path)
    
    # Test Govern function (has most ground truth annotations)
    print("\nTesting Govern function...")
    report, assessments = run_nist_gap_agent(
        function_name="Govern",
        policy_content=policy_content,
        model_name="gemma4:e2b"
    )
    
    # Compare against ground truth
    matches = 0
    total = 0
    mismatches = []
    
    for assessment in assessments:
        sub_id = assessment.subcategory_id
        if sub_id in ground_truth_gaps:
            total += 1
            expected_status = ground_truth_gaps[sub_id]
            actual_status = assessment.status
            
            if expected_status == actual_status:
                matches += 1
                print(f"  ✓ {sub_id}: {actual_status} (correct)")
            else:
                mismatches.append({
                    "subcategory": sub_id,
                    "expected": expected_status,
                    "actual": actual_status
                })
                print(f"  ✗ {sub_id}: Expected '{expected_status}', got '{actual_status}'")
    
    accuracy = matches / total if total > 0 else 0.0
    
    print(f"\n{'='*60}")
    print(f"Accuracy: {matches}/{total} ({accuracy:.1%})")
    print(f"{'='*60}")
    
    if mismatches:
        print("\nMismatches:")
        for mm in mismatches:
            print(f"  - {mm['subcategory']}: Expected '{mm['expected']}', got '{mm['actual']}'")
    
    # We expect at least 70% accuracy (allowing for LLM variability)
    assert accuracy >= 0.70, (
        f"Gap assessment accuracy ({accuracy:.1%}) is below threshold (70%). "
        f"Mismatches: {mismatches}"
    )

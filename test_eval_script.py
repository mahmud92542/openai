import pytest
import json
from eval_script import evaluate_tests, load_test_cases

@pytest.fixture
def test_cases():
    return load_test_cases("test_cases.json")

def test_eval_script(test_cases):
    # Call evaluate_tests, which returns results and pass_percentage
    results, pass_percentage = evaluate_tests(test_cases)

    # Check if the overall pass percentage is at least 80%
    assert pass_percentage >= 80, f"Deployment failed because less than 80% of tests passed. Pass percentage: {pass_percentage}%"
    
    # Optionally, log the results to see failed tests
    failed_tests = [test_id for test_id, result in results if result != "PASS"]
    if failed_tests:
        print(f"Failed Tests: {failed_tests}")

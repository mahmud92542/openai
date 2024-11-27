import pytest
import json
from eval_script import evaluate_tests, load_test_cases

@pytest.fixture
def test_cases():
    return load_test_cases("test_cases.json")

def test_eval_script(test_cases):
    # Call evaluate_tests, which returns results and pass_percentage
    results, pass_percentage = evaluate_tests(test_cases)

    # Track the number of failed tests to log them
    failed_tests = []

    # Iterate over the results, which is a list of tuples (test_id, result)
    for test_id, result in results:
        if result != "PASS":
            failed_tests.append(test_id)
    
    # Assert that pass percentage is at least 80%
    assert pass_percentage >= 80, f"Deployment failed because less than 80% of tests passed. Pass percentage: {pass_percentage}%"
    
    # Optionally, print the failed tests
    if failed_tests:
        print(f"Failed Tests: {failed_tests}")

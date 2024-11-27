import pytest
import json
from eval_script import evaluate_tests, load_test_cases

@pytest.fixture
def test_cases():
    return load_test_cases("test_cases.json")

def test_eval_script(test_cases):
    # Call evaluate_tests, which returns results and pass_percentage
    results, pass_percentage = evaluate_tests(test_cases)
    
    # Iterate over the results, which is a list of tuples (test_id, result)
    for test_id, result in results:
        assert result == "PASS", f"Test {test_id} failed with result {result}"

    # Assert that at least 80% of the tests passed
    assert pass_percentage >= 80, f"Deployment failed because less than 80% of tests passed. Pass percentage: {pass_percentage}%"

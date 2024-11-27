import pytest
from eval_script import evaluate_tests, load_test_cases

@pytest.fixture
def test_cases():
    # Load test cases from the provided JSON file
    return load_test_cases("test_cases.json")

def test_eval_script(test_cases):
    # Call the evaluate_tests function to evaluate the test cases
    results = evaluate_tests(test_cases)
    
    # Assert that the test results contain "PASS" for each test case
    for test_id, result in results:
        assert result == "PASS", f"Test {test_id} failed. Expected: PASS, Got: {result}"

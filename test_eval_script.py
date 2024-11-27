import pytest
import json
from eval_script import evaluate_tests, load_test_cases

@pytest.fixture
def test_cases():
    return load_test_cases("test_cases.json")

def test_eval_script(test_cases):
    results = evaluate_tests(test_cases)
    
    # Iterate over the results, which is a list of tuples (test_id, result)
    for test_id, result in results:
        assert result == "PASS", f"Test {test_id} failed with result {result}"

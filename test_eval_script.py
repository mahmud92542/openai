import pytest
import json
from eval_script import evaluate_tests, load_test_cases

@pytest.fixture
def test_cases():
    return load_test_cases("test_cases.json")

def test_eval_script(test_cases):
    results, pass_percentage = evaluate_tests(test_cases)

    # Assert that pass percentage is at least 80%
    assert pass_percentage >= 80, f"Tests did not pass enough. Only {pass_percentage}% passed."

    # Handle if results is a dict
    if isinstance(results, dict):
        for test_id, result in results.items():
            print(f"Test {test_id}: {result}")
    else:
        # Handle if results is a list of tuples/lists, possibly with extra values
        for item in results:
            # Unpack first two items safely, ignore rest
            test_id, result, *rest = item
            print(f"Test {test_id}: {result}")

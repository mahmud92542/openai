import pytest
import json
from eval_script import evaluate_tests, load_test_cases

@pytest.fixture
def test_cases():
    return load_test_cases("test_cases.json")

def test_eval_script(test_cases):
    results, pass_percentage = evaluate_tests(test_cases)

    # Check if pass percentage is 50 or greater
    assert pass_percentage >= 50, f"Tests did not pass enough. Only {pass_percentage}% passed."

    # Additional checks if needed (e.g., print results)
    for test_id, result in results:
        print(f"Test {test_id}: {result}")

    # Assert the overall pass percentage is at least 50%
    assert pass_percentage >= 50, f"Pass percentage is below 80%. It is {pass_percentage}%"

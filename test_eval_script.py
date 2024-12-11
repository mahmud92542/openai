import pytest
import json
from eval_script import evaluate_tests, load_test_cases

@pytest.fixture
def test_cases():
    return load_test_cases("test_cases.json")

@pytest.fixture
def assistant_id():
    return "asst_7wJ5VYgMJYjTtALPHdieu7sE"  # Example assistant ID

def test_eval_script(test_cases, assistant_id):
    results, pass_percentage = evaluate_tests(test_cases, assistant_id)
    assert pass_percentage >= 80, f"Tests did not pass enough. Only {pass_percentage}% passed."
    for test_id, result in results:
        print(f"Test {test_id}: {result}")
    assert pass_percentage >= 80, f"Pass percentage is below 80%. It is {pass_percentage}%"

import os
import openai
import json
import pytest
from difflib import SequenceMatcher  # For partial match

# Load test cases from a JSON file
def load_test_cases(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Call the OpenAI API to get the model's actual response
def get_actual_output(input_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": input_text},
            ],
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"ERROR: {e}"

# Compare expected and actual outputs
def compare_outputs(expected, actual, method="exact"):
    if method == "exact":
        return expected.strip().lower() == actual.strip().lower()
    elif method == "partial":
        return expected.strip().lower() in actual.strip().lower()
    elif method == "similarity":
        similarity = SequenceMatcher(None, expected.strip().lower(), actual.strip().lower()).ratio()
        return similarity > 0.8
    else:
        raise ValueError("Unknown comparison method: Choose 'exact', 'partial', or 'similarity'.")

# Define a pytest test function for each test case
@pytest.mark.parametrize("test_case", load_test_cases("test_cases.json"))
def test_assistant_output(test_case):
    print(f"Running Test: {test_case['id']}")
    actual_output = get_actual_output(test_case["input"])
    expected_output = test_case["expected_output"]
    comparison_method = test_case.get("comparison_method", "exact")

    print(f"Expected: {expected_output}")
    print(f"Actual: {actual_output}")

    # Perform comparison
    assert compare_outputs(expected_output, actual_output, method=comparison_method), f"{test_case['id']} - FAIL"

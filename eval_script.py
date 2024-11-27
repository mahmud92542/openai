# eval_script.py
import os
import openai
import json
from difflib import SequenceMatcher  # For partial match

# Function to load test cases from a JSON file
def load_test_cases(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Function to call the OpenAI API to get the model's actual response
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

# Function to compare expected and actual outputs
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

# Function to evaluate tests
def evaluate_tests(test_cases):
    results = []
    for test in test_cases:
        actual_output = get_actual_output(test["input"])
        if compare_outputs(test["expected_output"], actual_output, method=test.get("comparison_method", "exact")):
            results.append((test["id"], "PASS"))
        else:
            results.append((test["id"], "FAIL"))
    return results

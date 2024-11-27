import os
import openai
import json
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
    expected = expected.strip().lower()
    actual = actual.strip().lower()

    if method == "exact":
        return expected == actual
    elif method == "partial":
        return expected in actual
    elif method == "similarity":
        similarity = SequenceMatcher(None, expected, actual).ratio()
        return similarity >= 0.8  # 80% similarity for "PASS"
    else:
        raise ValueError("Unknown comparison method: Choose 'exact', 'partial', or 'similarity'.")

# Evaluate the tests and return the results
def evaluate_tests(test_cases):
    results = []
    for test in test_cases:
        print(f"Running Test: {test['id']}")
        actual_output = get_actual_output(test["input"])
        print(f"Expected: {test['expected_output']}")
        print(f"Actual: {actual_output}")

        if compare_outputs(test["expected_output"], actual_output, method=test.get("comparison_method", "exact")):
            results.append((test["id"], "PASS"))
            print(f"{test['id']} - PASS")
        else:
            results.append((test["id"], "FAIL"))
            print(f"{test['id']} - FAIL")
        print("-" * 50)

    # Calculate percentage of passed tests
    pass_count = sum(1 for _, result in results if result == "PASS")
    total_tests = len(results)
    pass_percentage = (pass_count / total_tests) * 100

    print(f"Total Tests: {total_tests}, Passed: {pass_count}, Pass Percentage: {pass_percentage}%")

    # Check if 80% tests passed
    if pass_percentage >= 80:
        print("Deployment triggered: 80% or more tests passed.")
        return True  # Indicate that deployment can happen
    else:
        print("Deployment not triggered: Less than 80% tests passed.")
        return False

if __name__ == "__main__":
    # Set OpenAI API key from environment variable
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Error: OpenAI API key not found in environment variables.")
        exit(1)

    # Load test cases
    test_cases = load_test_cases("test_cases.json")

    # Evaluate test cases
    deploy = evaluate_tests(test_cases)

    # Trigger deployment if 80% tests pass
    if deploy:
        print("Proceeding with deployment...")
    else:
        print("Deployment aborted.")

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
    if method == "exact":
        return expected.strip().lower() == actual.strip().lower()
    elif method == "partial":
        return expected.strip().lower() in actual.strip().lower()
    elif method == "similarity":
        similarity = SequenceMatcher(None, expected.strip().lower(), actual.strip().lower()).ratio()
        return similarity > 0.8
    else:
        raise ValueError("Unknown comparison method: Choose 'exact', 'partial', or 'similarity'.")

# Evaluate the tests
def evaluate_tests(test_cases):
    results = []
    for test in test_cases:
        print(f"Running Test: {test['id']}")
        actual_output = get_actual_output(test["input"])
        print(f"Expected: {test['expected_output']}")
        print(f"Actual: {actual_output}")

        test_result = "PASS" if compare_outputs(test["expected_output"], actual_output, method=test.get("comparison_method", "exact")) else "FAIL"
        
        print(f"{test['id']} - {test_result}")
        print("-" * 50)
        
        results.append((test['id'], test_result))  # Collect test result (id, result)

    return results  # Return the list of results

if __name__ == "__main__":
    # Set OpenAI API key from environment variable
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Error: OpenAI API key not found in environment variables.")
        exit(1)

    # Load test cases
    test_cases = load_test_cases("test_cases.json")

    # Evaluate test cases
    results = evaluate_tests(test_cases)

    # Output results (for visual feedback)
    print("Test Results:")
    for test_id, result in results:
        print(f"Test {test_id}: {result}")

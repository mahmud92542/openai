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
            model="asst_L42MN296w0C5D1fNcomfTvi1",  # Use your custom assistant model
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
        return similarity > 0.7
    else:
        raise ValueError("Unknown comparison method: Choose 'exact', 'partial', or 'similarity'.")

# Evaluate the tests
def evaluate_tests(test_cases):
    passed_tests = 0
    total_tests = len(test_cases)
    results = []

    for test in test_cases:
        print(f"Running Test: {test['id']}")
        actual_output = get_actual_output(test["input"])
        print(f"Expected: {test['expected_output']}")
        print(f"Actual: {actual_output}")

        test_result = compare_outputs(test["expected_output"], actual_output, method=test.get("comparison_method", "exact"))
        
        if test_result:
            results.append((test['id'], "PASS"))
            passed_tests += 1
            print(f"{test['id']} - PASS")
        else:
            results.append((test['id'], "FAIL"))
            print(f"{test['id']} - FAIL")
        
        print("-" * 50)

    # Calculate pass percentage
    pass_percentage = (passed_tests / total_tests) * 100
    print(f"Pass percentage: {pass_percentage}%")
    
    return results, pass_percentage

if __name__ == "__main__":
    # Set OpenAI API key from environment variable
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Error: OpenAI API key not found in environment variables.")
        exit(1)

    # Load test cases
    test_cases = load_test_cases("test_cases.json")

    # Evaluate test cases
    results, pass_percentage = evaluate_tests(test_cases)
    print(f"Test Results: {results}")
    print(f"Overall pass percentage: {pass_percentage}%")

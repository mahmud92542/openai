import os
import openai
import json
from difflib import SequenceMatcher  # For partial match

# Set your assistant ID at the beginning of the script
assistant_id = "asst_7wJ5VYgMJYjTtALPHdieu7sE"  # You can also use "gpt-3.5-turbo" if that's your assistant

# Load test cases from a JSON file
def load_test_cases(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Call the OpenAI API to get the assistant's actual response
def get_actual_output(input_text, assistant_id):
    try:
        response = openai.ChatCompletion.create(
            model=assistant_id,  # Use the assistant ID or model name
            messages=[
                {"role": "user", "content": input_text},
            ],
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"ERROR: {e}"

# Compare expected and actual outputs
def compare_outputs(expected, actual, method="exact", ai_model="gpt-4"):
    if "ERROR:" in actual:
        return False
    if method == "exact":
        return expected.strip().lower() == actual.strip().lower()
    elif method == "partial":
        return expected.strip().lower() in actual.strip().lower()
    elif method == "similarity":
        similarity = SequenceMatcher(None, expected.strip().lower(), actual.strip().lower()).ratio()
        return similarity > 0.7
    elif method == "ai_comparison":
        return ai_comparison(expected, actual, ai_model)
    else:
        raise ValueError("Unknown comparison method: Choose 'exact', 'partial', 'similarity', or 'ai_comparison'.")

# AI-powered comparison using OpenAI API
def ai_comparison(expected, actual, ai_model="gpt-4"):
    try:
        response = openai.ChatCompletion.create(
            model=ai_model,  # Use the assistant ID or model name
            messages=[
                {"role": "system", "content": "You are an assistant that evaluates the similarity of two texts."},
                {
                    "role": "user",
                    "content": f"Compare the following two text outputs and rate their similarity on a scale from 0 to 100:\n\n"
                    f"Expected Output: {expected}\n\n"
                    f"Actual Output: {actual}\n\n"
                    f"Only provide the numeric similarity score as an integer without any additional text.",
                },
            ],
            temperature=0.0,  # Ensure the response is deterministic
        )

        # Extract the numeric similarity score from the response
        similarity_score = float(response["choices"][0]["message"]["content"].strip())
        return similarity_score >= 80  # Adjust the threshold as needed

    except Exception as e:
        print(f"Error during AI comparison: {e}")
        return False

# Evaluate the tests
def evaluate_tests(test_cases, assistant_id):
    passed_tests = 0
    total_tests = len(test_cases)
    results = []

    for test in test_cases:
        print(f"Running Test: {test['id']}")
        actual_output = get_actual_output(test["input"], assistant_id)
        print(f"Expected: {test['expected_output']}")
        print(f"Actual: {actual_output}")

        # Default to exact comparison unless specified
        comparison_method = test.get("comparison_method", "exact")
        test_result = compare_outputs(test["expected_output"], actual_output, method=comparison_method)

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
    file_path = "test_cases.json"  # Specify your JSON file path
    if not os.path.exists(file_path):
        print(f"Error: Test case file '{file_path}' not found.")
        exit(1)

    test_cases = load_test_cases(file_path)

    # Evaluate the test cases
    results, pass_percentage = evaluate_tests(test_cases, assistant_id)
    print(f"Test Results: {results}")
    print(f"Overall pass percentage: {pass_percentage}%")

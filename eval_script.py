import os
import requests
import json
from difflib import SequenceMatcher  # For partial match

# Set your assistant ID at the beginning of the script
assistant_id = "asst_7wJ5VYgMJYjTtALPHdieu7sE"  # Use your actual assistant ID

# Load test cases from a JSON file
def load_test_cases(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Call the OpenAI Assistants API to get the assistant's actual response
def get_actual_output(input_text, assistant_id):
    try:
        # Set the OpenAI API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "ERROR: OpenAI API key not found in environment variables."

        # Define the URL and headers
        url = f"https://api.openai.com/v1/assistants/{assistant_id}/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "OpenAI-Beta": "assistants=v2"
        }


        # The request body with the input message
        payload = {
            "messages": [
                {"role": "user", "content": input_text}
            ]
        }

        # Make the POST request to the API
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        else:
            return f"ERROR: {response.status_code} - {response.json()}"
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

# AI-powered comparison using OpenAI Assistants API
def ai_comparison(expected, actual, ai_model="gpt-4"):
    try:
        # Set the OpenAI API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return False

        # Define the URL and headers for a chat completion request
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # The request body
        payload = {
            "model": ai_model,
            "messages": [
                {"role": "system", "content": "You are an assistant that evaluates the similarity of two texts."},
                {
                    "role": "user",
                    "content": f"Compare the following two text outputs and rate their similarity on a scale from 0 to 100:\n\n"
                    f"Expected Output: {expected}\n\n"
                    f"Actual Output: {actual}\n\n"
                    f"Only provide the numeric similarity score as an integer without any additional text.",
                }
            ],
            "temperature": 0.0
        }

        # Make the POST request
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            similarity_score = float(data["choices"][0]["message"]["content"].strip())
            return similarity_score >= 80  # Adjust the threshold as needed
        else:
            print(f"Error: {response.status_code} - {response.json()}")
            return False
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
    if not os.getenv("OPENAI_API_KEY"):
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

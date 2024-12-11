import os
import json
from assistant_api_v2 import create_thread, create_run, get_thread_messages

# Load test cases from a JSON file
def load_test_cases(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Evaluate the tests
def evaluate_tests(test_cases, assistant_id):
    passed_tests = 0
    total_tests = len(test_cases)
    results = []

    for test in test_cases:
        print(f"Running Test: {test['id']}")
        
        thread_id = create_thread(test["input"])
        if "ERROR" in thread_id:
            print(thread_id)
            continue

        run_id = create_run(thread_id, assistant_id)
        if "ERROR" in run_id:
            print(run_id)
            continue

        messages = get_thread_messages(thread_id)
        if isinstance(messages, str) and "ERROR" in messages:
            print(messages)
            continue

        if not messages:
            print(f"ERROR: No messages returned for thread {thread_id}")
            continue

        # Check if the message content is present
        try:
            actual_output = messages[0]["content"][0]["text"]["value"]
        except (IndexError, KeyError) as e:
            print(f"ERROR: Invalid message structure - {e}")
            continue

        print(f"Expected: {test['expected_output']}")
        print(f"Actual: {actual_output}")

        if test['expected_output'].strip().lower() == actual_output.strip().lower():
            results.append((test['id'], "PASS"))
            passed_tests += 1
            print(f"{test['id']} - PASS")
        else:
            results.append((test['id'], "FAIL"))
            print(f"{test['id']} - FAIL")

        print("-" * 50)

    pass_percentage = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"Pass percentage: {pass_percentage}%")
    return results, pass_percentage

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OpenAI API key not found in environment variables.")
        exit(1)

    file_path = "test_cases.json"
    if not os.path.exists(file_path):
        print(f"Error: Test case file '{file_path}' not found.")
        exit(1)

    test_cases = load_test_cases(file_path)
    assistant_id = "asst_7wJ5VYgMJYjTtALPHdieu7sE"
    results, pass_percentage = evaluate_tests(test_cases, assistant_id)
    print(f"Test Results: {results}")
    print(f"Overall pass percentage: {pass_percentage}%")

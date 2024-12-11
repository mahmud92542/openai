import os
import time
import requests
import json
from difflib import SequenceMatcher  # For partial match

# Set your assistant ID at the beginning of the script
assistant_id = "asst_7wJ5VYgMJYjTtALPHdieu7sE"  # Use your actual assistant ID

# Load test cases from a JSON file
def load_test_cases(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Create a thread for the assistant to interact with
def create_thread(input_text):
    try:
        # Set the OpenAI API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "ERROR: OpenAI API key not found in environment variables."

        # Define the URL and headers
        url = "https://api.openai.com/v1/threads"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # The request body to create a thread
        payload = {
            "messages": [
                {"role": "user", "content": input_text}
            ]
        }

        # Make the POST request to create a thread
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            data = response.json()
            return data["id"]  # Return the thread ID
        else:
            return f"ERROR: {response.status_code} - {response.json()}"
    except Exception as e:
        return f"ERROR: {e}"

# Create a run to process the thread and assistant's response
def create_run(thread_id, assistant_id):
    try:
        # Set the OpenAI API key from environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "ERROR: OpenAI API key not found in environment variables."

        # Define the URL and headers
        url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        # The request body to create a run
        payload = {"assistant_id": assistant_id}

        # Make the POST request to create a run
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            data = response.json()
            return data["id"]  # Return the run ID
        else:
            return f"ERROR: {response.status_code} - {response.json()}"
    except Exception as e:
        return f"ERROR: {e}"

# Wait for the run to complete
def wait_for_run(thread_id, run_id):
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "ERROR: OpenAI API key not found in environment variables."

        url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        while True:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                status = data["status"]
                if status == "completed":
                    return "completed"
                elif status in ["failed", "cancelled"]:
                    return f"ERROR: {status}"
            time.sleep(0.5)  # Wait before checking again
    except Exception as e:
        return f"ERROR: {e}"

# Get all messages from the thread
def get_thread_messages(thread_id):
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "ERROR: OpenAI API key not found in environment variables."

        url = f"https://api.openai.com/v1/threads/{thread_id}/messages"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data["data"]  # Return the list of messages
        else:
            return f"ERROR: {response.status_code} - {response.json()}"
    except Exception as e:
        return f"ERROR: {e}"

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

        wait_status = wait_for_run(thread_id, run_id)
        if "ERROR" in wait_status:
            print(wait_status)
            continue

        messages = get_thread_messages(thread_id)
        actual_output = messages[0]["content"][0]["text"]["value"]
        
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

    pass_percentage = (passed_tests / total_tests) * 100
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
    results, pass_percentage = evaluate_tests(test_cases, assistant_id)
    print(f"Test Results: {results}")
    print(f"Overall pass percentage: {pass_percentage}%")

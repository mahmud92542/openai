import json
import os
import time
from openai import OpenAI

def load_test_cases(file_path):
    """Load test cases from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def ask_question_and_get_response(thread_id, question, assistant_id):
    """Send a question to the assistant and retrieve the assistant's response."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    
    client = OpenAI(api_key=api_key)
    
    # Send user message
    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=question)
    
    # Start the assistant's run
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
    
    while run.status in ["queued", "in_progress"]:
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
    
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        if messages.data:
            return messages.data[-1].content
    return None

def evaluate_tests(test_cases, assistant_id):
    """Evaluate test cases and compare the assistant's response to the expected answer."""
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, test_case in enumerate(test_cases):
        print(f"Running Test {i+1}/{total_tests}: {test_case['question']}")
        
        thread_id, _ = create_thread_and_attach_assistant(assistant_id)
        assistant_response = ask_question_and_get_response(thread_id, test_case['question'], assistant_id)
        
        is_pass = assistant_response.strip() == test_case['expected_answer'].strip()
        results.append((test_case['id'], is_pass))
        
        if is_pass:
            passed_tests += 1
        
    pass_percentage = (passed_tests / total_tests) * 100
    
    return results, pass_percentage

if __name__ == "__main__":
    test_cases = load_test_cases("test_cases.json")
    assistant_id = "asst_7wJ5VYgMJYjTtALPHdieu7sE"  # Replace with your assistant ID
    results, pass_percentage = evaluate_tests(test_cases, assistant_id)
    print(f"Test Results: {results}")
    print(f"Pass Percentage: {pass_percentage}%")

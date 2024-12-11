import os
import time
import requests

# Create a thread for the assistant to interact with
def create_thread(input_text):
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "ERROR: OpenAI API key not found in environment variables."

        url = "https://api.openai.com/v1/threads"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {"messages": [{"role": "user", "content": input_text}]}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            return response.json().get("id", "ERROR: No 'id' found in response.")
        else:
            return f"ERROR: {response.status_code} - {response.json()}"
    except Exception as e:
        return f"ERROR: {e}"

# Create a run to process the thread
def create_run(thread_id, assistant_id):
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "ERROR: OpenAI API key not found in environment variables."

        url = f"https://api.openai.com/v1/threads/{thread_id}/runs"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {"assistant_id": assistant_id}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 201:
            return response.json().get("id", "ERROR: No 'id' found in response.")
        else:
            return f"ERROR: {response.status_code} - {response.json()}"
    except Exception as e:
        return f"ERROR: {e}"

# Wait for the run to complete (added timeout to avoid infinite loops)
def wait_for_run(thread_id, run_id, timeout=60):
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "ERROR: OpenAI API key not found in environment variables."

        url = f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        start_time = time.time()
        while True:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                status = response.json().get("status", "ERROR: No 'status' in response.")
                if status == "completed":
                    return "completed"
                elif status in ["failed", "cancelled"]:
                    return f"ERROR: {status}"
            time.sleep(0.5)
            
            # Check for timeout
            if time.time() - start_time > timeout:
                return "ERROR: Timeout while waiting for run to complete."
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
            return response.json().get("data", [])
        else:
            return f"ERROR: {response.status_code} - {response.json()}"
    except Exception as e:
        return f"ERROR: {e}"

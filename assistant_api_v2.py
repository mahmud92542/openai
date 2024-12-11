### assistant_api_v2.py (Thread & Run creation)

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
            return response.json()["id"]
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
            return response.json()["id"]
        else:
            return f"ERROR: {response.status_code} - {response.json()}"
    except Exception as e:
        return f"ERROR: {e}"

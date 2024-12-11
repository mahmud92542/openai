import os
import time
from openai import OpenAI

def create_thread_and_attach_assistant(assistant_id):
    """
    Creates a new thread and attaches it to the assistant.
    
    Args:
        assistant_id (str): The ID of the assistant to attach the thread to.
    
    Returns:
        tuple: The thread ID and the assistant ID.
    """
    # Get OpenAI API Key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    
    # Create OpenAI client
    client = OpenAI(api_key=api_key)
    
    # Create a new thread
    thread = client.beta.threads.create()
    
    # Attach assistant to the thread
    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)
    
    return thread.id, assistant_id

if __name__ == "__main__":
    assistant_id = "asst_7wJ5VYgMJYjTtALPHdieu7sE"  # Replace with your assistant ID
    thread_id, assistant_id = create_thread_and_attach_assistant(assistant_id)
    print(f"Thread ID: {thread_id}, Assistant ID: {assistant_id}")

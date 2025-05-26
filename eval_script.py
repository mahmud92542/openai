import os
import json
import openai
from openai import OpenAI
from difflib import SequenceMatcher
import logging
import time

 # Set up logging
logging.basicConfig(filename='ai_test.log', level=logging.DEBUG,
                     format='%(asctime)s - %(levelname)s - %(message)s')


def load_test_cases(file_path):
     try:
         with open(file_path, "r") as f:
             return json.load(f)
     except Exception as e:
         logging.error(f"Error loading test cases: {e}")
         print(f"Error loading test cases: {e}")
         return None


def get_actual_output(input_text, assistant_id):
     try:
         openai_client = OpenAI()
         logging.info(f"Requesting actual output for input: {input_text}")

         thread = openai_client.beta.threads.create()
         thread_id = thread.id

         message = openai_client.beta.threads.messages.create(
             thread_id=thread_id,
             role="user",
             content=input_text
         )

         run = openai_client.beta.threads.runs.create(
             thread_id=thread_id,
             assistant_id=assistant_id,
         )

         tool_name = None
         tool_calls = []

         while True:
             run = openai_client.beta.threads.runs.retrieve(
                 thread_id=thread_id,
                 run_id=run.id
             )
             logging.info(f"Run status: {run.status}")
             if run.status == "completed":
                 break
             elif run.status == "requires_action":
                 tool_outputs = []
                 if hasattr(run.required_action, 'submit_tool_outputs'):
                     if hasattr(run.required_action.submit_tool_outputs, 'tool_calls'):
                         for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                             function_name = tool_call.function.name
                             arguments = tool_call.function.arguments
                             tool_call_id = tool_call.id
                             tool_name = function_name
                             tool_calls.append({"name": function_name, "arguments": arguments}) # Store tool name and arguments
                             logging.info(f"Tool call required: {function_name} with arguments {arguments}")
                             tool_output = execute_tool(function_name, arguments)
                             tool_outputs.append({
                                 "tool_call_id": tool_call_id,
                                 "output": tool_output,
                             })
                         openai_client.beta.threads.runs.submit_tool_outputs(
                             thread_id=thread_id,
                             run_id=run.id,
                             tool_outputs=tool_outputs,
                         )
             elif run.status in ["failed", "cancelled", "expired"]:
                 logging.error(f"Run failed with status: {run.status}")
                 print(f"Run failed with status: {run.status}. Error: {run.error}")
                 raise Exception(f"Run {run.status}. Error: {run.error}")
             time.sleep(1)

         messages = openai_client.beta.threads.messages.list(
             thread_id=thread_id,
             order="asc"
         )
         if not messages.data:
             logging.warning("No messages found in thread.")
             print("No messages found in thread.")
             openai_client.beta.threads.delete(thread_id)
             return "No messages found.", None

         assistant_message_content = None
         for message in reversed(messages.data):
             if message.role == "assistant":
                 if isinstance(message.content, list) and len(message.content) > 0:
                     assistant_message_content = message.content[0].text.value
                     logging.info(f"Actual output received: {assistant_message_content}")
                     break
                 else:
                     assistant_message_content = str(message.content).strip()
                     logging.info(f"Actual output received: {assistant_message_content}")
                     break

         openai_client.beta.threads.delete(thread_id)
         return assistant_message_content, tool_calls

     except Exception as e:
         logging.error(f"Error in get_actual_output: {e}")
         print(f"Error in get_actual_output: {e}")
         return f"ERROR: {e}", None

def execute_tool(function_name, arguments):
     try:
         arguments_dict = json.loads(arguments)  # Convert arguments string to dictionary
     except json.JSONDecodeError:
         logging.error(f"Error decoding arguments: {arguments}")
         return "Invalid arguments provided."
     except Exception as e:
         logging.error(f"Error in execute_tool: {e}")
         return f"Error: {e}"

     if function_name == "call_assistant_customerchurn":  # Renamed
         logging.info(f"{function_name} called")
         return "{}"  # Return an empty JSON object
     else:
         return f"Tool {function_name} not found."  # Ensure a string is returned


def compare_outputs(expected, actual, method="exact"):
     try:
         if method == "exact":
             return expected.strip().lower() == actual.strip().lower()
         elif method == "partial":
             return expected.strip().lower() in actual.strip().lower()
         elif method == "similarity":
             similarity = SequenceMatcher(None, expected.strip().lower(), actual.strip().lower()).ratio()
             return similarity
         elif method == "model_graded":
             logging.info("Using AI model to compare outputs")
             return model_graded(expected, actual)
         else:
             raise ValueError("Unknown comparison method.")
     except Exception as e:
         logging.error(f"Error in compare_outputs: {e}")
         return False


def model_graded(expected_output, actual_output):
     try:
         prompt = """
         You are an expert evaluator for AI assistant responses.
         Given the expected output and the actual output, determine if they are equivalent.
         Consider logical correctness, semantic meaning, and completeness.

         If the actual response is logically and semantically correct, reply with "PASS".
         Otherwise, reply with "FAIL".
         """
         test_data = f"""Expected output: {expected_output}
                         Actual output: {actual_output}"""

         logging.info("Sending request to GPT-4 to compare outputs")
         response = openai.chat.completions.create(
             model="gpt-4",
             messages=[
                 {"role": "system", "content": prompt},
                 {"role": "user", "content": test_data}
             ],
             max_tokens=10,
             temperature=0
         )

         gpt_output = response.choices[0].message.content.strip().upper()
         logging.info(f"AI Evaluation result: {gpt_output}")
         print(f"GPT-4 AI Evaluation: {gpt_output}")
         return gpt_output == "PASS"

     except openai.error.OpenAIError as e:
         logging.error(f"OpenAI API Error: {e}")
         print(f"OpenAI API Error: {e}")
         return False
     except Exception as e:
         logging.error(f"General Error: {e}")
         print(f"General Error: {e}")
         return False


def compare_tool_calls(expected_tool_name, actual_tool_calls):
     if not actual_tool_calls:
         logging.warning("No tools were called by the assistant.")
         print("No tools were called by the assistant.")
         return False

     for tool_call in actual_tool_calls:
         if tool_call.get("name") == expected_tool_name:
             logging.info(f"Expected tool '{expected_tool_name}' was called.")
             print(f"Expected tool '{expected_tool_name}' was called.")
             return True

     logging.info(
         f"Expected tool '{expected_tool_name}' was not called. Actual tools called: {[tc.get('name') for tc in actual_tool_calls]}")
     print(
         f"Expected tool '{expected_tool_name}' was not called. Actual tools called: {[tc.get('name') for tc in actual_tool_calls]}")
     return False


def evaluate_tests(test_cases):
     passed_tests = 0
     total_tests = len(test_cases)
     results = []

     openai.api_key = os.getenv("OPENAI_API_KEY")
     assistant_id = os.getenv("DEV_ASSISTANT_ID")
     if not assistant_id:
         logging.error("Assistant ID not found in environment variables.")
         print("Error: Assistant ID not found in environment variables.")
         return [], 0

     if test_cases is None:
         return [], 0

     for test in test_cases:
         logging.info(f"Running Test: {test['id']}")
         print(f"Running Test: {test['id']}")

         actual_output_text, tool_calls = get_actual_output(test["input"], assistant_id)

         comparison_method = test.get("comparison_method", "model_graded")
         expected_output = test.get("expected_output") # This can now be a string (for text) or a tool name

         if comparison_method == "tool_call":
             if not isinstance(expected_output, str):
                 logging.error(f"Test {test['id']}: 'expected_output' for 'tool_call' method must be a string (tool name).")
                 print(f"Test {test['id']}: 'expected_output' for 'tool_call' method must be a string (tool name).")
                 test_result = False
                 results.append((test['id'], "FAIL", tool_calls))
             else:
                 logging.info(f"Expected Tool Name: {expected_output}")
                 print(f"Expected Tool Name: {expected_output}")
                 logging.info(f"Tool Calls: {tool_calls}")
                 print(f"Tool Calls: {tool_calls}")
                 test_result = compare_tool_calls(expected_output, tool_calls)
                 logging.info(f"Tool Call Comparison Result: {'PASS' if test_result else 'FAIL'}")
                 print(f"Tool Call Comparison Result: {'PASS' if test_result else 'FAIL'}")
                 if test_result:
                     results.append((test['id'], "PASS", tool_calls))
                     passed_tests += 1
                 else:
                     results.append((test['id'], "FAIL", tool_calls))
         elif actual_output_text.startswith("ERROR"):
             test_result = False
             logging.error(f"Actual output was an error: {actual_output_text}")
             print(f"Actual: {actual_output_text}")
             results.append((test['id'], "FAIL", tool_calls))
         else:
             logging.info(f"Expected Output: {expected_output}")
             print(f"Expected Output: {expected_output}")
             logging.info(f"Actual: {actual_output_text}")
             print(f"Actual: {actual_output_text}")
             test_result = compare_outputs(
                 expected_output,
                 actual_output_text,
                 method=comparison_method
             )
             if test_result:
                 results.append((test['id'], "PASS", tool_calls))
                 passed_tests += 1
             else:
                 results.append((test['id'], "FAIL", tool_calls))

         print(f"Test {test['id']} Result: {'PASS' if test_result else 'FAIL'}")
         print("-" * 50)

     pass_percentage = (passed_tests / total_tests) * 100 if total_tests else 0
     logging.info(f"Pass percentage: {pass_percentage}%")
     print(f"Overall pass percentage: {pass_percentage}%")
     logging.info(f"Test Results: {results}")

     return results, pass_percentage


if __name__ == "__main__":
     openai.api_key = os.getenv("OPENAI_API_KEY")
     if not openai.api_key:
         print("Error: OpenAI API key not found in environment variables.")
         logging.error("Error: OpenAI API key not found in environment variables.")
         exit(1)

     test_cases = load_test_cases("test_cases.json")
     if test_cases is not None:
         results, pass_percentage = evaluate_tests(test_cases)
         print(f"Test Results: {results}")
         print(f"Overall pass percentage: {pass_percentage}%")
     else:
         print("Failed to load test cases. Exiting.")
         logging.error("Failed to load test cases. Exiting.")
         exit(1)

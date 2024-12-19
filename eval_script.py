import os
import json
import openai
from openai import OpenAI
from difflib import SequenceMatcher
import logging

# Set up logging to log all AI calls, responses, and debug info
logging.basicConfig(filename='ai_test.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_test_cases(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def get_actual_output(input_text, assistant_id="asst_7wJ5VYgMJYjTtALPHdieu7sE"):
    try:
        openai_client = OpenAI()
        logging.info(f"Requesting actual output for input: {input_text}")
        
        response = openai_client.beta.threads.create_and_run_poll(
            assistant_id=assistant_id,
            thread={
                "messages": [
                    {"role": "user", "content": input_text}
                ]
            }
        )

        thread_id = response.thread_id
        messages = openai_client.beta.threads.messages.list(
            thread_id=thread_id,
            order="asc"
        )
        logging.info(thread_id)
        for message in messages.data[::-1]:
            if message.role == "assistant":
                if isinstance(message.content, list) and len(message.content) > 0:
                    content_item = message.content[0]
                    text_value = message.content[0].text.value
                    logging.info(f"Actual output received: {text_value}")
                    return text_value
                else:
                    result = str(message.content).strip()
                    logging.info(f"Actual output received: {result}")
                    return result
    except Exception as e:
        logging.error(f"Error getting actual output: {e}")
        return f"ERROR: {e}"

def compare_outputs(expected, actual, method="exact"):
    """
    Compares expected and actual outputs using various methods.
    
    Args:
        expected (str): The expected output.
        actual (str): The actual output.
        method (str): The comparison method. Options are 'exact', 'partial', 'similarity', or 'model_graded'.
    
    Returns:
        bool: True if the comparison passes, False otherwise.
    """
    try:
        if method == "exact":
            return expected.strip().lower() == actual.strip().lower()
        
        elif method == "partial":
            return expected.strip().lower() in actual.strip().lower() 
        
        elif method == "similarity":
            similarity = SequenceMatcher(None, expected.strip().lower(), actual.strip().lower()).ratio()
            return similarity
        
        elif method == "model_graded":
            logging.info(f"Using AI model to compare expected and actual outputs")
            return model_graded(expected, actual)
        
        else:
            raise ValueError("Unknown comparison method: Choose 'exact', 'partial', 'similarity', or 'model_graded'.")

    except Exception as e:
        logging.error(f"Error in compare_outputs: {e}")
        return False


def model_graded(expected_output, actual_output):
    """
    Uses an AI model to evaluate if the expected and actual outputs are equivalent.
    
    Args:
        expected_output (str): The expected output.
        actual_output (str): The actual output.
    
    Returns:
        bool: True if the AI determines the responses are equivalent, False otherwise.
    """
    try:
        prompt = f"""
        You are an expert evaluator for AI assistant responses. 
        Given the expected output and the actual output, determine if they are equivalent. 
        Consider logical correctness, semantic meaning, and completeness.

        Expected: {expected_output}

        Actual: {actual_output}

        If the actual response is logically and semantically correct, reply with "PASS". 
        Otherwise, reply with "FAIL".
        """
        
        logging.info("Sending request to GPT-4 to compare outputs")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # GPT-4o mini rather than GPT-4
            messages=[
                {"role": "system", "content": "You are an expert evaluator of AI responses."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0
        )

        gpt_output = response.choices[0].message.content.strip().upper()
        
        logging.info(f"Response from GPT-4: {response}")
        logging.info(f"AI Evaluation result: {gpt_output}")

        if gpt_output not in ["PASS", "FAIL"]:
            logging.warning(f"Unexpected AI response: {gpt_output}")

        print(f"GPT-4 AI Evaluation: {gpt_output}")  # Print to console for live feedback
        return gpt_output == "PASS"

    except openai.error.OpenAIError as e:
        logging.error(f"OpenAI API Error: {e}")
        return False

    except Exception as e:
        logging.error(f"General Error: {e}")
        return False

def evaluate_tests(test_cases, assistant_id="asst_7wJ5VYgMJYjTtALPHdieu7sE"):
    passed_tests = 0
    total_tests = len(test_cases)
    results = []

    for test in test_cases:
        logging.info(f"Running Test: {test['id']}")
        print(f"Running Test: {test['id']}")

        actual_output = get_actual_output(test["input"], assistant_id)
        print(f"Expected: {test['expected_output']}")
        print(f"Actual: {actual_output}")

        test_result = model_graded(test["expected_output"], actual_output)

        if test_result:
            results.append((test['id'], "PASS"))
            passed_tests += 1
            logging.info(f"Test {test['id']} - PASS")
        else:
            results.append((test['id'], "FAIL"))
            logging.info(f"Test {test['id']} - FAIL")

        print(f"Test {test['id']} Result: {'PASS' if test_result else 'FAIL'}")
        print("-" * 50)

    pass_percentage = (passed_tests / total_tests) * 100
    logging.info(f"Pass percentage: {pass_percentage}%")
    print(f"Overall pass percentage: {pass_percentage}%")

    return results, pass_percentage

if __name__ == "__main__":
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        print("Error: OpenAI API key not found in environment variables.")
        logging.error("Error: OpenAI API key not found in environment variables.")
        exit(1)

    test_cases = load_test_cases("test_cases.json")
    results, pass_percentage = evaluate_tests(test_cases)
    logging.info(f"Test Results: {results}")
    print(f"Test Results: {results}")
    print(f"Overall pass percentage: {pass_percentage}%")

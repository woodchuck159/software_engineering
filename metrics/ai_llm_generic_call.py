import sys
import os
import time
from typing import Tuple, Optional

# --- Import Setup ---
# This block of code is crucial for allowing this script to find and import modules
# from the sibling 'classes' directory.

# Get the absolute path of the directory containing the current script (metrics/).
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate one level up to get the project's root directory (ece30861-team-8/).
project_root = os.path.dirname(current_dir)
# Construct the path to the 'classes' directory.
classes_path = os.path.join(project_root, 'classes')
# Add BOTH the project root and the classes directory to the Python system path.
# Adding 'classes_path' allows llm_child_api.py to find its sibling module 'api.py'.
sys.path.append(project_root)
sys.path.append(classes_path)

# Now that the project root is on the path, we can import from the 'classes' package.
# The file we are importing from is `llm_child_api.py`.
from classes.llm_child_api import GenAiChatApi

def process_file_and_get_response(filename: str, instruction: str, model: str) -> str:
    """
    Reads a .md or .txt file, prepends instructions, gets a response from the LLM,
    and measures the execution time.

    Args:
        filename (str): The path to the input file (.md or .txt).
        api_key (str): The API key for authentication.

    Returns:
        A tuple containing:
        - The LLM's response text (Optional[str]).
        - The total time spent in the function (float).
    """
    api_key = os.getenv("API_KEY", "YOUR_API_KEY_HERE") # Replace with your key if not set as env var
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("Error: API_KEY not set.")
        return

    if not filename.endswith(('.md', '.txt')):
        print("Error: Invalid file type. Please provide a .md or .txt file.")
        return None

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None

    # Instructions for the LLM
    prompt = instruction + file_content

    # Initialize the client
    chat_api = GenAiChatApi(
        base_url="https://genai.rcac.purdue.edu",
        model=model
    )

    # Set the token
    chat_api.set_bearer_token(api_key)

    # Get a completion
    print(f"\n> Sending content from '{filename}' to the model...")
    response_text = chat_api.get_chat_completion(prompt)

    
    return response_text

def main():
    """
    Example of how to use the GenAiChatApi class and the new processing function.
    """
    api_key = os.getenv("API_KEY", "YOUR_API_KEY_HERE") # Replace with your key if not set as env var
    if api_key == "YOUR_API_KEY_HERE":
        print("Error: API_KEY not set. Please set the environment variable or edit the script.")
        return

    # --- Example 1: Original direct prompt ---
    chat_api = GenAiChatApi(
        base_url="https://genai.rcac.purdue.edu",
        model="llama3.1:latest"
    )
    chat_api.set_bearer_token(api_key)
    prompt = "What are the three most important things to know about Python classes?"
    print(f"\n> Sending prompt: '{prompt}'")
    response_text = chat_api.get_chat_completion(prompt)
    if response_text:
        print("\n--- Model Response (Direct Prompt) ---")
        print(response_text)
        print("---------------------------------------")
    else:
        print("\nFailed to get a response from the model.")
        
    print("\n" + "="*50 + "\n")

    # --- Example 2: Using the new file processing function ---
    file_to_process = "sample_document.md"
    llm_response = process_file_and_get_response(file_to_process)

    if llm_response:
        print(f"\n--- Model Response (from {file_to_process}) ---")
        print(llm_response)
        print("------------------------------------------")
    else:
        print(f"\nFailed to get a response from the model for {file_to_process}.")


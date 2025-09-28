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
    api_key = os.getenv("GEN_AI_STUDIO_API_KEY", "YOUR_API_KEY_HERE") # Replace with your key if not set as env var
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        # print("Error: API_KEY not set.")
        return

    if not filename.endswith(('.md', '.txt')):
        # print("Error: Invalid file type. Please provide a .md or .txt file.")
        return None

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except FileNotFoundError:
        # print(f"Error: The file '{filename}' was not found.")
        return None
    except Exception as e:
        # print(f"An error occurred while reading the file: {e}")
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
    # print(f"\n> Sending content from '{filename}' to the model...")
    response_text = chat_api.get_chat_completion(prompt)

    
    return response_text



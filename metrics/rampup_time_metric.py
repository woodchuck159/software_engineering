import sys
import os
import time
from typing import Tuple

# --- Import Setup ---
# This block gets the project root onto the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Now we can import the function from the other file in the 'metrics' directory
from .ai_llm_generic_call import process_file_and_get_response

def rampup_time_metric(filename: str, verbosity: int, log_queue) -> Tuple[float, float]:
    """
    Calls an LLM to rate the "ramp-up" time for a model based on its readme, logging to a queue.

    Args:
        filename (str): The absolute path to the input file (.md or .txt).
        verbosity (int): The verbosity level (0=silent, 1=INFO, 2=DEBUG).
        log_queue (multiprocessing.Queue): The queue to send log messages to.

    Returns:
        A tuple containing:
        - The score from the LLM as a float (0.0 on error).
        - The total time spent (float).
    """
    start_time = time.time()
    pid = os.getpid() # Get process ID for clear log messages

    instruction = "Given the following readme, give a number from 0 to 1.0, with 1 being the best, on what the 'ramp-up' time of this model would be for a brand new engineer. Take into account things like the descriptions and examples given in the readme to make the score. ONLY PROVIDE A SINGLE NUMBER, NO OTHER TEXT SHOULD BE IN THE RESPONSE. IT SHOULD BE DIRECTLY CONVERTABLE TO A FLOAT:\n\n"

    try:
        if verbosity >= 1: # Informational
            log_queue.put(f"[{pid}] [INFO] Calling LLM for ramp-up time on '{os.path.basename(filename)}'...")

        llm_response_str = process_file_and_get_response(filename, instruction, "gemma3:1b")

        score = 0.0  # Default to 0.0 for failure cases

        # Safely convert the LLM's string response to a float
        if llm_response_str is not None:
            score = float(llm_response_str.strip())
            if verbosity >= 2: # Debug
                log_queue.put(f"[{pid}] [DEBUG] Successfully converted LLM response to score: {score}")
        else:
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [WARNING] Received no response from LLM for ramp-up time metric.")

    except (ValueError, TypeError):
        if verbosity >= 1: # Informational
            log_queue.put(f"[{pid}] [WARNING] Could not convert LLM response '{llm_response_str}' to a float.")
        score = 0.0 # Ensure score is -1 on conversion failure
    except Exception as e:
        # Log any other critical error before the process terminates
        if verbosity >0:
            log_queue.put(f"[{pid}] [CRITICAL ERROR] in rampup_time_metric: {e}")
        raise # Re-raise the exception to be caught by the worker
    
    end_time = time.time()
    time_taken = end_time - start_time
    
    return score, time_taken


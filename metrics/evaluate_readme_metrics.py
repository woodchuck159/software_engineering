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

def evaluate_readme_metrics(filename: str, verbosity: int, log_queue) -> Tuple[float, float, float]:
    """
    Calls an LLM to rate performance claims and ramp-up time from a readme file.

    This function sends the content of a given file to a language model and
    asks for two scores, comma-separated:
    1. Performance Claims: A score from 0.0 to 1.0 based on verifiable claims.
    2. Ramp-up Time: A score from 0.0 to 1.0 on the ease of getting started for a new engineer.

    It logs its progress to a queue and returns the two scores along with the total time taken.

    Args:
        filename (str): The absolute path to the input file (.md or .txt).
        verbosity (int): The verbosity level (0=silent, 1=INFO, 2=DEBUG).
        log_queue (multiprocessing.Queue): The queue to send log messages to.

    Returns:
        A tuple containing:
        - The performance claims score as a float (0.0 on error).
        - The ramp-up time score as a float (0.0 on error).
        - The total time spent (latency) as a float.
    """
    start_time = time.time()
    pid = os.getpid()  # Get process ID for clear log messages

    # The combined instruction for the language model
    instruction = (
        "Given the following readme, provide two numbers separated by a single comma. "
        "The first number, from 0.0 to 1.0, should rate the performance claims of this model, with 1.0 being the best. "
        "Consider verifiable claims and evidence. "
        "The second number, from 0.0 to 1.0, should rate the 'ramp-up' time for a new engineer, with 1.0 being the easiest/fastest. "
        "Consider the quality of descriptions and examples. "
        "YOUR RESPONSE MUST BE ONLY THE TWO NUMBERS SEPARATED BY A COMMA (e.g., '0.8, 0.6'). "
        "DO NOT INCLUDE ANY OTHER TEXT.\n\n"
    )

    performance_score = 0.0
    rampup_score = 0.0

    try:
        if verbosity >= 1:  # Informational
            log_queue.put(f"[{pid}] [INFO] Calling LLM for combined metrics on '{os.path.basename(filename)}'...")

        llm_response_str = process_file_and_get_response(filename, instruction, "gemma3:1b")

        if llm_response_str:
            # Attempt to parse the two comma-separated values
            parts = llm_response_str.strip().split(',')
            if len(parts) == 2:
                performance_score = float(parts[0].strip())
                rampup_score = float(parts[1].strip())
                if verbosity >= 2:  # Debug
                    log_queue.put(f"[{pid}] [DEBUG] LLM response parsed to scores: Perf={performance_score}, RampUp={rampup_score}")
            else:
                if verbosity >= 1: # Informational
                    log_queue.put(f"[{pid}] [WARNING] LLM response '{llm_response_str}' was not in the expected 'num,num' format.")
        else:
            if verbosity >= 1:  # Informational
                log_queue.put(f"[{pid}] [WARNING] Received no response from LLM for combined metrics.")

    except (ValueError, TypeError, IndexError) as e:
        if verbosity >= 1:  # Informational
            log_queue.put(f"[{pid}] [WARNING] Could not parse LLM response '{llm_response_str}'. Error: {e}")
        # Ensure scores are reset to 0.0 on any parsing failure
        performance_score = 0.0
        rampup_score = 0.0
    except Exception as e:
        # Log any other critical error before the process terminates
        if verbosity > 0:
            log_queue.put(f"[{pid}] [CRITICAL ERROR] in evaluate_readme_metrics: {e}")
        raise  # Re-raise the exception to be caught by the worker

    end_time = time.time()
    time_taken = end_time - start_time

    return performance_score, rampup_score, time_taken
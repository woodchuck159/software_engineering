import os
import time
import subprocess
from typing import Tuple

def code_quality(github_str: str, verbosity: int, log_queue) -> Tuple[float, float]:
    """
    Computes the PyLint score for a Python file, logging its progress to a queue.

    Args:
        github_str (str): The GitHub repository string (e.g., "owner/repo").
        verbosity (int): The verbosity level (0=silent, 1=info, 2=debug).
        log_queue (multiprocessing.Queue): The queue to send log messages to.

    Returns:
        A tuple containing:
        - The PyLint score scaled from 0.0 to 1.0.
        - The total time spent (float).
    """
    start_time = time.perf_counter()
    pid = os.getpid()
    score = 0.0  # Default score for any failure

    if verbosity >= 1:
        log_queue.put(f"[{pid}] Running PyLint on '{os.path.basename(github_str)}'...")

    try:
        # Run PyLint and capture output. check=False prevents an exception on non-zero exit codes.
        result = subprocess.run(
            ["pylint", github_str, "--score=y"],
            capture_output=True,
            text=True,
            check=False
        )

        output = result.stdout or result.stderr
        found_score = False

        # Look for the line that contains the score
        for line in output.splitlines():
            if "Your code has been rated at" in line:
                # Example: 'Your code has been rated at 8.56/10'
                parts = line.split(" ")
                for part in parts:
                    if "/" in part:
                        score_str = part.split("/")[0]
                        # Scale the score (e.g., 8.56) to be between 0.0 and 1.0
                        score = float(score_str) / 10.0
                        found_score = True
                        if verbosity >= 1:
                            log_queue.put(f"[{pid}] Found PyLint score for '{os.path.basename(github_str)}': {score*10:.2f}/10")
                        break  # Inner loop
                if found_score:
                    break  # Outer loop
        
        if not found_score:
            log_queue.put(f"[{pid}] [WARNING] Could not find PyLint score line in output for '{github_str}'.")
            if verbosity >= 2:
                log_queue.put(f"[{pid}] [DEBUG] PyLint output for '{github_str}':\n---BEGIN---\n{output}\n---END---")

    except FileNotFoundError:
        if verbosity >0:
            log_queue.put(f"[{pid}] [CRITICAL ERROR] 'pylint' command not found. Is PyLint installed and in the system's PATH?")
    except Exception as e:
        if verbosity >0:
            log_queue.put(f"[{pid}] [CRITICAL ERROR] running PyLint on '{github_str}': {e}")
        if verbosity >= 2:
            # The captured output might be useful for debugging the exception
            log_queue.put(f"[{pid}] [DEBUG] PyLint output for '{github_str}':\n---BEGIN---\n{output}\n---END---")
    
    end_time = time.perf_counter()
    time_taken = end_time - start_time
    
    return score, time_taken

if __name__ == "__main__":
    score = get_pylint_score("./classes/api.py")
    print("PyLint code quality score:", score)

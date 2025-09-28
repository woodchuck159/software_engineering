import multiprocessing
import re
import os
import importlib
import shutil
import time
import inspect
from collections import defaultdict

def parse_keys_from_string(key_string: str) -> list[str]:
    """Parses a comma-separated string of keys into a clean list."""
    if not key_string.strip():
        return []
    return [key.strip() for key in key_string.split(',')]

def logger_process(log_queue: multiprocessing.Queue, log_file_path: str):
    """
    A dedicated process that listens for messages on a queue and writes them to a log file.
    """
    try:
        with open(log_file_path, 'w', encoding='utf-8') as f:
            f.write(f"--- Log started at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
            while True:
                message = log_queue.get()
                if message is None: # A 'None' message is our signal to stop
                    f.write(f"--- Log ended at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
                    break
                f.write(f"{message}\n")
                f.flush() # Ensure messages are written immediately
    except Exception as e:
        print(f"[Logger Process Error] An error occurred: {e}")


def process_worker(target_func, result_queue, weight, func_name, *args):
    """
    Worker that executes the target function and handles any exceptions,
    returning a score of 0.0 upon failure.
    """
    start_time = time.perf_counter()
    try:
        score, time_taken = target_func(*args)
        result_queue.put((score, float(time_taken), float(weight), func_name))
    except Exception as e:
        time_taken = time.perf_counter() - start_time
        # The metric function itself should use the log_queue to report its error before failing.
        # This is a fallback print for critical failures in the worker itself.
        print(f"[WORKER CRASH] Process for '{func_name}' failed critically: {e}")
        result_queue.put((0.0, time_taken, float(weight), func_name))

def load_available_functions(directory: str, script_verbosity: int = 1) -> dict:
    # This function remains the same.
    functions = {}
    if script_verbosity > 0: print(f"Discovering functions in './{directory}/'...")
    for filename in os.listdir(directory):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"{directory}.{module_name}")
                func = getattr(module, module_name)
                functions[module_name] = func
                if script_verbosity > 0: print(f"  - Loaded function: '{module_name}'")
            except (ImportError, AttributeError) as e:
                if script_verbosity > 0: print(f"  - Could not load '{module_name}': {e}")
    return functions

def run_concurrently_from_file(tasks_filename: str, all_args_dict: dict, available_functions: dict, log_file: str, script_verbosity: int = 1):
    """
    Parses a file, runs functions concurrently, and manages centralized logging.
    """
    manager = multiprocessing.Manager()
    log_queue = manager.Queue()
    
    # Start the dedicated logger process
    logger = multiprocessing.Process(target=logger_process, args=(log_queue, log_file))
    logger.start()

    # Add the log queue to the dictionary of available arguments for our metrics
    all_args_dict['log_queue'] = log_queue

    line_pattern = re.compile(r'(\w+)\((.*)\)\s*([\d.]+)')
    processes = []
    results_queue = multiprocessing.Queue()
    total_weight = 0.0 # Accumulator for the total weight of all valid metrics

    if script_verbosity > 0: print(f"\nReading and parsing tasks from '{tasks_filename}'...")
    
    with open(tasks_filename, 'r', encoding="utf-8") as f:
        # (The parsing and validation logic remains largely the same)
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line: continue
            match = line_pattern.match(line)
            if not match:
                log_queue.put(f"[WARNING] Skipped line {i}: Could not parse syntax: '{line}'.")
                continue

            func_name, keys_str, weight_str = match.groups()
            
            if func_name not in available_functions:
                log_queue.put(f"[WARNING] Skipped line {i}: Function '{func_name}' not found.")
                continue

            target_func = available_functions[func_name]
            required_keys = parse_keys_from_string(keys_str)
            
            sig = inspect.signature(target_func)
            expected_count = len(sig.parameters)
            provided_count = len(required_keys)

            if provided_count != expected_count:
                log_queue.put(f"[WARNING] Skipped line {i}: '{func_name}' expects {expected_count} args, but {provided_count} keys were provided.")
                continue
            
            if not all(key in all_args_dict for key in required_keys):
                missing = [key for key in required_keys if key not in all_args_dict]
                log_queue.put(f"[WARNING] Skipped line {i}: Missing required keys in input dictionary: {missing}")
                continue

            resolved_args = [all_args_dict[key] for key in required_keys]
            weight = float(weight_str)
            process_args = (target_func, results_queue, weight, func_name) + tuple(resolved_args)
            process = multiprocessing.Process(target=process_worker, args=process_args)
            processes.append(process)
            total_weight += weight # Add the weight of this valid metric to the total
            if script_verbosity > 0: print(f'  - Queued: {func_name}(...) with weight {weight}')

    if not processes:
        if script_verbosity > 0: print("\nNo valid tasks to run.")
        log_queue.put(None) # Tell logger to stop
        logger.join()
        return {'net_score': 0.0}, {}
    
    if script_verbosity > 0: print("\n--- Starting all processes ---")
    concurrent_start_time = time.perf_counter()
    for p in processes: p.start()
    
    if script_verbosity > 0: print("--- Collecting results ---")
    times_dictionary = { "net_score_latency": 0.0 }
    scores_dictionary = {}
    weighted_score_sum = 0.0
    
    for _ in range(len(processes)):
        score, time_taken, weight, func_name = results_queue.get()
        
        # --- FIX: Use the function name directly as the key ---
        scores_dictionary[func_name] = score
        times_dictionary[func_name] = round(time_taken * 1000)
        if func_name != "calculate_size_score":
            weighted_score_sum += score * weight
        else:
             weighted_score_sum += (sum(score.values()) / len(score) if score else 0.0) * weight
    
    # Calculate net_score as a weighted average
    if total_weight > 0:
        net_score = weighted_score_sum / total_weight
    else:
        net_score = 0.0
            
    scores_dictionary['net_score'] = net_score

    concurrent_end_time = time.perf_counter()
    times_dictionary["net_score_latency"] = concurrent_end_time - concurrent_start_time

    for p in processes: p.join()
    if script_verbosity > 0: print("\n--- All processes have completed ---")
    
    # --- SHUTDOWN ---
    # Tell the logger process it's time to exit
    log_queue.put(None)
    # Wait for the logger process to finish writing any remaining messages
    logger.join()
    
    return scores_dictionary, times_dictionary


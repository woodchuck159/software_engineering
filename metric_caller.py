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

def process_worker(target_func, result_queue, weight, func_name, *args):
    """
    Worker that executes the target function and handles any exceptions,
    returning a score of -1.0 upon failure.
    """
    start_time = time.perf_counter()
    try:
        # Execute the actual metric function
        score, time_taken = target_func(*args)
        result_queue.put((float(score), float(time_taken), float(weight), func_name))
    except Exception as e:
        # If any exception occurs, catch it and return -1.0
        time_taken = time.perf_counter() - start_time
        print(f"🔥 [Process {os.getpid()}] Function '{func_name}' failed: {e}")
        result_queue.put((-1.0, time_taken, float(weight), func_name))

def load_available_functions(directory: str, script_verbosity: int = 1) -> dict:
    # This function remains the same.
    functions = {}
    if script_verbosity > 0: print(f"🔍 Discovering functions in './{directory}/'...")
    for filename in os.listdir(directory):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"{directory}.{module_name}")
                func = getattr(module, module_name)
                functions[module_name] = func
                if script_verbosity > 0: print(f"  - Loaded function: '{module_name}'")
            except (ImportError, AttributeError) as e:
                if script_verbosity > 0: print(f"  - ⚠️  Could not load '{module_name}': {e}")
    return functions

def run_concurrently_from_file(tasks_filename: str, all_args_dict: dict, available_functions: dict, script_verbosity: int = 1):
    """
    Parses a file, resolves arguments from a dictionary, runs functions concurrently,
    and returns dictionaries of scores and times.
    """
    line_pattern = re.compile(r'(\w+)\((.*)\)\s*([\d.]+)')
    processes = []
    results_queue = multiprocessing.Queue()

    if script_verbosity > 0: print(f"\nReading and parsing tasks from '{tasks_filename}'...")
    
    with open(tasks_filename, 'r', encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line: continue
            match = line_pattern.match(line)
            if not match:
                if script_verbosity > 0: print(f"  - ⚠️  Skipped line {i}: Could not parse syntax: '{line}'.")
                continue

            func_name, keys_str, weight_str = match.groups()
            
            if func_name not in available_functions:
                if script_verbosity > 0: print(f"  - ⚠️  Skipped line {i}: Function '{func_name}' not found.")
                continue

            target_func = available_functions[func_name]
            required_keys = parse_keys_from_string(keys_str)
            
            # --- VALIDATION AND ARGUMENT RESOLUTION ---
            sig = inspect.signature(target_func)
            expected_count = len(sig.parameters)
            provided_count = len(required_keys)

            if provided_count != expected_count:
                if script_verbosity > 0: print(f"  - ⚠️  Skipped line {i}: '{func_name}' expects {expected_count} args, but {provided_count} keys were provided.")
                continue

            # Check if all required keys exist in the main dictionary
            if not all(key in all_args_dict for key in required_keys):
                missing = [key for key in required_keys if key not in all_args_dict]
                if script_verbosity > 0: print(f"  - ⚠️  Skipped line {i}: Missing required keys in input dictionary: {missing}")
                continue

            # If all checks pass, resolve values and queue the process
            resolved_args = [all_args_dict[key] for key in required_keys]
            weight = float(weight_str)
            process_args = (target_func, results_queue, weight, func_name) + tuple(resolved_args)
            process = multiprocessing.Process(target=process_worker, args=process_args)
            processes.append(process)
            if script_verbosity > 0: print(f'  - ✅ Queued: {func_name}(...) with weight {weight}')

    # --- Execution and Result Collection ---
    if not processes:
        if script_verbosity > 0: print("\nNo valid tasks to run.")
        return {'net_score': 0.0}, {}
    
    if script_verbosity > 0: print("\n--- Starting all processes ---")
    for p in processes: p.start()
    
    if script_verbosity > 0: print("--- Collecting results ---")
    times_dictionary = {}
    scores_dictionary = {}
    net_score = 0.0
    func_call_counts = defaultdict(int)

    for _ in range(len(processes)):
        score, time_taken, weight, func_name = results_queue.get()
        
        # Create a unique key for each function call (e.g., "code_quality_check_1")
        func_call_counts[func_name] += 1
        unique_key = f"{func_name}_{func_call_counts[func_name]}"
        
        scores_dictionary[unique_key] = score
        times_dictionary[unique_key] = time_taken
        
        # Exclude failed runs (score == -1) from the net score
        if score != -1.0:
            net_score += score * weight

    scores_dictionary['net_score'] = net_score

    for p in processes: p.join()
    if script_verbosity > 0: print("\n--- All processes have completed ---")
    
    return scores_dictionary, times_dictionary


if __name__ == "__main__":
    # --- 1. SETUP ---
    functions_dir = "functions"
    os.makedirs(functions_dir, exist_ok=True)
    with open(os.path.join(functions_dir, "__init__.py"), "w") as f: pass
    
    # Create dummy files for the quality check function
    with open("main_file.py", "w") as f: f.write("# TODO: Fix this later\nprint('hello')\n# TODO: Add tests")
    with open("test_file.py", "w") as f: f.write("assert True")
    
    with open(os.path.join(functions_dir, "code_quality_check.py"), "w", encoding="utf-8") as f:
        f.write("import os, time\n")
        f.write("def code_quality_check(file_path: str, verbosity: int) -> tuple[float, float]:\n")
        f.write("    start_time = time.perf_counter()\n")
        f.write("    pid = os.getpid()\n")
        f.write("    if verbosity > 0: print(f'🚀 [Process ID: {pid}] Checking quality of \\'{file_path}\\'')\n")
        f.write("    time.sleep(1)\n")
        f.write("    try:\n")
        f.write("        with open(file_path, 'r') as f: content = f.read()\n")
        f.write("        todo_count = content.upper().count('TODO')\n")
        f.write("        score = max(0, 100 - (todo_count * 10))\n")
        f.write("    except FileNotFoundError:\n")
        f.write("        if verbosity > 0: print(f'🔥 [Process ID: {pid}] ERROR: File not found: {file_path}')\n")
        f.write("        raise\n")
        f.write("    end_time = time.perf_counter()\n")
        f.write("    time_taken = end_time - start_time\n")
        f.write("    if verbosity > 0: print(f'✅ [Process ID: {pid}] Finished code_quality_check. Score: {score}, Time: {time_taken:.4f}s')\n")
        f.write("    return score, time_taken\n")

    with open(os.path.join(functions_dir, "api_latency_test.py"), "w", encoding="utf-8") as f:
        f.write("import os, time\n")
        f.write("def api_latency_test(api_endpoint: str, timeout: int, verbosity: int) -> tuple[float, float]:\n")
        f.write("    start_time = time.perf_counter()\n")
        f.write("    pid = os.getpid()\n")
        f.write("    if verbosity > 0: print(f'📝 [Process ID: {pid}] Testing latency for \\'{api_endpoint}\\' with timeout {timeout}s')\n")
        f.write("    simulated_latency = 0.75\n")
        f.write("    time.sleep(simulated_latency)\n")
        f.write("    score = 100 - (simulated_latency * 20)\n")
        f.write("    end_time = time.perf_counter()\n")
        f.write("    time_taken = end_time - start_time\n")
        f.write("    if verbosity > 0: print(f'👍 [Process ID: {pid}] Finished api_latency_test. Score: {score:.2f}, Time: {time_taken:.4f}s')\n")
        f.write("    return score, time_taken\n")
        
    with open(os.path.join(functions_dir, "failing_task.py"), "w", encoding="utf-8") as f:
        f.write("import os, time\n")
        f.write("def failing_task(message: str, verbosity: int) -> tuple[float, float]:\n")
        f.write("    if verbosity > 0: print(f'🔥 [Process ID: {os.getpid()}] Starting a task that is designed to fail...')\n")
        f.write("    time.sleep(0.2)\n")
        f.write("    raise ValueError('This is an intentional failure for demonstration.')\n")
        f.write("    return 0.0, 0.0\n")

    tasks_filename = "tasks.txt"
    # with open(tasks_filename, "w", encoding="utf-8") as f:
    #     f.write('code_quality_check(main_file, verbosity_level) 1.5\n')
    #     f.write('api_latency_test(endpoint_url, api_timeout, verbosity_level) 0.5\n')
    #     f.write('code_quality_check(test_file, verbosity_level) 2.0\n')
    #     f.write('failing_task(fail_message, verbosity_level) 1.0\n') # Will fail
    #     f.write('code_quality_check(non_existent_file, verbosity_level) 1.0\n') # Will also fail

    # --- 2. EXECUTION ---
    # The single dictionary argument containing ALL possible parameters.
    all_parameters = {
        "main_file": "main_file.py",
        "test_file": "test_file.py",
        "non_existent_file": "no_file.txt",
        "endpoint_url": "https://api.example.com/v1/status",
        "api_timeout": 30,
        "verbosity_level": 1,
        "fail_message": "This task will fail.",
        "readme" : "C:/Users/aleca/Documents/GitHub/ece30861-team-8/functions/readme_testcases/sample_readme.md"
    }
    
    AVAILABLE_FUNCTIONS = load_available_functions(functions_dir)
    
    final_scores, final_times = run_concurrently_from_file(
        tasks_filename,
        all_parameters,
        AVAILABLE_FUNCTIONS
    )
    
    # --- 3. DISPLAY RESULTS ---
    print("\n" + "="*50)
    print(" " * 18 + "FINAL RESULTS")
    print("="*50)
    print("Scores by Function Call:")
    if final_scores:
        for name, s in final_scores.items():
            if name == 'net_score': continue
            print(f"  - {name:<30}: {s:.2f}")
    print("-" * 50)
    print(f"  - {'net_score':<30}: {final_scores.get('net_score', 0.0):.2f}")
    print("="*50)
    print("Execution Times by Function Call:")
    if final_times:
        for name, t in final_times.items():
            print(f"  - {name:<30}: {t:.4f}s")
    else:
        print("  - No functions were executed.")
    print("="*50)

    # --- 4. CLEANUP ---
    # os.remove(tasks_filename)
    # os.remove("main_file.py")
    # os.remove("test_file.py")
    # shutil.rmtree(functions_dir)
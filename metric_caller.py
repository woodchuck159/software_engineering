import multiprocessing
import re
import os
import importlib
import shutil
import time
import inspect # <-- Import the inspect module

# The parse_and_convert_args and process_worker functions remain the same as the previous version.
def parse_and_convert_args(arg_string: str) -> list:
    string_args = re.findall(r'"[^"]*"|[\w.-]+', arg_string)
    final_args = []
    for arg in string_args:
        if arg.startswith('"') and arg.endswith('"'):
            final_args.append(arg[1:-1]); continue
        try:
            final_args.append(int(arg)); continue
        except ValueError: pass
        try:
            final_args.append(float(arg)); continue
        except ValueError: pass
        final_args.append(arg)
    return final_args

def process_worker(target_func, result_queue, weight, func_name, *args):
    score, time_taken = target_func(*args)
    result_queue.put((float(score), float(time_taken), float(weight), func_name))

# load_available_functions also remains the same.
def load_available_functions(directory: str, script_verbosity: int = 1) -> dict:
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


def run_concurrently_from_file(filename: str, available_functions: dict, script_verbosity: int = 1):
    """
    Parses a file, validates argument counts for each function, and runs them concurrently.
    """
    line_pattern = re.compile(r'(\w+)\((.*)\)\s*([\d.]+)')
    processes = []
    results_queue = multiprocessing.Queue()

    if script_verbosity > 0: print(f"\nReading and parsing tasks from '{filename}'...")
    
    with open(filename, 'r', encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line: continue
            match = line_pattern.match(line)
            if match:
                func_name, args_str, weight_str = match.groups()
                if func_name in available_functions:
                    target_func = available_functions[func_name]
                    final_args = parse_and_convert_args(args_str)
                    
                    # --- NEW VALIDATION LOGIC ---
                    try:
                        sig = inspect.signature(target_func)
                        expected_count = len(sig.parameters)
                        provided_count = len(final_args)
                        
                        if provided_count == expected_count:
                            # If valid, create the process as before
                            weight = float(weight_str)
                            process_args = (target_func, results_queue, weight, func_name) + tuple(final_args)
                            process = multiprocessing.Process(target=process_worker, args=process_args)
                            processes.append(process)
                            if script_verbosity > 0: print(f'  - ✅ Queued: {func_name}(...) with weight {weight}')
                        else:
                            # If invalid, print a warning and skip
                            if script_verbosity > 0:
                                print(f"  - ⚠️  Skipped line {i}: '{func_name}' expects {expected_count} arguments, but {provided_count} were given.")
                    except ValueError:
                        if script_verbosity > 0: print(f"  - ⚠️  Skipped line {i}: Could not inspect signature for '{func_name}'.")

                elif script_verbosity > 0: print(f"  - ⚠️  Skipped line {i}: Function '{func_name}' not found.")
            elif script_verbosity > 0: print(f"  - ⚠️  Skipped line {i}: Could not parse syntax: '{line}'.")

    # --- Execution and Result Collection (This part remains the same) ---
    if not processes:
        if script_verbosity > 0: print("\nNo valid tasks to run.")
        return 0.0, {}

    if script_verbosity > 0: print("\n--- Starting all processes ---")
    for p in processes: p.start()
    if script_verbosity > 0: print("--- Collecting results ---")
    times_dictionary = {}
    net_score = 0.0
    for _ in range(len(processes)):
        score, time_taken, weight, func_name = results_queue.get()
        net_score += score * weight
        times_dictionary[func_name] = time_taken
    for p in processes: p.join()
    if script_verbosity > 0: print("\n--- All processes have completed ---")
    return net_score, times_dictionary


if __name__ == "__main__":
    # --- 1. SETUP ---
    functions_dir = "functions"
    os.makedirs(functions_dir, exist_ok=True)
    with open(os.path.join(functions_dir, "__init__.py"), "w", encoding="utf-8") as f: pass
    
    with open(os.path.join(functions_dir, "process_data.py"), "w", encoding="utf-8") as f:
        f.write("import os, time\n")
        f.write("def process_data(message: str, base_score: int) -> tuple[float, float]:\n")
        f.write("    start_time = time.perf_counter()\n")
        f.write("    pid = os.getpid()\n")
        f.write("    print(f'🚀 [Process ID: {pid}] Processing \\'{message}\\' with base score {base_score}')\n")
        f.write("    time.sleep(1)\n")
        f.write("    score = float(base_score + len(message))\n")
        f.write("    end_time = time.perf_counter()\n")
        f.write("    time_taken = end_time - start_time\n")
        f.write("    print(f'✅ [Process ID: {pid}] Finished process_data. Score: {score}, Time: {time_taken:.4f}s')\n")
        f.write("    return score, time_taken\n")
        
    with open(os.path.join(functions_dir, "log_activity.py"), "w", encoding="utf-8") as f:
        f.write("import os, time\n")
        f.write("def log_activity(activity_name: str) -> tuple[float, float]:\n")
        f.write("    start_time = time.perf_counter()\n")
        f.write("    pid = os.getpid()\n")
        f.write("    print(f'📝 [Process ID: {pid}] Logging activity: \\'{activity_name}\\'')\n")
        f.write("    time.sleep(0.5)\n")
        f.write("    score = 5.0\n")
        f.write("    end_time = time.perf_counter()\n")
        f.write("    time_taken = end_time - start_time\n")
        f.write("    print(f'👍 [Process ID: {pid}] Finished log_activity. Score: {score}, Time: {time_taken:.4f}s')\n")
        f.write("    return score, time_taken\n")

    tasks_filename = "tasks.txt"
    with open(tasks_filename, "w", encoding="utf-8") as f:
        f.write('process_data("Analyze system performance", 100) 1.5\n')
        f.write('log_activity("User login successful") 0.5\n')
        f.write('process_data("Generate weekly report", 50, "extra_arg") 2.0\n') # Invalid
        f.write('log_activity("Database backup complete") 0.2\n')

    # --- 2. EXECUTION ---
    AVAILABLE_FUNCTIONS = load_available_functions(functions_dir)
    net_score, time_dictionary = run_concurrently_from_file(tasks_filename, AVAILABLE_FUNCTIONS)
    
    print("\n" + "="*50)
    print(" " * 18 + "FINAL RESULTS")
    print("="*50)
    print(f"Net Score:             {net_score:.2f}")
    print("-" * 50)
    print("Execution Times by Function:")
    if time_dictionary:
        for name, t in time_dictionary.items():
            print(f"  - {name:<20}: {t:.4f}s")
    else:
        print("  - No functions were executed.")
    print("="*50)

    # --- 3. CLEANUP ---
    # os.remove(tasks_filename)
    # shutil.rmtree(functions_dir)
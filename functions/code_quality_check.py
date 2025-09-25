import os, time
def code_quality_check(file_path: str, verbosity: int, log_queue) -> tuple[float, float]:
    start_time = time.perf_counter()
    pid = os.getpid()
    if verbosity > 0: log_queue.put(f'[{pid}] Checking quality of \'{file_path}\'')
    time.sleep(1)
    try:
        with open(file_path, 'r') as f: content = f.read()
        todo_count = content.upper().count('TODO')
        score = max(0, 100 - (todo_count * 10))
    except FileNotFoundError:
        if verbosity > 0: log_queue.put(f'[{pid}] ERROR: File not found: {file_path}')
        raise
    end_time = time.perf_counter()
    time_taken = end_time - start_time
    if verbosity > 0: log_queue.put(f'[{pid}] Finished code_quality_check. Score: {score}, Time: {time_taken:.4f}s')
    return score, time_taken

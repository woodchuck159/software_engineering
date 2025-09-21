import os, time
def log_message(message: str, verbosity: int) -> tuple[float, float]:
    start_time = time.perf_counter()
    pid = os.getpid()
    if verbosity > 0: print(f'📝 [Process ID: {pid}] Logging message: \'{message}\'')
    time.sleep(0.5)
    score = float(len(message))
    end_time = time.perf_counter()
    time_taken = end_time - start_time
    if verbosity > 0: print(f'👍 [Process ID: {pid}] Logged. Score: {score}, Time: {time_taken:.4f}s')
    return score, time_taken

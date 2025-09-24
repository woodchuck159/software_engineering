import os, time
def log_activity(activity_name: str) -> tuple[float, float]:
    start_time = time.perf_counter()
    pid = os.getpid()
    print(f'📝 [Process ID: {pid}] Logging activity: \'{activity_name}\'')
    time.sleep(0.5)
    score = 5.0
    end_time = time.perf_counter()
    time_taken = end_time - start_time
    print(f'👍 [Process ID: {pid}] Finished log_activity. Score: {score}, Time: {time_taken:.4f}s')
    return score, time_taken

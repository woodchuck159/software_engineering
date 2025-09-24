import os, time
def process_data(message: str, base_score: int) -> tuple[float, float]:
    start_time = time.perf_counter()
    pid = os.getpid()
    print(f'🚀 [Process ID: {pid}] Processing \'{message}\' with base score {base_score}')
    time.sleep(1)
    score = float(base_score + len(message))
    end_time = time.perf_counter()
    time_taken = end_time - start_time
    print(f'✅ [Process ID: {pid}] Finished process_data. Score: {score}, Time: {time_taken:.4f}s')
    return score, time_taken

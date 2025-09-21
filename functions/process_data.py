import os, time, hashlib
def process_data(data: str, verbosity: int) -> tuple[float, float]:
    start_time = time.perf_counter()
    pid = os.getpid()
    if verbosity > 0: print(f'🚀 [Process ID: {pid}] Processing data: \'{data}\'')
    time.sleep(1)
    hash_object = hashlib.md5(data.encode())
    score = int(hash_object.hexdigest(), 16) % 1000 / 10.0
    end_time = time.perf_counter()
    time_taken = end_time - start_time
    if verbosity > 0: print(f'✅ [Process ID: {pid}] Finished. Score: {score}, Time: {time_taken:.4f}s')
    return score, time_taken

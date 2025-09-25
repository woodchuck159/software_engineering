import os, time
def api_latency_test(api_endpoint: str, timeout: int, verbosity: int) -> tuple[float, float]:
    start_time = time.perf_counter()
    pid = os.getpid()
    if verbosity > 0: print(f'📝 [Process ID: {pid}] Testing latency for \'{api_endpoint}\' with timeout {timeout}s')
    simulated_latency = 0.75
    time.sleep(simulated_latency)
    score = 100 - (simulated_latency * 20)
    end_time = time.perf_counter()
    time_taken = end_time - start_time
    if verbosity > 0: print(f'👍 [Process ID: {pid}] Finished api_latency_test. Score: {score:.2f}, Time: {time_taken:.4f}s')
    return score, time_taken

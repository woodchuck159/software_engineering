import os, time
def failing_task(message: str, verbosity: int, log_queue) -> tuple[float, float]:
    pid = os.getpid()
    if verbosity > 0: log_queue.put(f'[{pid}] Starting a task that is designed to fail...')
    time.sleep(0.2)
    raise ValueError('This is an intentional failure for demonstration.')
    return 0.0, 0.0

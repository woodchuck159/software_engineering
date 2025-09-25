import os, time
def failing_task(message: str, verbosity: int) -> tuple[float, float]:
    if verbosity > 0: print(f'🔥 [Process ID: {os.getpid()}] Starting a task that is designed to fail...')
    time.sleep(0.2)
    raise ValueError('This is an intentional failure for demonstration.')
    return 0.0, 0.0

import os, time
def log_message(message: str, verbosity: int) -> float:
    pid = os.getpid()
    if verbosity > 0: print(f'📝 [Process ID: {pid}] Logging message: \'{message}\'')
    time.sleep(0.5)
    score = float(len(message))
    if verbosity > 0: print(f'👍 [Process ID: {pid}] Message logged. Score: {score}')
    return score

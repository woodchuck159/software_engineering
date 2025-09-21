import os, time, hashlib
def process_data(data: str, verbosity: int) -> float:
    pid = os.getpid()
    if verbosity > 0: print(f'🚀 [Process ID: {pid}] Processing data: \'{data}\'')
    time.sleep(1)
    hash_object = hashlib.md5(data.encode())
    score = int(hash_object.hexdigest(), 16) % 1000 / 10.0
    if verbosity > 0: print(f'✅ [Process ID: {pid}] Finished processing. Score: {score}')
    return score

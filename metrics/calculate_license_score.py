import os
import time
import requests
import re
from typing import Tuple


def calculate_license_score(license_info: str, verbosity: int, log_queue) -> Tuple[float, float]:

    '''
    Calculates a score based on the license of a GitHub repository.
    Verbosity is controlled by the passed-in argument (0=silent, 1=INFO, 2=DEBUG).
    '''
    
    pid = os.getpid()
    
    # Score = 1 if license is LGPL-2.1. Score is 0 if any other license or no license 
    if verbosity >= 1: # Informational
        log_queue.put(f"[{pid}] [INFO] Starting license score calculation for {license_info}...")

    # latency time
    start_time = time.time()  

    try:
        ''''
        # GitHub API URL for repository metadata
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        if verbosity >= 1: # Informational
            log_queue.put(f"[{pid}] [INFO] Fetching repo metadata from: {url}")

        response = requests.get(url)

        # error check 
        if response.status_code != 200:
            raise Exception(f"GitHub API request failed with {response.status_code}")

        repo_data = response.json()

        # pull license info 
        license_info = repo_data.get("license") 
        '''

        if verbosity >= 1: # Informational
            if license_info:
                log_queue.put(f"[{pid}] [INFO] License info found: {license_info}")
            else:
                log_queue.put(f"[{pid}] [INFO] No license info found")

        
        # simple score if it has correct license then 1 if not then 0 
        if license_info in ["lgpl-2.1", "lgpl-lr", "lgpl", "lgpl-3.0", "gpl-3.0"]:
            score = 1.0
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] License matches LGPL-2.1 -> Score = 1.0")
        else:
            score = 0.0
            if verbosity >= 1: # Informational
                log_queue.put(f"[{pid}] [INFO] License does not match LGPL-2.1 -> Score = 0.0")

    except Exception as e:
        if verbosity >= 1: # Informational
            log_queue.put(f"[{pid}] [CRITICAL ERROR] calculating license score for '{license_info}': {e}")
        score = 0.0
    
    # end latency timer 
    time_taken = time.time() - start_time 
    if verbosity >= 1: # Informational
        log_queue.put(f"[{pid}] [INFO] Finished calculation. Score={score:.2f}, Time={time_taken:.3f}s")

    return score, time_taken


'''
# Example usage:
#fail 
repo_owner = "alecandrulis"
repo_name = "ece30861-team-8"
score, latency = calculate_license_score(repo_owner, repo_name)

print(f"License score for {repo_owner}/{repo_name}: {score:.2f}")
print(f"Latency: {latency:.3f} seconds")

#success 
repo_owner = "drowe67"
repo_name = "codec2"
score, latency = calculate_license_score(repo_owner, repo_name)
print(f"License score for {repo_owner}/{repo_name}: {score:.2f}")
print(f"Latency: {latency:.3f} seconds")
'''

'''
###testing only
if __name__ == "__main__":
    import queue

    # Create a log queue
    log_queue = queue.Queue()

    # Hard-coded test values
    test_licenses = ["LGPL-2.1", "MIT", "GPL-3.0", "lgpl-2.1", "lgpl-lr", "lgpl", "lgpl-3.0", "gpl-3.0", None]  # different test cases
    verbosity = 2  # 0=silent, 1=INFO, 2=DEBUG

    for lic in test_licenses:
        print(f"\nTesting license: {lic}")
        score, latency = calculate_license_score(lic, verbosity, log_queue)
        print(f"Score: {score}")
        print(f"Time taken: {latency:.3f}s")

        # Print log messages
        while not log_queue.empty():
            print(log_queue.get())
'''
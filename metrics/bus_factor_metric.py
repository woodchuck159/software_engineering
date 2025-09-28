import os
import time
import requests
from datetime import datetime, timedelta
from typing import Tuple

def bus_factor_metric(repo_owner: str, repo_name: str, verbosity: int, log_queue) -> Tuple[float, float]:
    """
    Calculate bus factor score based on number of contributors 
    within the last month for a Hugging Face repo hosted on GitHub.
    Verbosity is controlled by the passed-in argument (0=silent, 1=INFO, 2=DEBUG).
    """
    pid = os.getpid()
    start_time = time.time()
    
    if verbosity >= 1:
        log_queue.put(f"[{pid}] Starting bus factor calculation for '{repo_owner}/{repo_name}'...")

    try:
        # use url to find github pulls to see contributers (change this as need for intergration)
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls?state=all&per_page=100"
        
        if verbosity >= 2: # Debug
            log_queue.put(f"[{pid}] [INFO] Fetching pull requests from: {url}")

        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"GitHub API request failed with {response.status_code}")

        pull_requests = response.json()

        # set cutoff date to last 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        
        if verbosity >= 2: # Debug
            log_queue.put(f"[{pid}] [DEBUG] Contributor cutoff date set to {cutoff_date.strftime('%Y-%m-%d')}")

        # hold contributers 
        recent_contributors = set()
        all_contributors = set()

        # loop through all the pull requests 
        for pr in pull_requests:
            pr_date = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
            user = pr.get("user", {}).get("login")

            if user:
                # add all to all contributers
                all_contributors.add(user)
                
                if verbosity >= 2:
                    log_queue.put(f"[{pid}] [DEBUG] Found PR by {user} at {pr_date.strftime('%Y-%m-%d')}")

                # add only recent to recent
                if pr_date >= cutoff_date:
                    recent_contributors.add(user)

        num_contributors = len(all_contributors)
        
        if verbosity >= 1:
            log_queue.put(f"[{pid}] Found {len(recent_contributors)} recent contributors and {num_contributors} total contributors for '{repo_owner}/{repo_name}'.")


        # scoring system to match requirements 
        if len(recent_contributors) == 0:
            score = 0.0
        else:
            if num_contributors >= 10:
                score = 1.0
            else:
                score = 0.1 * num_contributors
    
    except Exception as e:
        log_queue.put(f"[{pid}] [CRITICAL ERROR] calculating bus factor for '{repo_owner}/{repo_name}': {e}")
        score = 0.0

    # end latency timer 
    time_taken = time.time() - start_time 

    if verbosity >= 1:
        log_queue.put(f"[{pid}] Bus factor calculation for '{repo_owner}/{repo_name}' complete. Score: {score:.2f}")

    # return final values 
    return score, time_taken

#testing with our repo:
'''
repo_owner = "alecandrulis"
repo_name = "ece30861-team-8"
score,latency = calculate_bus_factor(repo_owner, repo_name)

print(f"Bus factor score for {repo_owner}/{repo_name}: {score:.2f}")
print(f"Latency: {latency:.3f} seconds")
'''
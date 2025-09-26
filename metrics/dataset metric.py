import os
import time
import requests
from typing import Tuple

def dataset_metric(repo_owner: str, repo_name: str, github_token: str, verbosity: int, log_queue) -> Tuple[float, float]:
    """
    Calculates a score based on the presence of datasets and code in a GitHub repo.
    Verbosity is controlled by the passed-in argument (0=silent, 1=INFO, 2=DEBUG).
    """
    pid = os.getpid()
    start_time = time.perf_counter()
    score = 0.0  # Default score for any failure

    try:
        if verbosity >= 1: # Informational
            log_queue.put(f"[{pid}] [INFO] Starting dataset metric calculation for {repo_owner}/{repo_name}...")

        headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3.raw"
        }

        # Get the readme from the repo
        readme_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/readme"
        if verbosity >= 2: # Debug
            log_queue.put(f"[{pid}] [DEBUG] Fetching README from: {readme_url}")
        
        r = requests.get(readme_url, headers={"Accept": "application/vnd.github.v3.raw"})
        readme_text = r.text.lower() if r.status_code == 200 else ""

        # Check for these datasets (add more if needed)
        dataset_hosts = [
            "huggingface.co/datasets", "kaggle.com/datasets", 
            "roboflow.com", "drive.google.com"
        ]
        dataset_keywords = ["dataset", "datasets", "data", "training data", "download data"]

        has_dataset = any(host in readme_text for host in dataset_hosts) or \
                      any(kw in readme_text for kw in dataset_keywords)
        
        if verbosity >= 1: # Informational
            log_queue.put(f"[{pid}] [INFO] Dataset mention found: {has_dataset}")

        # Look for code in the repo
        has_code = False
        contents_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
        if verbosity >= 1: # Informational
            log_queue.put(f"[{pid}] [INFO] Fetching repo contents from root...")

        rc = requests.get(contents_url, headers=headers)

        if rc.status_code == 200:
            for item in rc.json():
                name = item.get("name", "").lower()

                # Python files in root
                if item["type"] == "file" and (name.endswith(".py") or name.endswith(".ipynb")):
                    has_code = True
                    if verbosity >= 2: log_queue.put(f"[{pid}] [DEBUG] Found code file in root: {name}")
                    break # Found code, no need to look further in root

                # Look for directories that would have code probably 
                if item["type"] == "dir" and name in ["examples", "notebooks", "tutorials", "research", "official", "src", "lib"]:
                    if verbosity >= 2: log_queue.put(f"[{pid}] [DEBUG] Checking common code directory: {name}")
                    subdir_url = item["url"]
                    sub_resp = requests.get(subdir_url, headers=headers)
                    if sub_resp.status_code == 200:
                        for sub_item in sub_resp.json():
                            sub_name = sub_item.get("name", "").lower()
                            if sub_item["type"] == "file" and (sub_name.endswith(".py") or sub_name.endswith(".ipynb")):
                                has_code = True
                                if verbosity >= 2: log_queue.put(f"[{pid}] [DEBUG] Found code file in '{name}': {sub_name}")
                                break # Exit inner loop
                    if has_code:
                        break # Exit outer loop
        
        if verbosity >= 1: # Informational
            log_queue.put(f"[{pid}] [INFO] Final check -> Has Dataset: {has_dataset}, Has Code: {has_code}")

        # Score based on results (NOT PERFECT)
        if has_dataset and has_code:
            score = 1.0
        elif has_dataset or has_code:
            score = 0.5
        else:
            score = 0.0

    except Exception as e:
        if verbosity >= 1: # Informational
            log_queue.put(f"[{pid}] [CRITICAL ERROR] calculating dataset metric for '{repo_owner}/{repo_name}': {e}")
        score = 0.0

    time_taken = time.perf_counter() - start_time

    if verbosity >= 1: # Informational
        log_queue.put(f"[{pid}] [INFO] Finished calculation. Score={score:.2f}, Time={time_taken:.3f}s")

    return score, time_taken


'''
### TESTING ONLY (note returns all zeros if you do not add api key)
repos_to_test = [
    ("huggingface", "transformers", 1.0),        # dataset + code
    ("huggingface", "datasets", 0.5),            # dataset mentions only
    ("pytorch", "examples", 0.5),                # example code only
    ("torvalds", "linux", 0.0),                  # neither
    ("apple", "swift", 0.0),                     # neither
    ("pandas-dev", "pandas", 0.5),               # code only
    ("ultralytics", "yolov5", 1.0),              # dataset links (Google Drive/Roboflow) + code
    ("facebookresearch", "fairseq", 0.5),        # code only
]

for owner, repo, expected in repos_to_test:
    score, latency = dataset_metric(owner, repo)
    print(f"{owner}/{repo} -> Score: {score} (expected {expected}), Latency: {latency} ms")
'''

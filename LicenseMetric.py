import requests
import time

def calculate_license_score(repo_owner, repo_name):
    
    # Score = 1 if license is LGPL-2.1. Score is 0 if any other license or no license 

    #latency timer
    start_time = time.time()  

    #GitHub API URL for repository metadata
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
    response = requests.get(url)

    #error check 
    if response.status_code != 200:
        raise Exception(f"GitHub API request failed with {response.status_code}")

    repo_data = response.json()

    #pull license info 
    license_info = repo_data.get("license") 

    #simple score if it has correct license then 1 if not then 0 
    if license_info and license_info.get("spdx_id") in ["LGPL-2.1", "LGPL-2.1-only", "LGPL-2.1-or-later"]:
        score = 1.0
    else:
        score = 0.0

    #end latency timer 
    latency = time.time() - start_time  

    return score, latency


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


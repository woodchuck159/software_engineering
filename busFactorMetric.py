import requests
import json 
import time
from datetime import datetime, timedelta

def calculate_bus_factor(repo_owner, repo_name):
    """
    Calculate bus factor score based on number of contributors 
    within the last month for a Hugging Face repo hosted on GitHub.
    """

    #latency timer 
    start_time = time.time()

    #use url to find github pulls to see contributers (change this as need for intergration)
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls?state=all&per_page=100"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"GitHub API request failed with {response.status_code}")

    pull_requests = response.json()

    #set cutoff date to last 30 days  
    cutoff_date = datetime.now() - timedelta(days=30)

    #hold contributers 
    recent_contributors = set()
    all_contributors = set()

    #loop through all the pull requests 
    for pr in pull_requests:
        pr_date = datetime.strptime(pr["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        user = pr.get("user", {}).get("login")

        if user:
            #add all to all contributers
            all_contributors.add(user)
            print(f"PR by {user} at {pr_date}") #testing 

            #add only recent to recent
            if pr_date >= cutoff_date:
                recent_contributors.add(user)

    num_contributors = len(all_contributors)

    #scoring system to match requirements 
    if len(recent_contributors) == 0:
        score = 0.0
    else:
        
        if num_contributors >= 10:
            score = 1.0
        else:
            score = 0.1 * num_contributors

    #end latency timer 
    latency = time.time() - start_time  

    #return final values 
    return score, latency

#testing with our repo:
repo_owner = "alecandrulis"
repo_name = "ece30861-team-8"
score,latency = calculate_bus_factor(repo_owner, repo_name)

print(f"Bus factor score for {repo_owner}/{repo_name}: {score:.2f}")
print(f"Latency: {latency:.3f} seconds")

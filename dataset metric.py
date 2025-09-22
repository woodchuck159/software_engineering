import requests
import time

def dataset_metric(repo_owner, repo_name):
    
    #latency timer 
    start = time.time()

    TOKEN = "TOKEN HERE"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3.raw"
    }

    #Get the readme from the repo
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/readme"
    r = requests.get(url, headers={"Accept": "application/vnd.github.v3.raw"})
    readme_text = r.text.lower() if r.status_code == 200 else ""

    #Check for these datasets (add more if needed)
    dataset_hosts = [
        "huggingface.co/datasets",
        "kaggle.com/datasets",
        "roboflow.com",
        "drive.google.com"
    ]

    dataset_keywords = ["dataset", "datasets", "data", "training data", "download data"]#add more to this if needed 

    has_dataset = any(host in readme_text for host in dataset_hosts) or \
                  any(kw in readme_text for kw in dataset_keywords)

    #Look for code in the repo anything with .py or .ipyng (should this include non python things?)
    has_code = False
    contents_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
    rc = requests.get(contents_url, headers=headers)

    if rc.status_code == 200:
        for item in rc.json():
            name = item.get("name", "").lower()

            #Python files in root
            if item["type"] == "file" and (name.endswith(".py") or name.endswith(".ipynb")):
                has_code = True

            #Look for directories that would have code probably 
            if item["type"] == "dir" and name in ["examples", "notebooks", "tutorials", "research", "official"]:
                subdir_url = item["url"]
                sub_resp = requests.get(subdir_url, headers=headers)
                if sub_resp.status_code == 200:
                    for sub_item in sub_resp.json():
                        sub_name = sub_item.get("name", "").lower()
                        if sub_name.endswith(".py") or sub_name.endswith(".ipynb"):
                            has_code = True

    #Score based on results (NOT PERFECT)
    if has_dataset and has_code:
        score = 1.0
    elif has_dataset or has_code:
        score = 0.5
    else:
        score = 0.0

    latency_ms = int((time.time() - start) * 1000)
    return score, latency_ms


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


import argparse
import sys
import subprocess
import url_class
import metric_caller
from collections import defaultdict
import time
from json_output import build_model_output
import os
from classes.github_api import GitHubApi
from get_model_metrics import get_model_size, get_model_README, get_model_license

import requests


def validate_github_token(token: str) -> bool:
    """Checks if a GitHub token is valid by making a simple API call."""
    if not token:
        return False
    headers = {"Authorization": f"token {token}"}
    response = requests.get("https://api.github.com/zen", headers=headers)
    return response.status_code == 200

def validate_log_file_path(path: str) -> bool:
    """Checks if the log file path is valid and the directory is writable."""
    if not path:
        return False
    try:
        dir_name = os.path.dirname(os.path.abspath(path))
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        if not os.access(dir_name, os.W_OK):
            return False
    except (OSError, IOError):
        return False
    return True


def main() -> int:
    start_time = time.time()




    log_level_str = os.getenv('LOG_LEVEL')
    log_file_path = os.getenv('LOG_FILE')
    github_token = os.getenv("GITHUB_TOKEN")
    gen_ai_key = os.getenv('GEN_AI_STUDIO_API_KEY') # Used by a child module

    


    GitHubApi.verify_token(github_token)
    
    if not log_level_str or not log_level_str.isdigit() or int(log_level_str) not in [0, 1, 2]:
        # print("ERROR: LOG_LEVEL environment variable not set or invalid. Must be 0, 1, or 2.", file=sys.stderr)
        sys.exit(1)
        
    if not log_file_path or not validate_log_file_path(log_file_path):
        # print(f"ERROR: LOG_FILE environment variable not set or path is unwritable: '{log_file_path}'", file=sys.stderr)
        sys.exit(1)
        
    if not github_token or not validate_github_token(github_token):
        # print("ERROR: GITHUB_TOKEN environment variable not set or is invalid.", file=sys.stderr)
        sys.exit(1)
        
    if not gen_ai_key:
        # print("ERROR: GEN_AI_STUDIO_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(
        prog="run",
        description="LLM Model Evaluator",
        add_help=False
    )

    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help="""usage: run [-v | --verbose] [-h | --help] { install, test } | URL_FILE\n
                        positional arguments:\n
                        \tinstall             Install any dependencies needed\n
                        \ttest                Runs testing suite\n
                        \tURL_FILE            Absolute file location of set of URLs\n
                        
                        options:\n
                        \t-h, --help          show this help message\n
                        \t-v. --verbose       enable verbose output\n""")
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='enable verbose output'
    )

    # install command
    parser.add_argument(
        "target",
        type=str,
        help="Choose 'install', 'test', or URL path."
    )

    args = parser.parse_args()


    # --- dispatch logic ---
    if args.target == "install":
        # if args.verbose:
        #     print("Verbose: Installing dependencies...")  
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"])

    elif args.target == "test":
        if args.verbose:
            print("Verbose: Running tests...")
        print("Running test suite...")

    else:
        #Running URL FILE
        project_groups: list[url_class.ProjectGroup] = url_class.parse_project_file(args.target)
        x = metric_caller.load_available_functions("metrics")
        for i in project_groups:
            
            size = get_model_size(i.model.namespace, i.model.repo, i.model.rev)
            filename = get_model_README(i.model.namespace, i.model.repo, i.model.rev)
            license = get_model_license(i.model.namespace, i.model.repo, i.model.rev)

            input_dict = {
                "repo_owner": i.model.namespace,
                "repo_name": i.model.repo,
                "verbosity": int(log_level_str),
                "log_queue": log_file_path,
                "model_size_bytes": size,
                "github_str": f"{i.code.link}",  # New parameter for GitHub repo
                "dataset_name": f"{i.dataset.repo}",  # New parameter for dataset name
                "filename" : filename,
                "license" : license
            }

            
            scores,latency = metric_caller.run_concurrently_from_file("./tasks.txt",input_dict,x,log_file_path)
            
            build_model_output(f"{i.model.repo}","model",scores,latency)
    
    return 0





if __name__ == "__main__":
    main()



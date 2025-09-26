import argparse
import sys
import subprocess
import url_class
import metric_caller
from collections import defaultdict
import metric_caller
import time
from json_output import build_model_output
import os





def main() -> int:

    time = time.time()

    verbosity = my_variable_value = os.getenv('LOG_LEVEL', None)
    log_file_location = os.getenv('LOG_FILE', None)
    gen_ai_key = os.getenv('GEN_AI_STUDIO_API_KEY', None)
    github_token = os.getenv("GITHUB_TOKEN",None)


    if (verbosity == None or log_file_location == None or gen_ai_key == None or github_token == None):
        return 1


    logfile = "LOG_FILE.txt"
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
        for i in project_groups:
            
            input_dict = {
                "repo_owner": i.model.namespace,
                "repo_name": i.model.repo,
                "filename": "WE NEED TO ADD FILEPATH TO README HERE",
                "verbosity": 1 if args.verbose else 0 ,
                "log_queue": logfile,
                "model_size_bytes": "WE NEED TO ADD MODEL SIZE HERE",
                "github_str": f"{i.code.link}",  # New parameter for GitHub repo
                "dataset_name": f"{i.dataset.namespace}",  # New parameter for dataset name
            }

            x = metric_caller.load_available_functions("./metrics")
            scores,latency = metric_caller.run_concurrently_from_file("./tasks.txt",input_dict,x,logfile)

            build_model_output(f"{i.code.namespace}","code",scores,latency)
            build_model_output(f"{i.dataset.namespace}","dataset",scores,latency)
            build_model_output(f"{i.model.namespace}/{i.model.repo}","model",scores,latency)
    
    return 0





if __name__ == "__main__":

    main()



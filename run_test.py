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
from get_model_metrics import get_model_metrics

if __name__ == '__main__':
    verbosity = 1
    logfile = "log.txt"
    verbosity = 1

    github_token = "no"
    os.environ['API_KEY'] = "no"


    #Running URL FILE
    project_groups: list[url_class.ProjectGroup] = url_class.parse_project_file("C:/Users/aleca/Documents/GitHub/ece30861-team-8/test.txt")
    for i in project_groups:

        #Get Model Metrics returns a dictionary with the following keys: namespace, repo, model_size_bytes
        model_metrics = get_model_metrics(i.model.namespace, i.model.repo)
        


        i.code.link = "https://github.com/alecandrulis/ece30861-team-8" 
        i.dataset.namespace = "imdb"
        i.model.namespace = "alecandrulis"
        i.model.repo = "ece30861-team-8"
        
        
        input_dict = {
            "repo_owner": i.model.namespace,
            "repo_name": i.model.repo,
            "readme": "readtest.txt",
            "verbosity": verbosity,
            "log_queue": logfile,
            "model_size_bytes": 1,
            "github_str": f"{i.code.link}",  # New parameter for GitHub repo
            "dataset_name": f"{i.dataset.namespace}",  # New parameter for dataset name
            "github_token" : github_token
        }

        x = metric_caller.load_available_functions("metrics")
        scores,latency = metric_caller.run_concurrently_from_file("./tasks.txt",input_dict,x,logfile)

        build_model_output(f"{i.code.namespace}","code",scores,latency)
        build_model_output(f"{i.dataset.namespace}","dataset",scores,latency)
        build_model_output(f"{i.model.namespace}/{i.model.repo}","model",scores,latency)


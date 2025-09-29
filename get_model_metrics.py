from typing import Dict, Any
from classes.hugging_face_api import HuggingFaceApi  # adjust import to where your class is saved

def get_model_size(namespace: str, repo: str, rev: str = "main") -> float:
    api = HuggingFaceApi(namespace, repo, rev)
    # api.set_bearer_token_from_file("token.ini")  # <-- load token here


    files_info = api.get_model_files_info()
    total_size: float= sum(f["size"] or 0 for f in files_info)

    return total_size

def get_model_README(namespace: str, repo: str, rev: str = "main") -> str:
    api = HuggingFaceApi(namespace, repo, rev)
                     
    ReadME_filepath = api.download_file("model_file_download", "README.md")

    return ReadME_filepath

def get_model_README(namespace: str, repo: str, rev: str = "main") -> str:
    api = HuggingFaceApi(namespace, repo, rev)
                     
    ReadME_filepath = api.download_file("model_file_download", "README.md")

    return ReadME_filepath


def get_model_license(namespace: str, repo: str, rev: str = "main") -> str:
    api = HuggingFaceApi(namespace, repo, rev)

    tags = api.get_model_info().get("tags", [])

    for t in tags:
        if t.startswith("license:"):
            return t.split("license:")[-1]                 
    return ""

if __name__ == "__main__":
    metrics = get_model_license("openai-community", "gpt2")
    print(metrics)
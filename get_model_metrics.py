from typing import Dict, Any
from classes.hugging_face_api import HuggingFaceApi  # adjust import to where your class is saved

def get_model_size(namespace: str, repo: str, rev: str = "main") -> float:
    api = HuggingFaceApi(namespace, repo, rev)
    api.set_bearer_token_from_file("token.ini")  # <-- load token here


    files_info = api.model_files_info()
    total_size: float= sum(f["size"] or 0 for f in files_info)

    return total_size


if __name__ == "__main__":
    metrics = get_model_size("openai-community", "gpt2")
    print(metrics)

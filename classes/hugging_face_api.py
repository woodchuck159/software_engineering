from .api import Api
import typing
import requests
import os
import tempfile
from typing import Optional
from typing import Union


class HuggingFaceApi(Api) :
    """
    A client for interacting with the Hugging Face API, providing methods to retrieve model and dataset information,
    list files, and download files from Hugging Face repositories.

    Constants:
    ----------
    BASE_URL (str): The base URL for the Hugging Face API.
    ENDPOINT (Dict[str, str]): Dictionary mapping endpoint names to their URL templates.

    Attributes:
    ----------
    namespace (str): The namespace (user or organization) of the Hugging Face repository.
    repo (str): The name of the model or dataset repository.
    rev (str): The revision (branch, tag, or commit) to use, defaults to "main".
    
    Methods:
    --------
    __init__(_namespace: str, _repo: str, _rev: str = "main"):
        Initializes the HuggingFaceApi instance with the given namespace, repo, and revision.
    set_bearer_token_from_file(filepath: str, section: str = "huggingface", key: str = "bearer_token"):
        Loads the bearer token from a configuration file for authentication.
    validate_model_fields() -> bool:
        Validates that the namespace, repo, and rev fields are set.
    build_endpoint(endpoint: str, path: str = "", filename: str = "") -> str:
        Constructs the API endpoint URL using the provided parameters.
    get_base_info(endpoint: str) -> dict[str, Any]:
        Retrieves base information from the specified endpoint.
    get_model_info(endpoint: str = "model_info") -> dict[str, Any]:
        Fetches metadata about the specified model repository.
    get_dataset_info(endpoint: str = "dataset_info") -> dict[str, Any]:
        Fetches metadata about the specified dataset repository.
    get_files_info(endpoint: str, path: str = "") -> list[dict[str, Any]]:
        Lists files in the specified model or dataset repository path.
    get_model_files_info(endpoint: str = "model_files", path: str = "") -> list[dict[str, Any]]:
        Lists files in the model repository.
    get_dataset_files_info(endpoint: str = "dataset_files", path: str = "") -> list[dict[str, Any]]:
        Lists files in the dataset repository.
    download_file(endpoint: str, filename: Union[str, list[str]], dest_dir: str = "tmp") -> Union[str, list[str]]:
        Downloads a file or list of files from the specified endpoint to the destination directory.
    download_model_file(filename: Union[str, list[str]], dest_dir: str = "tmp", endpoint: str = "model_file_download") -> Union[str, list[str]]:
        Downloads a model file or files from the model repository.
    download_dataset_file(filename: Union[str, list[str]], dest_dir: str = "tmp", endpoint: str = "dataset_file_download") -> Union[str, list[str]]:
        Downloads a dataset file or files from the dataset repository.
    """
    
    BASE_URL: str = "https://huggingface.co"
    ENDPOINT: typing.Dict[str, str] = {
        "model_info": "api/models/{namespace}/{repo}",
        "model_files": "api/models/{namespace}/{repo}/tree/{rev}/{path}",
        "model_file_download": "{namespace}/{repo}/resolve/{rev}/{filename}",
        "dataset_info": "api/dataset/{namespace}/{repo}",
        "dataset_files": "api/dataset/{namespace}/{repo}/tree/{rev}/{path}",
        "dataset_file_download": "{namespace}/{repo}/resolve/{rev}/{filename}",
        # Add more endpoints as needed
    }

    namespace: str
    repo: str
    rev: str

    def __init__(self, _namespace: str, _repo: str, _rev: str = "main"):
        super().__init__(self.BASE_URL)
        self.namespace = _namespace
        self.repo = _repo
        self.rev = _rev

# Tokens will be pulled from env var
    def set_bearer_token_from_file(self, filepath: str, section: str = "huggingface", key: str = "bearer_token"):
        super().set_bearer_token_from_file(filepath, section=section, key=key)


    def validate_model_fields(self) -> bool:
        if not self.namespace or not self.repo or not self.rev:
            raise Exception("Missing model information")
            return False
        return True

    def build_endpoint(self, endpoint: str, path: str = "", filename: str = "") -> str:
        endpoint_temp: Optional[str] = self.ENDPOINT.get(endpoint)
        if not endpoint_temp:
            raise ValueError(f"Invalid Endpoint: '{endpoint_temp}' ")
        api_endpoint: str = endpoint_temp.format(namespace=self.namespace, repo=self.repo, rev=self.rev, path=path, filename=filename)
        return api_endpoint

    def get_base_info(self, endpoint: str) -> dict[str, typing.Any] :
        # self.validate_model_fields()
        
        api_endpoint: str = self.build_endpoint(endpoint)
        return self.get(api_endpoint)

    def get_model_info(self, endpoint: str = "model_info") -> dict[str, typing.Any] :
        self.validate_model_fields()
        
        return self.get_base_info(endpoint)
    
    def get_dataset_info(self, endpoint: str = "dataset_info") -> dict[str, typing.Any] :
        
        return self.get_base_info(endpoint)
    

    def get_files_info(self, endpoint: str, path: str = "") -> list[dict[str, typing.Any]]:
        
        api_endpoint: str = self.build_endpoint(endpoint, path=path)

        response: list[dict[str, typing.Any]] = self.get(api_endpoint, payload={'recursive': 'True'})
        file_infos: list[dict[str, typing.Any]] = [
            {"path": item["path"], "size": item.get("size", None)}
            for item in response if item.get("type") == "file"
        ]
        return file_infos
    
    def get_model_files_info(self, endpoint:str = "model_files", path: str = "") -> list[dict[str, typing.Any]]:
        self.validate_model_fields()
        
        return self.get_files_info(endpoint, path)
    
    def get_dataset_files_info(self, endpoint:str = "dataset_files", path: str = "") -> list[dict[str, typing.Any]]:
        
        return self.get_files_info(endpoint, path)

    def download_file(self, endpoint: str, filename: Union[str, list[str]], dest_dir: str = "tmp") -> Union[str, list[str]]:
        file_path: str = ""
        endpoint_temp: Optional[str] = self.ENDPOINT.get(endpoint)
        if not endpoint_temp:
            raise ValueError(f"Invalid Endpoint: '{endpoint_temp}' ")
        
        if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir, exist_ok=True)

        if isinstance(filename, list):
            file_paths: list[str] = []
            for fname in filename:
                api_endpoint = self.build_endpoint(endpoint, filename=fname)
                content = str(self.get(api_endpoint))
                fname = fname.replace('/', '_')
                file_path = os.path.join(dest_dir, f"{self.repo}_{fname}")
                with open(file_path, "wb") as f:
                    f.write(content.encode())
                file_paths.append(file_path)
            return file_paths

        api_endpoint = self.build_endpoint(endpoint, filename=filename)
        content = self.get(api_endpoint)
        
        file_path: str = os.path.join(dest_dir, f"{self.repo}_{filename}.txt")
        with open(file_path, "wb") as f:
            f.write(content.encode())

        return file_path
    
    def download_model_file(self, filename: Union[str, list[str]], dest_dir: str = "tmp", endpoint: str = "model_file_download") -> Union[str, list[str]]:
        return self.download_file(endpoint, filename, dest_dir)
    
    def download_dataset_file(self, filename: Union[str, list[str]], dest_dir: str = "tmp", endpoint: str = "dataset_file_download") -> Union[str, list[str]]:
        return self.download_file(endpoint, filename, dest_dir)

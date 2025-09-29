from .api import Api
import typing
import requests
from os import getenv
from sys import exit
import configparser
from typing import Optional

class GitHubApi(Api) :
    """
    GitHubApi provides methods for interacting with the GitHub REST API.
    This class allows authentication, repository content retrieval, reading README files,
    and fetching pull requests for a given repository. It extends the base Api class
    to provide GitHub-specific endpoints and logic.

    Constants:
    ----------
    BASE_URL (str): The base URL for the GitHub API.
    ENDPOINT (Dict[str, str]): Dictionary mapping logical endpoint names to URL paths.

    Attributes:
    -----------
    owner (str): The owner of the repository.
    repo (str): The name of the repository.
    rev (str): The branch or revision (default: "main").

    Methods:
    --------
    __init__(owner, _repo, _rev="main", env_var=None):
        Initializes the GitHubApi instance with repository details.
    verify_token(github_token):
        Verifies the provided GitHub token by making an authenticated request.
    build_endpoint(endpoint, path="", filename=""):
        Constructs the API endpoint URL with provided parameters.
    set_bearer_token_from_env(var_name="GITHUB_TOKEN"):
        Sets the bearer token for authentication from an environment variable.
    get_repo_pulls(state="all", endpoint="pull_requests"):
        Retrieves pull requests for the repository with the specified state.
    
    # GitHubApi: Implements GitHub-specific API interactions.
    """


    BASE_URL: str = "https://api.github.com"
    ENDPOINT: typing.Dict[str, str] = {
        "verify_token": "/user",
        "repo_content": "/repose/{owner}/{repo}/contents/{path}",
        "readme": "/repos/{owner}/{repo}/readme",
        "pull_requests": "/repos/{owner}/{repo}/pulls"
        # Add more endpoints as needed
    }

    owner: str
    repo: str
    rev: str

    def __init__(self, owner: str, _repo: str, _rev: str = "main", env_var: Optional[str] = None):
        super().__init__(self.BASE_URL)
        self.owner = owner
        self.repo = _repo
        self.rev = _rev
            

    @staticmethod
    def verify_token(github_token: Optional[str]) :
        endpoint:str = GitHubApi.ENDPOINT['verify_token']
        url:str = GitHubApi.BASE_URL + endpoint
        if github_token is None:
            # log non-existant github token
            exit(1)

        headers: Optional[dict[str, typing.Any]] = {}
        headers["Authorization"] = f"Bearer {github_token}"

        resp: requests.Response = requests.get(
            url=url,
            headers=headers,
            timeout=Api._TIMEOUT
        )

        if resp.status_code == 401:
            # Invalid github token
            exit(1)
        
    def build_endpoint(self, endpoint: str, path: str = "", filename: str = "") -> str:
        endpoint_temp: Optional[str] = self.ENDPOINT.get(endpoint)
        if not endpoint_temp:
            raise ValueError(f"Invalid Endpoint: '{endpoint_temp}' ")
        api_endpoint: str = endpoint_temp.format(owner=self.owner, repo=self.repo, rev=self.rev, path=path, filename=filename)
        return api_endpoint

# Tokens will be pulled from env var
    def set_bearer_token_from_env(self, var_name:str = "GITHUB_TOKEN"):
        token: Optional[str] = getenv(var_name, None)
        self.verify_token(token)
        assert isinstance(token, str)

        super().set_bearer_token(token)



    def get_repo_pulls(self, state:str = "all", endpoint:str = "pull_requests"):
        url = self.build_endpoint(endpoint)
        payload = {"state": state}

        resp = self.get(url, payload=payload)
        return resp




from .api import Api
import typing
import requests
from os import getenv
from sys import exit
import configparser
from typing import Optional

class GitHubApi(Api) :
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




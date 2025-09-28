import requests
import configparser
import typing
from typing import TextIO
from typing import Optional


class Api :
    """
    A simple API client for making GET requests to a specified base URL.
    
    Attributes:
        base_url (str): The base URL for the API.
        bearer_token (str | None): Optional bearer token for authentication.
    """

    _TIMEOUT : float = 15.0

    def __init__(self, _base_url: str) :
        self.base_url = _base_url
        self.__bearer_token: Optional[str] = None

    @property
    def bearer_token(self) ->  Optional[str] :
        return self.__bearer_token


    def set_bearer_token(self, token: str) :
        self.__bearer_token = token

    def set_bearer_token_from_file(self, filepath: str, section: str = "auth", key: str = "bearer_token") :
        token: Optional[str] = None

        if filepath.endswith(".ini"):
            config: configparser.ConfigParser = configparser.ConfigParser()
            config.read(filepath)
            if config.has_section(section) and config.has_option(section, key):
                token = config.get(section, key)
        else:
            f: TextIO
            with open(filepath, "r") as f:
                token = f.read().strip()
        if not token:
            raise ValueError(f"Bearer token not found in file '{filepath}' (section: '{section}', key: '{key}')")
        self.set_bearer_token(token)
    
    
    def build_url(self, endpoint: str = "") -> str :
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"


    def get(self, endpoint: str = "", payload: Optional[dict[str, typing.Any]] = {}) -> typing.Any :
        url : str = self.build_url(endpoint)
        
        headers: Optional[dict[str, typing.Any]] = {}
        if self.__bearer_token:
            headers["Authorization"] = f"Bearer {self.__bearer_token}"

        resp: requests.Response = requests.get(
            url=url,
            params=payload,
            headers=headers,
            timeout=self._TIMEOUT
        )
        
        status_code: int = resp.status_code
        if status_code != 200 :
            raise Exception(f"GET request failed with status code {status_code} from {url}: {resp.text}")

        try:
            return resp.json()
        except requests.exceptions.JSONDecodeError:
            return resp.text

    def post(self, endpoint: str = "", payload: dict[str, str] = {}) -> dict[str, str] :
        url : str = self.build_url(endpoint)
        
        # <-- YOU WERE MISSING THIS SECTION IN post()
        headers: dict[str, str] = {}
        if self.__bearer_token:
            headers["Authorization"] = f"Bearer {self.__bearer_token}"
        # -->

        resp: requests.Response = requests.post(
            url=url,
            json=payload,
            headers=headers, # <-- AND YOU WERE MISSING THIS ARGUMENT
            timeout=self._TIMEOUT
        )
        
        status_code: int = resp.status_code
        if status_code != 200 :
            raise Exception(f"POST request failed with status code {status_code}: {resp.text}")

        return resp.json()




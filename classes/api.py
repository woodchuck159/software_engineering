import requests

class Api :
    """
    A simple API client for making GET requests to a specified base URL.
    
    Attributes:
        base_url (str): The base URL for the API.
        bearer_token (str | None): Optional bearer token for authentication.
    """

    _TIMEOUT : float = 5.0

    def __init__(self, _base_url: str) :
        self.base_url = _base_url
        self.__bearer_token: str | None = None

    @property
    def bearer_token(self) -> str | None :
        return self.__bearer_token


    def set_bearer_token(self, token: str) :
        self.__bearer_token = token

    
    def build_url(self, endpoint: str = "") -> str :
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

    def get(self, endpoint: str = "", payload: dict = {}) -> dict :
        url : str = self.build_url(endpoint)
        
        headers = {}
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
            raise Exception(f"GET request failed with status code {status_code}: {resp.text}")

        return resp.json()

    def post(self, endpoint: str = "", payload: dict = {}) -> dict :
        url : str = self.build_url(endpoint)
        
        # <-- YOU WERE MISSING THIS SECTION IN post()
        headers = {}
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




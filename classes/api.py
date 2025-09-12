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
        """
        Send a GET request to the API.

        Args:
            payload (dict, optional): Dictionary of query parameters to include in the request.

        Returns:
            dict: The JSON response from the API.

        Raises:
            Exception: If the request fails or returns a non-200 status code.
        """
        url : str = self.build_url(endpoint)

        resp: requests.Response = requests.get(
            url=url,
            data=payload,
            timeout=self._TIMEOUT
        )
        
        status_code: int = resp.status_code
        
        # This could probably use more explicit error handling
        if status_code != 200 :
            raise Exception(f"GET request failed with status code {status_code}")

        return resp.json()

    def post(self, endpoint: str = "", payload: dict = {}) -> dict :
        """
        Send a POST request to the API.

        Args:
            payload (dict, optional): Dictionary of data to include in the request body.

        Returns:
            dict: The JSON response from the API.

        Raises:
            Exception: If the request fails or returns a non-200 status code.
        """
        url : str = self.build_url(endpoint)

        resp: requests.Response = requests.post(
            url=url,
            json=payload,
            timeout=self._TIMEOUT
        )
        
        status_code: int = resp.status_code
        
        # This could probably use more explicit error handling
        if status_code != 200 :
            raise Exception(f"POST request failed with status code {status_code}")

        return resp.json()


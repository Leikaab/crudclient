from typing import Any, Dict, Optional


class ClientConfig:
    """
    Configuration class for Client.

    Attributes:
        base_url (str): The base URL of the API.
        api_key (Optional[str]): The API key for authentication.
        headers (Optional[Dict[str, str]]): Additional headers to include in every request.
        timeout (Optional[float]): Timeout for requests in seconds.
        retries (Optional[int]): Number of retries for failed requests.
    """

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = 10.0,
        retries: Optional[int] = 3,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.headers = headers or {}
        self.timeout = timeout
        self.retries = retries

    @property
    def auth(self) -> Dict[str, Any]:
        return {"Authorization": f"Bearer {self.api_key}"}

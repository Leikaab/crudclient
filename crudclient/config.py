from typing import Any, Dict, Optional
from urllib.parse import urljoin


class ClientConfig:
    """
    Configuration class for the Client.

    Attributes:
        hostname (Optional[str]): The hostname of the API.
        version (Optional[str]): The version of the API.
        api_key (Optional[str]): The API key to use for authentication.
        headers (Optional[Dict[str, str]]): Additional headers to include in the requests.
        timeout (Optional[float]): The timeout duration for requests.
        retries (Optional[int]): The number of retries to attempt for requests.

    Methods:
        base_url: Returns the base URL for the API.
        auth: Returns the authentication, standard is Bearer token. Overwrite this method if needed.
        __init__: Initializes the ClientConfig object with the provided values.
    """

    hostname: Optional[str] = None
    version: Optional[str] = None
    api_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    timeout: Optional[float] = 10.0
    retries: Optional[int] = 3

    @property
    def base_url(self) -> str:
        assert self.hostname, "Hostname is required!"
        return urljoin(self.hostname, self.version)

    def __init__(
        self,
        hostname: Optional[str] = None,
        version: Optional[str] = None,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
    ) -> None:
        self.hostname = hostname or self.hostname
        self.version = version or self.version
        self.api_key = api_key or self.api_key
        self.headers = headers or self.headers or {}
        self.timeout = timeout or self.timeout
        self.retries = retries or self.retries

    def auth(self) -> Dict[str, Any]:
        return {"Authorization": f"Bearer {self.api_key}"}

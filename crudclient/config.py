"""
Module `config.py`
==================

This module defines the ClientConfig class, which is used to configure the Client
for API interactions. It provides a flexible way to set up authentication, request
parameters, and other configuration options.

Classes:
    - ClientConfig: Configuration class for the Client.
"""

from typing import Any, Dict, Optional
from urllib.parse import urljoin


class ClientConfig:
    """
    Configuration class for the Client.

    This class holds the configuration parameters for API client interactions,
    including authentication details, request settings, and API endpoints.

    :ivar hostname: Optional[str] The hostname of the API.
    :ivar version: Optional[str] The version of the API.
    :ivar api_key: Optional[str] The API key to use for authentication.
    :ivar headers: Optional[Dict[str, str]] Additional headers to include in the requests.
    :ivar timeout: Optional[float] The timeout duration for requests.
    :ivar retries: Optional[int] The number of retries to attempt for requests.

    Methods:
        base_url: Returns the base URL for the API.
        auth: Returns the authentication header.
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
        """
        Constructs and returns the base URL for the API.

        :return: str The base URL for the API.
        :raises AssertionError: If the hostname is not set.
        """
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
        """
        Initializes the ClientConfig object with the provided values.

        :param hostname: Optional[str] The hostname of the API.
        :param version: Optional[str] The version of the API.
        :param api_key: Optional[str] The API key to use for authentication.
        :param headers: Optional[Dict[str, str]] Additional headers to include in the requests.
        :param timeout: Optional[float] The timeout duration for requests.
        :param retries: Optional[int] The number of retries to attempt for requests.
        :return: None
        """
        self.hostname = hostname or self.hostname
        self.version = version or self.version
        self.api_key = api_key or self.api_key
        self.headers = headers or self.headers or {}
        self.timeout = timeout or self.timeout
        self.retries = retries or self.retries

    def auth(self) -> Dict[str, Any]:
        """
        Returns the authentication header.

        By default, this method returns a Bearer token authentication header.
        Overwrite this method if a different authentication method is needed.

        :return: Dict[str, Any] The authentication header.
        """
        return {"Authorization": f"Bearer {self.api_key}"}

"""
Module `config.py`
==================

Defines the `ClientConfig` base class used for configuring API clients.

This module provides a reusable configuration system for HTTP API clients,
including support for custom base URLs, authentication strategies, request headers,
timeouts, and retry behavior. The configuration is structured using a dataclass
to ensure clarity, type safety, and extensibility.

Features:
    - Bearer, Basic, or no authentication support
    - Customizable headers, timeouts, and retry policy
    - Extensible via subclassing for token refresh or session logic
    - Supports dynamic token injection and pre-request preparation hooks

Classes:
    - ClientConfig: Base configuration class for API clients.
"""

from typing import Any, Dict, Literal, Optional
from urllib.parse import urljoin


class ClientConfig:
    """
    Generic configuration class for API clients.

    Provides common settings for hostname, versioning, headers, authentication,
    retry behavior, and request timeouts. Designed for use across different APIs.

    Attributes:
        hostname (Optional[str]): Base hostname of the API (e.g., "https://api.example.com").
        version (Optional[str]): API version to be appended to the base URL (e.g., "v1").
        api_key (Optional[str]): Credential used for authentication (token or raw credential).
        headers (Dict[str, str]): Optional default headers to include in all requests.
        timeout (float): Timeout in seconds for each request (default: 10.0).
        retries (int): Number of retry attempts for failed requests (default: 3).
        auth_type (Literal["bearer", "basic", "none"]): Authentication strategy used to format the auth header.
    """

    hostname: Optional[str] = None
    version: Optional[str] = None
    api_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    timeout: float = 10.0
    retries: int = 3
    auth_type: Literal["bearer", "basic", "none"] = "bearer"

    def __init__(
        self,
        hostname: Optional[str] = None,
        version: Optional[str] = None,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        auth_type: Optional[Literal["bearer", "basic", "none"]] = None,
    ) -> None:
        self.hostname = hostname or self.__class__.hostname
        self.version = version or self.__class__.version
        self.api_key = api_key or self.__class__.api_key
        self.headers = headers or self.__class__.headers or {}
        self.timeout = timeout if timeout is not None else self.__class__.timeout
        self.retries = retries if retries is not None else self.__class__.retries
        self.auth_type = auth_type or self.__class__.auth_type

    @property
    def base_url(self) -> str:
        """
        Returns the full base URL by joining hostname and version.

        Raises:
            ValueError: If hostname is not set.

        Returns:
            str: Complete base URL to use in requests.
        """
        if not self.hostname:
            raise ValueError("hostname is required")
        return urljoin(self.hostname, self.version or "")

    def get_auth_token(self) -> Optional[str]:
        """
        Returns the raw authentication token or credential.

        Override in subclasses to implement custom token logic (e.g. refreshable tokens).

        Returns:
            Optional[str]: Raw token or credential string.
        """
        return self.api_key

    def get_auth_header_name(self) -> str:
        """
        Returns the name of the header used for authentication.

        Override to change the default "Authorization" header (e.g. "X-API-Key").

        Returns:
            str: Header key for authentication.
        """
        return "Authorization"

    def prepare(self) -> None:
        """
        Hook for any pre-request setup logic.

        Override to implement token refresh, credential rotation, or pre-fetch logic.
        This method is intended to be called once before executing a request.
        """

    def auth(self) -> Dict[str, Any]:
        """
        Builds and returns the authentication header dictionary.

        Behavior is controlled by the `auth_type` field:
            - "bearer":     Returns "Authorization: Bearer <token>"
            - "basic":      Returns "Authorization: Basic <token>"
            - "none":       Returns an empty dict
            - other/custom: Returns "Authorization: <raw token>"

        Returns:
            Dict[str, Any]: Dictionary of headers to include for authentication.
        """
        token = self.get_auth_token()
        if not token or self.auth_type == "none":
            return {}

        header_name = self.get_auth_header_name()

        if self.auth_type == "basic":
            return {header_name: f"Basic {token}"}
        elif self.auth_type == "bearer":
            return {header_name: f"Bearer {token}"}
        else:
            return {header_name: token}

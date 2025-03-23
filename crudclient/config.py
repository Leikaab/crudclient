"""
Module `config.py`
==================

Defines the `ClientConfig` base class used for configuring API clients.

This module provides a reusable configuration system for HTTP API clients,
including support for base URLs, authentication strategies, headers, timeouts,
and retry logic. Designed for subclassing and reuse across multiple APIs.

Features:
    - Support for Bearer, Basic, or no authentication
    - Automatic generation of authentication headers
    - Pre-request initialization and hook support
    - Extensible retry logic, including 403-retry fallback for session-based APIs

Classes:
    - ClientConfig: Base configuration class for API clients.
"""

from typing import Any, Dict, Literal, Optional
from urllib.parse import urljoin


class ClientConfig:
    """
    Generic configuration class for API clients.

    Provides common settings for hostname, versioning, authentication,
    retry behavior, and request timeouts. Designed to be subclassed
    for specific APIs that require token refresh, session handling, or
    additional logic.

    Attributes:
        hostname (Optional[str]): Base hostname of the API (e.g., "https://api.example.com").
        version (Optional[str]): API version to be appended to the base URL (e.g., "v1").
        api_key (Optional[str]): Credential or token used for authentication.
        headers (Dict[str, str]): Optional default headers for every request.
        timeout (float): Timeout for each request in seconds (default: 10.0).
        retries (int): Number of retry attempts for failed requests (default: 3).
        auth_type (Literal["bearer", "basic", "none"]): Authentication scheme.
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

        Override this in subclasses to implement dynamic or refreshable tokens.

        Returns:
            Optional[str]: Token or credential used for authentication.
        """
        return self.api_key

    def get_auth_header_name(self) -> str:
        """
        Returns the name of the HTTP header used for authentication.

        Override if the API uses non-standard auth headers.

        Returns:
            str: Name of the header (default: "Authorization").
        """
        return "Authorization"

    def prepare(self) -> None:
        """
        Hook for pre-request setup logic.

        Override in subclasses to implement setup steps such as refreshing tokens,
        validating credentials, or preparing session context.

        This method is called once at client startup.
        """

    def auth(self) -> Dict[str, Any]:
        """
        Builds the authentication headers to use in requests.

        Behavior depends on `auth_type`:
            - "bearer": Returns {'Authorization': 'Bearer <token>'}
            - "basic": Returns {'Authorization': 'Basic <token>'}
            - "none": Returns {}
            - other/custom: Returns {'Authorization': <token>}

        Returns:
            Dict[str, Any]: Headers to include in requests.
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

    def should_retry_on_403(self) -> bool:
        """
        Indicates whether the client should retry once after a 403 Forbidden response.

        Override in subclasses to enable fallback retry logic, typically used in APIs
        where sessions or tokens may expire and require refresh.

        Returns:
            bool: True to enable 403 retry, False by default.
        """
        return False

    def handle_403_retry(self, client) -> None:
        """
        Hook to handle 403 response fallback logic (e.g. token/session refresh).

        Called once when a 403 response is received and `should_retry_on_403()` returns True.
        The method may update headers, refresh tokens, or mutate session state.

        Args:
            client: Reference to the API client instance making the request.
        """

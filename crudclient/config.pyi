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
from crudclient.auth.base import AuthStrategy

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
        auth (Optional[AuthStrategy]): Authentication strategy to use.

    Methods:
        __init__: Initializes a configuration object with specified parameters.
        __add__: Combines two configurations into a new instance with merged attributes.
        base_url: Property that returns the complete base URL for API requests.
        get_auth_token: Returns the authentication token used for authorization.
        get_auth_header_name: Returns the header name used for authentication.
        get_auth_headers: Builds authentication headers using the configured AuthStrategy.
        prepare: Hook for pre-request setup logic like refreshing tokens.
        should_retry_on_403: Indicates whether to retry after a 403 response.
        handle_403_retry: Hook for handling retry logic after 403 responses.
    """

    hostname: Optional[str]
    version: Optional[str]
    api_key: Optional[str]
    headers: Optional[Dict[str, str]]
    timeout: float
    retries: int
    auth_strategy: Optional["AuthStrategy"]
    auth_type: str
    log_request_body: bool
    log_response_body: bool

    def __init__(
        self,
        hostname: Optional[str] = ...,
        version: Optional[str] = ...,
        api_key: Optional[str] = ...,
        headers: Optional[Dict[str, str]] = ...,
        timeout: Optional[float] = ...,
        retries: Optional[int] = ...,
        auth_strategy: Optional[AuthStrategy] = ...,
        auth_type: Optional[str] = ...,
        log_request_body: Optional[bool] = ...,
        log_response_body: Optional[bool] = ...,
    ) -> None: ...
    def merge(self, other: "ClientConfig") -> "ClientConfig":
        """
        Merges two configuration objects, creating a new instance.

        Creates a deep copy of 'other' and selectively updates it with attributes
        from 'self' that don't exist in 'other'. Headers are specially handled
        by merging the two dictionaries, with 'other' values taking precedence.

        This method allows for configuration composition without modifying
        the original instances.

        Args:
            other (ClientConfig): The configuration to combine with.
                Attributes from 'other' take precedence over 'self'.

        Returns:
            ClientConfig: A new configuration instance with combined attributes.

        Example:
            base_config = ClientConfig(hostname="https://api.example.com")
            custom_config = ClientConfig(timeout=30.0)
            combined = base_config.merge(custom_config)  # hostname from base, timeout from custom
        """
        ...

    def __add__(self, other: "ClientConfig") -> "ClientConfig":
        """
        Combines two configuration objects, creating a new instance.

        This method is deprecated. Use `merge()` instead.

        Creates a deep copy of 'other' and selectively updates it with attributes
        from 'self' that don't exist in 'other'. Headers are specially handled
        by merging the two dictionaries, with 'other' values taking precedence.

        This method allows for configuration composition without modifying
        the original instances.

        Args:
            other (ClientConfig): The configuration to combine with.
                Attributes from 'other' take precedence over 'self'.

        Returns:
            ClientConfig: A new configuration instance with combined attributes.

        Example:
            base_config = ClientConfig(hostname="https://api.example.com")
            custom_config = ClientConfig(timeout=30.0)
            combined = base_config + custom_config  # hostname from base, timeout from custom
        """
        ...

    @staticmethod
    def merge_configs(base_config: "ClientConfig", other_config: "ClientConfig") -> "ClientConfig":
        """
        Static method to merge two configuration objects without requiring an instance.

        Creates a new instance by merging attributes from both configurations.
        Attributes from 'other_config' take precedence over 'base_config'.
        Headers are specially handled by merging the two dictionaries.

        Args:
            base_config (ClientConfig): The base configuration.
            other_config (ClientConfig): The configuration to merge with base.
                Attributes from 'other_config' take precedence.

        Returns:
            ClientConfig: A new configuration instance with combined attributes.

        Example:
            base_config = ClientConfig(hostname="https://api.example.com")
            custom_config = ClientConfig(timeout=30.0)
            combined = ClientConfig.merge_configs(base_config, custom_config)
        """
        ...

    @property
    def base_url(self) -> str:
        """
        Returns the full base URL by joining hostname and version.

        Raises:
            ValueError: If hostname is not set.

        Returns:
            str: Complete base URL to use in requests.
        """
        ...

    def get_auth_token(self) -> Optional[str]:
        """
        Returns the raw authentication token or credential.

        Override this in subclasses to implement dynamic or refreshable tokens.

        Returns:
            Optional[str]: Token or credential used for authentication.
        """
        ...

    def get_auth_header_name(self) -> str:
        """
        Returns the name of the HTTP header used for authentication.

        Override if the API uses non-standard auth headers.

        Returns:
            str: Name of the header (default: "Authorization").
        """
        ...

    def get_auth_headers(self) -> Dict[str, Any]:
        """
        Builds the authentication headers to use in requests.

        If an AuthStrategy is set, uses it to prepare request headers.
        Otherwise, returns an empty dictionary.

        Returns:
            Dict[str, str]: Headers to include in requests.
        """
        ...

    def auth(self) -> Dict[str, Any]:
        """
        Legacy method for backward compatibility.

        Returns authentication headers based on the auth_type and token.
        New code should use the AuthStrategy pattern instead.
        """
        ...

    def prepare(self) -> None:
        """
        Hook for pre-request setup logic.

        Override in subclasses to implement setup steps such as refreshing tokens,
        validating credentials, or preparing session context.

        This method is called once at client startup.
        """
        ...

    def should_retry_on_403(self) -> bool:
        """
        Indicates whether the client should retry once after a 403 Forbidden response.

        Override in subclasses to enable fallback retry logic, typically used in APIs
        where sessions or tokens may expire and require refresh.

        Returns:
            bool: True to enable 403 retry, False by default.
        """
        ...

    def handle_403_retry(self, client: Any) -> None:
        """
        Hook to handle 403 response fallback logic (e.g. token/session refresh).

        Called once when a 403 response is received and `should_retry_on_403()` returns True.
        The method may update headers, refresh tokens, or mutate session state.

        Args:
            client: Reference to the API client instance making the request.

        Returns:
            None: This method doesn't return any value.
        """
        ...

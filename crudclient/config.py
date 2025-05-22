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

import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from crudclient.auth.base import AuthStrategy

# Set up logging
logger = logging.getLogger(__name__)


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
    """

    hostname: Optional[str] = None
    version: Optional[str] = None
    api_key: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    timeout: float = 10.0
    retries: int = 3
    auth_strategy: Optional[AuthStrategy] = None
    auth_type: str = "bearer"  # For backward compatibility
    log_request_body: bool = False
    log_response_body: bool = False

    def __init__(
        self,
        hostname: Optional[str] = None,
        version: Optional[str] = None,
        api_key: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        retries: Optional[int] = None,
        auth_strategy: Optional[AuthStrategy] = None,
        auth_type: Optional[str] = None,
        log_request_body: Optional[bool] = None,
        log_response_body: Optional[bool] = None,
    ) -> None:
        """
        Initializes a configuration object with specified parameters.
        """
        self.hostname = hostname or self.__class__.hostname
        self.version = version or self.__class__.version
        self.api_key = api_key or self.__class__.api_key
        self.headers = headers or self.__class__.headers or {}
        self.timeout = timeout if timeout is not None else self.__class__.timeout
        self.retries = retries if retries is not None else self.__class__.retries
        self.auth_strategy = auth_strategy or self.__class__.auth_strategy
        self.auth_type = auth_type or self.__class__.auth_type
        self.log_request_body = log_request_body if log_request_body is not None else self.__class__.log_request_body
        self.log_response_body = log_response_body if log_response_body is not None else self.__class__.log_response_body

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
            logger.error("Hostname is required")
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

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Builds the authentication headers to use in requests.

        If an AuthStrategy is set, uses it to prepare request headers.
        Otherwise, returns an empty dictionary.

        Returns:
            Dict[str, str]: Headers to include in requests.
        """
        if self.auth_strategy:
            return self.auth_strategy.prepare_request_headers()
        return {}

    def auth(self) -> Dict[str, str]:
        """
        Legacy method for backward compatibility.

        Returns authentication headers based on the auth_type and token.
        New code should use the AuthStrategy pattern instead.
        """
        # If we have an AuthStrategy, use it
        if isinstance(self.auth_strategy, AuthStrategy):
            return self.get_auth_headers()

        # Otherwise, fall back to the old behavior for backward compatibility
        token = self.get_auth_token()
        if not token:
            return {}

        header_name = self.get_auth_header_name()

        # Determine auth type from class attributes if available
        auth_type = getattr(self, "auth_type", "bearer") if hasattr(self, "auth_type") else "bearer"

        if auth_type == "basic":
            return {header_name: f"Basic {token}"}
        elif auth_type == "bearer":
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
        return None

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
        if not isinstance(other, self.__class__):
            return NotImplemented  # type: ignore

        import copy

        # Create a deep copy of self as the base for the new instance
        new_instance = copy.deepcopy(self)

        # Special handling for headers - merge them with other's headers taking precedence
        if hasattr(other, "headers") and other.headers:
            new_headers = copy.deepcopy(new_instance.headers or {})
            new_headers.update(other.headers)
            new_instance.headers = new_headers

        # Copy all other attributes from other, overriding self's values
        for key, value in other.__dict__.items():
            if key != "headers" and value is not None:
                setattr(new_instance, key, copy.deepcopy(value))

        return new_instance

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
        import warnings

        warnings.warn("The __add__ method is deprecated. Use merge() instead.", DeprecationWarning, stacklevel=2)
        return self.merge(other)

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
        if not isinstance(base_config, ClientConfig) or not isinstance(other_config, ClientConfig):
            raise TypeError("Both arguments must be instances of ClientConfig")

        return base_config.merge(other_config)

"""
Module `config.py`
==================

Defines the `ClientConfig` base class used for configuring API clients.

This module provides a configuration system for HTTP API clients built on top
of apiconfig's ClientConfig, adding crudclient-specific functionality while
preserving the declarative Django REST Framework feel.

Classes:
    - ClientConfig: Configuration class for crudclient API clients.
"""

import logging
from typing import Any, Dict, Optional

from apiconfig.config.base import ClientConfig as _ApiConfigClientConfig
from apiconfig.exceptions.config import MissingConfigError

# Import AuthStrategy from crudclient for type hints
from crudclient.auth import AuthStrategy

# Set up logging
logger = logging.getLogger(__name__)


class ClientConfig(_ApiConfigClientConfig):
    """
    Configuration class for crudclient API clients.

    Extends apiconfig's ClientConfig with crudclient-specific functionality
    including 403 retry hooks and legacy authentication support.

    Attributes:
        All attributes from apiconfig.config.base.ClientConfig plus:
        api_key (Optional[str]): Legacy credential for authentication.
        auth_type (str): Legacy auth type ("bearer", "basic", etc).
    """

    # Legacy attributes for backward compatibility
    api_key: Optional[str] = None
    auth_type: str = "bearer"

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
        Initialize configuration with crudclient-specific extensions.

        Args:
            hostname: Base hostname of the API
            version: API version string
            api_key: Legacy authentication credential
            headers: Default headers for requests
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            auth_strategy: Authentication strategy instance
            auth_type: Legacy auth type (default: "bearer")
            log_request_body: Flag to enable request body logging
            log_response_body: Flag to enable response body logging
        """
        # Call parent constructor
        super().__init__(
            hostname=hostname,
            version=version,
            headers=headers,
            timeout=timeout,
            retries=retries,
            auth_strategy=auth_strategy,
            log_request_body=log_request_body,
            log_response_body=log_response_body,
        )

        # Set legacy attributes
        self.api_key = api_key or self.__class__.api_key
        self.auth_type = auth_type or self.__class__.auth_type

    @property
    def base_url(self) -> str:
        """
        Override to maintain crudclient's ValueError for backward compatibility.

        This is a trivial change to keep the same exception type.
        """
        try:
            return super().base_url
        except MissingConfigError as e:
            # Convert to ValueError for backward compatibility
            logger.error("Hostname is required")
            raise ValueError("hostname is required") from e

    def get_auth_token(self) -> Optional[str]:
        """
        Returns the raw authentication token or credential.

        Returns:
            Optional[str]: Token or credential used for authentication.
        """
        return self.api_key

    def get_auth_header_name(self) -> str:
        """
        Returns the name of the HTTP header used for authentication.

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

    def handle_403_retry(self, client: Any) -> None:
        """
        Hook to handle 403 response fallback logic (e.g. token/session refresh).

        Called once when a 403 response is received and `should_retry_on_403()` returns True.
        The method may update headers, refresh tokens, or mutate session state.

        Args:
            client: Reference to the API client instance making the request.
        """

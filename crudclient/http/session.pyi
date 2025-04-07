"""
Stub file for `session.py`
=========================

This file provides type hints and method signatures for the `session.py` module.
It is used to provide better type checking and autocompletion support.
"""

from typing import Any, Dict, Optional

import requests

from ..config import ClientConfig
from ..auth.base import AuthStrategy


class SessionManager:
    """
    Manages HTTP sessions and their lifecycle.

    This class is responsible for creating, configuring, and cleaning up HTTP sessions.
    It handles authentication, retries, timeouts, and other session parameters.

    Attributes:
        config (ClientConfig): Configuration object for the session.
        session (requests.Session): The HTTP session managed by this instance.
        timeout (float): The timeout for requests in seconds.
    """

    config: ClientConfig
    session: requests.Session
    timeout: float

    def __init__(self, config: ClientConfig) -> None:
        """
        Initialize the SessionManager with a configuration.

        Args:
            config (ClientConfig): Configuration for the session.

        Raises:
            TypeError: If the provided config is not a ClientConfig object.
        """
        ...

    def _setup_auth(self) -> None:
        """
        Set up authentication for the requests session.

        This method configures the session with the appropriate authentication headers
        based on the authentication strategy defined in the config.

        It first tries to use the new auth strategy approach, and if that's not available,
        falls back to the old auth method for backward compatibility.
        """
        ...

    def _setup_retries_and_timeouts(self) -> None:
        """
        Set up retries and timeouts for the requests session.

        This method configures the session with the appropriate retry and timeout settings
        based on the configuration. It creates an HTTPAdapter with the specified number of
        retries and mounts it to both 'http://' and 'https://' URLs in the session.

        It also sets the timeout duration for the session.
        """
        ...

    def update_headers(self, headers: Dict[str, str]) -> None:
        """
        Update the session headers with the provided headers.

        Args:
            headers (Dict[str, str]): Headers to add to the session.

        Raises:
            TypeError: If headers is not a dictionary.
        """
        ...

    def set_content_type(self, content_type: str) -> None:
        """
        Set the Content-Type header for the session.

        Args:
            content_type (str): The content type to set.

        Raises:
            TypeError: If content_type is not a string.
        """
        ...

    def refresh_auth(self) -> None:
        """
        Refresh the authentication for the session.

        This method can be called when authentication needs to be refreshed,
        such as after a token expires.
        """
        ...

    def close(self) -> None:
        """
        Close the HTTP session and clean up resources.

        This method should be called when the session is no longer needed
        to ensure proper cleanup of resources.
        """
        ...

import logging
from typing import Dict

import requests
from requests.adapters import HTTPAdapter

from ..auth.base import AuthStrategy
from ..config import ClientConfig

# Set up logging
logger = logging.getLogger(__name__)


class SessionManager:

    def __init__(self, config: ClientConfig) -> None:
        if not isinstance(config, ClientConfig):
            raise TypeError("config must be a ClientConfig object")

        self.config: ClientConfig = config
        self.session = requests.Session()
        self.is_closed = False

        # Set up authentication
        self._setup_auth()

        # Set up default headers, if any
        if self.config.headers:
            self.session.headers.update(self.config.headers)

        # Set up retries and timeouts
        self._setup_retries_and_timeouts()

    def _setup_auth(self) -> None:
        self.config.prepare()

        # Try the new auth strategy first
        if hasattr(self.config, "auth_strategy") and isinstance(self.config.auth_strategy, AuthStrategy):
            logger.debug("Applying authentication using %s", type(self.config.auth_strategy).__name__)
            auth_headers = self.config.get_auth_headers()
            if auth_headers:
                self.session.headers.update(auth_headers)
            return

        # Fall back to the old auth method for backward compatibility
        # This handles the case where auth() is overridden in a subclass
        # Check if the config class has an auth method (old style)
        if hasattr(self.config, "auth") and callable(getattr(self.config, "auth")):
            auth = self.config.auth()
            if auth is not None:
                if isinstance(auth, dict):
                    logger.debug("Applying authentication via direct header dictionary")
                    self.session.headers.update(auth)
                elif isinstance(auth, tuple) and len(auth) == 2:
                    logger.debug("Applying authentication via session.auth tuple")
                    self.session.auth = auth
                elif callable(auth):
                    logger.debug("Applying authentication via callable: %s", type(auth).__name__)
                    auth(self.session)

    def _setup_retries_and_timeouts(self) -> None:
        retries = self.config.retries or 3
        timeout = self.config.timeout or 5

        adapter = HTTPAdapter(max_retries=retries)

        # Mount the adapter to both 'http://' and 'https://' URLs in the session
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set the timeout duration for the session
        self.timeout = timeout

    def update_headers(self, headers: Dict[str, str]) -> None:
        # Runtime type check
        if not isinstance(headers, dict):
            raise TypeError(f"headers must be a dictionary, got {type(headers).__name__}")
        if headers:
            self.session.headers.update(headers)

    def set_content_type(self, content_type: str) -> None:
        # Runtime type check
        if not isinstance(content_type, str):
            raise TypeError(f"content_type must be a string, got {type(content_type).__name__}")
        self.session.headers["Content-Type"] = content_type

    def refresh_auth(self) -> None:
        self._setup_auth()

    def close(self) -> None:
        self.session.close()
        self.is_closed = True
        logger.debug("Session closed.")

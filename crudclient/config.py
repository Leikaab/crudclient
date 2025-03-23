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

from typing import Any, Dict, Optional
from urllib.parse import urljoin


class ClientConfig:
    hostname = None
    version = None
    api_key = None
    headers = None
    timeout = 10.0
    retries = 3
    auth_type = "bearer"

    def __init__(
        self,
        hostname=None,
        version=None,
        api_key=None,
        headers=None,
        timeout=None,
        retries=None,
        auth_type=None,
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
        if not self.hostname:
            raise ValueError("hostname is required")
        return urljoin(self.hostname, self.version or "")

    def get_auth_token(self) -> Optional[str]:
        return self.api_key

    def get_auth_header_name(self) -> str:
        return "Authorization"

    def prepare(self) -> None:
        pass

    def auth(self) -> Dict[str, Any]:
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
        return False

    def handle_403_retry(self, client) -> None:
        pass

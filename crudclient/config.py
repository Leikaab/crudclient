import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

from crudclient.auth.base import AuthStrategy

# Set up logging
logger = logging.getLogger(__name__)


class ClientConfig:
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
        if not self.hostname:
            logger.error("Hostname is required")
            raise ValueError("hostname is required")
        return urljoin(self.hostname, self.version or "")

    def get_auth_token(self) -> Optional[str]:
        return self.api_key

    def get_auth_header_name(self) -> str:
        return "Authorization"

    def prepare(self) -> None:
        pass

    def get_auth_headers(self) -> Dict[str, str]:
        if self.auth_strategy:
            return self.auth_strategy.prepare_request_headers()
        return {}

    def auth(self) -> Dict[str, str]:
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
        return False

    def handle_403_retry(self, client: Any) -> None:
        return None

    def merge(self, other: "ClientConfig") -> "ClientConfig":
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
        import warnings

        warnings.warn("The __add__ method is deprecated. Use merge() instead.", DeprecationWarning, stacklevel=2)
        return self.merge(other)

    @staticmethod
    def merge_configs(base_config: "ClientConfig", other_config: "ClientConfig") -> "ClientConfig":
        if not isinstance(base_config, ClientConfig) or not isinstance(other_config, ClientConfig):
            raise TypeError("Both arguments must be instances of ClientConfig")

        return base_config.merge(other_config)

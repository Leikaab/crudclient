import logging
from typing import Any, Dict, Optional, Union

import requests

from ..config import ClientConfig

class HttpLifecycleLogger:
    """Handles logging for the HTTP request/response lifecycle."""

    config: ClientConfig
    logger: logging.Logger

    def __init__(self, config: ClientConfig, logger: logging.Logger) -> None: ...
    def log_request_body_content(self, kwargs: Dict[str, Any]) -> None:
        """Logs the content of the request body, redacting if necessary."""
        ...

    def log_response_body_content(self, response: requests.Response) -> None:
        """Logs the content of the response body, redacting if necessary."""
        ...

    def log_response_details(self, method: str, url: str, response: requests.Response) -> None:
        """Logs details about the received HTTP response."""
        ...

    def log_request_details(self, method: str, url: str, kwargs: Dict[str, Any]) -> None:
        """Logs details about the outgoing HTTP request."""
        ...

    def log_request_completion(
        self,
        start_time: float,
        method: str,
        url: str,
        attempt_count: int,
        final_outcome: Union[requests.Response, Exception, None],
    ) -> None:
        """Logs the final outcome and duration of an HTTP request."""
        ...

    def log_http_error(
        self,
        e: requests.exceptions.HTTPError,
        method: Optional[str] = ...,
        url: Optional[str] = ...,
    ) -> None:
        """Logs details about an HTTPError."""
        ...

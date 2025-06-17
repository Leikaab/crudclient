"""HTTP logging helpers for ``crudclient``.

This module exposes a ``setup_http_logging`` convenience function and a very
lightweight ``HttpLifecycleLogger`` that delegates redaction and formatting to
``apiconfig.utils.logging``.  All heavy lifting (redacting sensitive values,
formatting records and writing to the console) is handled by
``RedactingFormatter`` and ``ConsoleHandler``.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional, Union

import requests
from apiconfig.utils.logging import ConsoleHandler, RedactingFormatter, setup_logging

from ..config import ClientConfig

__all__ = ["setup_http_logging", "HttpLifecycleLogger"]


def setup_http_logging(level: int | str = logging.WARNING) -> logging.Logger:
    """Configure the ``crudclient.http`` logger.

    The returned logger will use ``RedactingFormatter`` and ``ConsoleHandler``
    so that request and response details are automatically scrubbed.
    ``apiconfig`` logging is configured with the same handler to ensure
    consistent output across the stack.
    """

    formatter = RedactingFormatter("%(message)s")
    handler = ConsoleHandler()
    handler.setFormatter(formatter)

    # Configure apiconfig's logger first so internal logs share the handler.
    setup_logging(level=level, handlers=[handler], formatter=formatter)

    logger = logging.getLogger("crudclient.http")
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = True

    # Allow apiconfig logs to propagate so test fixtures can capture them
    logging.getLogger("apiconfig").propagate = True
    return logger


class HttpLifecycleLogger:
    """Minimal logger for HTTP request/response lifecycle."""

    config: ClientConfig
    logger: logging.Logger

    def __init__(self, config: ClientConfig, logger: logging.Logger) -> None:
        self.config = config
        self.logger = logger

    def log_request_body_content(self, kwargs: Dict[str, Any]) -> None:
        """Log request body if enabled."""

        body: Optional[Any] = None
        headers: Dict[str, str] = kwargs.get("headers", {})
        if "json" in kwargs and kwargs["json"] is not None:
            body = kwargs["json"]
        elif "data" in kwargs and kwargs["data"] is not None:
            body = kwargs["data"]

        if body is None:
            self.logger.debug("Request body logging enabled but body is empty or not logged (no 'json' or 'data').")
            return

        content_type = headers.get("Content-Type", "unknown").lower() or "unknown"
        self.logger.debug({"message": f"Request body ({content_type})", "body": body})

    def log_response_body_content(self, response: requests.Response) -> None:
        """Log response body if enabled."""

        try:
            body_text = response.text
        except Exception as exc:  # pragma: no cover - extremely unlikely
            self.logger.warning("Could not access response body: %s", exc)
            return

        if not body_text:
            self.logger.debug("Response body logging enabled but body is empty.")
            return

        content_type = response.headers.get("Content-Type", "unknown").lower() or "unknown"
        self.logger.debug({"message": f"Response body ({content_type})", "body": body_text})

    def log_response_details(self, method: str, url: str, response: requests.Response) -> None:
        """Log high level response details."""

        self.logger.debug("Received response for %s %s: Status %d", method, url, response.status_code)
        if response.status_code in (401, 403):
            self.logger.warning("Authentication failed for %s %s: Status %d", method, url, response.status_code)
        elif 400 <= response.status_code < 500:
            self.logger.warning("Client error for %s %s: Status %d", method, url, response.status_code)
        elif response.status_code >= 500:
            self.logger.error("Server error for %s %s: Status %d", method, url, response.status_code)

        headers_to_log = dict(response.headers)
        self.logger.debug({"message": "Response Headers", "headers": headers_to_log})

        if self.config.log_response_body:
            self.log_response_body_content(response)
        else:
            self.logger.debug("Response body logging is disabled.")

    def log_request_details(self, method: str, url: str, kwargs: Dict[str, Any]) -> None:
        """Log outgoing request details."""

        params = kwargs.get("params")
        if params:
            self.logger.debug("Sending request: %s %s Params: %s", method, url, params)
        else:
            self.logger.debug("Sending request: %s %s", method, url)

        headers_to_log = dict(kwargs.get("headers", {}))
        self.logger.debug({"message": "Request Headers", "headers": headers_to_log})

        if self.config.log_request_body:
            self.log_request_body_content(kwargs)
        else:
            self.logger.debug("Request body logging is disabled.")

    def log_request_completion(
        self,
        start_time: float,
        method: str,
        url: str,
        attempt_count: int,
        final_outcome: Union[requests.Response, Exception, None],
    ) -> None:
        """Log the final outcome and duration of the HTTP request."""

        end_time = time.monotonic()
        duration_ms = int((end_time - start_time) * 1000)

        if isinstance(final_outcome, requests.Response):
            if final_outcome.ok:
                self.logger.info(
                    "Request %s %s completed successfully: %d %s in %dms.",
                    method,
                    url,
                    final_outcome.status_code,
                    final_outcome.reason,
                    duration_ms,
                )
            else:
                self.logger.info(
                    "Request %s %s failed after %d attempts: %d %s in %dms.",
                    method,
                    url,
                    attempt_count,
                    final_outcome.status_code,
                    final_outcome.reason,
                    duration_ms,
                )
        elif isinstance(final_outcome, Exception):
            self.logger.info(
                "Request %s %s failed after %d attempts: %s in %dms.",
                method,
                url,
                attempt_count,
                type(final_outcome).__name__,
                duration_ms,
            )
        else:
            self.logger.warning("Request %s %s completed with no outcome recorded in %dms.", method, url, duration_ms)

    def log_http_error(
        self,
        e: requests.exceptions.HTTPError,
        method: Optional[str] = None,
        url: Optional[str] = None,
    ) -> None:
        """Log HTTPError details."""

        response = e.response
        request = e.request
        req_method = method or (request.method if request else "UNKNOWN_METHOD")
        req_url = url or (request.url if request else "UNKNOWN_URL")

        if response is not None:
            log_level = logging.WARNING if 400 <= response.status_code < 500 else logging.ERROR
            try:
                response_snippet = response.text
            except Exception:
                response_snippet = "[Could not read response text]"

            self.logger.log(
                log_level,
                "HTTP error encountered for %s %s: Status %d - Response: %s",
                req_method,
                req_url,
                response.status_code,
                response_snippet,
            )
        else:
            self.logger.error("HTTPError occurred without a response object for %s %s: %s", req_method, req_url, e)

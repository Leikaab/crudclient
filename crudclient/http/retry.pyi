"""
Retry Module for CrudClient
===========================

This module provides retry functionality for the CrudClient library.
It contains classes and functions for managing retry policies and backoff strategies.

Classes:
    - RetryHandler: Manages retry policies and backoff strategies.
    - RetryStrategy: Base class for retry strategies.
    - FixedRetryStrategy: Implements a fixed delay retry strategy.
    - ExponentialBackoffStrategy: Implements an exponential backoff retry strategy.
"""

import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import (  # Added Tuple
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

import requests

from ..exceptions import CrudClientError, NetworkError  # Added NetworkError
from .retry_conditions import RetryCondition  # Import conditions
from .retry_strategies import RetryStrategy  # Import strategies

class RetryEvent(Enum):
    """Enum representing different retry events."""

    FORBIDDEN = 403
    UNAUTHORIZED = 401
    SERVER_ERROR = 500
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    CUSTOM = "custom"

# Note: RetryStrategy and RetryCondition definitions are now in their respective .pyi files
# crudclient/http/retry_strategies.pyi
# crudclient/http/retry_conditions.pyi

class RetryHandler:
    """Handles the logic for retrying HTTP requests based on configured conditions."""

    max_retries: int
    retry_strategy: RetryStrategy
    retry_conditions: List[RetryCondition]
    on_retry_callback: Optional[Callable[[int, float, Optional[requests.Response], Optional[Exception]], None]]

    def __init__(
        self,
        max_retries: int = ...,
        retry_strategy: Optional[RetryStrategy] = ...,
        retry_conditions: Optional[List[RetryCondition]] = ...,
        on_retry_callback: Optional[Callable[[int, float, Optional[requests.Response], Optional[Exception]], None]] = ...,
    ) -> None:
        """Initializes the RetryHandler.

        Args:
            max_retries: Maximum number of retry attempts (0 means no retries).
            retry_strategy: The strategy for calculating delays between retries.
                            Defaults to ExponentialBackoffStrategy.
            retry_conditions: A list of conditions that trigger a retry.
                              Defaults to retrying on common server errors (500, 502, 503, 504)
                              and network errors (Timeout, ConnectionError).
            on_retry_callback: An optional function called before each retry attempt.
                               It receives (attempt, delay, last_response, last_exception).

        Raises:
            ValueError: If max_retries is negative.
            TypeError: If retry_strategy, retry_conditions, or on_retry_callback have incorrect types.
        """
        ...

    def should_retry(self, attempt: int, response: Optional[requests.Response] = ..., exception: Optional[Exception] = ...) -> bool:
        """
        Determine whether a request should be retried.

        Args:
            attempt (int): The current retry attempt number (0-based).
            response (Optional[requests.Response]): The response from the request, if any.
            exception (Optional[Exception]): The exception raised by the request, if any.

        Returns:
            bool: True if the request should be retried, False otherwise.
        """
        ...

    def get_delay(self, attempt: int) -> float:
        """
        Calculate the delay before the next retry attempt.

        Args:
            attempt (int): The current retry attempt number (1-based).

        Returns:
            float: The delay in seconds before the next retry.
        """
        ...

    def execute_with_retry(
        self,
        method: str,
        url: str,
        request_func: Callable[[], requests.Response],
        session: Optional[requests.Session] = ...,  # Session not directly used, passed for context
        setup_auth_func: Optional[Callable[[], None]] = ...,
    ) -> Tuple[Union[requests.Response, Exception], int]:  # Corrected return type
        """Executes a request function with retry logic.

        Handles retries based on configured conditions and strategy. Logs errors
        and raises NetworkError if retries are exhausted due to network issues.
        Returns the final response or caught exception along with the attempt count.

        Args:
            method: The HTTP method (for logging).
            url: The request URL (for logging).
            request_func: The function that executes the actual HTTP request.
            session: The requests.Session object (optional, for context).
            setup_auth_func: An optional function to refresh authentication,
                             typically called on 401 errors before retrying.

        Returns:
            A tuple containing:
            - The final `requests.Response` on success or retryable non-OK status.
            - The caught `Exception` if the request function failed unexpectedly
              (and was not retryable or retries exhausted).
            - The total number of attempts made (including the final one).

        Raises:
            NetworkError: If a `requests.RequestException` occurs and retries are
                          exhausted or the exception is not configured for retry.
            TypeError: If `request_func` or `setup_auth_func` are not callable.
        """
        ...

    def _execute_request(
        self,
        request_func: Callable[[], requests.Response],
        method: str,
        url: str,
        attempt: int,
    ) -> Tuple[Optional[requests.Response], Optional[Exception]]:
        """Executes the request function and handles exceptions."""
        ...

    def _handle_response(
        self,
        response: Optional[requests.Response],
        exception: Optional[Exception],
        attempt: int,
        method: str,
        url: str,
    ) -> Tuple[Optional[requests.Response], bool]:
        """Processes the response or exception, determining if retry is needed."""
        ...

    def _perform_retry_delay_and_callbacks(
        self,
        attempt: int,
        last_response: Optional[requests.Response],
        last_exception: Optional[Exception],
        setup_auth_func: Optional[Callable[[], None]],
        method: str,
        url: str,
    ) -> None:
        """Calculates delay, sleeps, and calls callbacks before the next retry."""
        ...
    # maybe_retry_after_403 stub removed as method was removed from implementation.

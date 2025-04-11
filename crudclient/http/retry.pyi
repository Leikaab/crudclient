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
from typing import Any, Callable, Dict, List, Optional, Type, Union

import requests

from ..exceptions import CrudClientError

class RetryEvent(Enum):
    """Enum representing different retry events."""

    FORBIDDEN = 403
    UNAUTHORIZED = 401
    SERVER_ERROR = 500
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    CUSTOM = "custom"

class RetryStrategy(ABC):
    """
    Base class for retry strategies.

    This abstract class defines the interface for retry strategies.
    Concrete implementations should provide specific backoff algorithms.
    """

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """
        Calculate the delay before the next retry attempt.

        Args:
            attempt (int): The current retry attempt number (1-based).

        Returns:
            float: The delay in seconds before the next retry.
        """
        ...

class FixedRetryStrategy(RetryStrategy):
    """
    Implements a fixed delay retry strategy.

    This strategy uses the same delay between each retry attempt.
    """

    delay: float

    def __init__(self, delay: float = ...) -> None:
        """
        Initialize the fixed retry strategy.

        Args:
            delay (float): The fixed delay in seconds between retry attempts.
                Defaults to 1.0 second.
        """
        ...

    def get_delay(self, attempt: int) -> float:
        """
        Calculate the delay before the next retry attempt.

        Args:
            attempt (int): The current retry attempt number (1-based).

        Returns:
            float: The fixed delay in seconds.
        """
        ...

class ExponentialBackoffStrategy(RetryStrategy):
    """
    Implements an exponential backoff retry strategy.

    This strategy increases the delay exponentially between retry attempts,
    optionally with jitter to prevent synchronized retries.
    """

    base_delay: float
    max_delay: float
    factor: float
    jitter: bool

    def __init__(
        self,
        base_delay: float = ...,
        max_delay: float = ...,
        factor: float = ...,
        jitter: bool = ...,
    ) -> None:
        """
        Initialize the exponential backoff strategy.

        Args:
            base_delay (float): The base delay in seconds. Defaults to 1.0 second.
            max_delay (float): The maximum delay in seconds. Defaults to 60.0 seconds.
            factor (float): The exponential factor. Defaults to 2.0.
            jitter (bool): Whether to add jitter to the delay. Defaults to True.
        """
        ...

    def get_delay(self, attempt: int) -> float:
        """
        Calculate the delay before the next retry attempt.

        Args:
            attempt (int): The current retry attempt number (1-based).

        Returns:
            float: The calculated delay in seconds.
        """
        ...

class RetryCondition:
    """
    Represents a condition for retrying a request.

    This class encapsulates the logic for determining whether a request should be retried
    based on the response or exception.
    """

    events: List[Union[RetryEvent, int]]
    status_codes: List[int]
    exceptions: List[Type[Exception]]
    custom_condition: Optional[Callable[[Optional[requests.Response], Optional[Exception]], bool]]

    def __init__(
        self,
        events: Optional[List[Union[RetryEvent, int]]] = ...,
        status_codes: Optional[List[int]] = ...,
        exceptions: Optional[List[Type[Exception]]] = ...,
        custom_condition: Optional[Callable[[Optional[requests.Response], Optional[Exception]], bool]] = ...,
    ) -> None:
        """
        Initialize the retry condition.

        Args:
            events (List[Union[RetryEvent, int]], optional): List of retry events or status codes.
            status_codes (List[int], optional): List of status codes to retry on.
            exceptions (List[Type[Exception]], optional): List of exception types to retry on.
            custom_condition (Callable[[Optional[requests.Response], Optional[Exception]], bool], optional):
                Custom function to determine whether to retry.
        """
        ...

    def should_retry(self, response: Optional[requests.Response] = ..., exception: Optional[Exception] = ...) -> bool:
        """
        Determine whether a request should be retried.

        Args:
            response (Optional[requests.Response]): The response from the request, if any.
            exception (Optional[Exception]): The exception raised by the request, if any.

        Returns:
            bool: True if the request should be retried, False otherwise.
        """
        ...

class RetryHandler:
    """
    Manages retry policies and backoff strategies.

    This class is responsible for determining whether a request should be retried
    and calculating the delay before the next retry attempt.
    """

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
        """
        Initialize the retry handler.

        Args:
            max_retries (int): Maximum number of retry attempts. Defaults to 3.
            retry_strategy (RetryStrategy, optional): The strategy to use for calculating
                retry delays. Defaults to ExponentialBackoffStrategy.
            retry_conditions (List[RetryCondition], optional): List of conditions for retrying
                a request. Defaults to a condition that retries on 5xx status codes and
                connection/timeout errors.
            on_retry_callback (Callable, optional): Callback function to call before each retry.
                The function receives the current attempt number, delay, response, and exception.
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
        request_func: Callable[[], requests.Response],
        session: Optional[requests.Session] = ...,
        setup_auth_func: Optional[Callable[[], None]] = ...,
    ) -> requests.Response:
        """
        Execute a request function with retry logic.

        Args:
            request_func (Callable[[], requests.Response]): Function that makes the HTTP request.
            session (Optional[requests.Session]): The session to use for the request.
            setup_auth_func (Optional[Callable[[], None]]): Function to call to refresh auth before retrying.

        Returns:
            requests.Response: The response from the successful request.

        Raises:
            CrudClientError: If all retry attempts fail.
        """
        ...

    def maybe_retry_after_403(
        self, method: str, url: str, kwargs: dict, response: requests.Response, session: requests.Session, setup_auth_func: Callable[[], None]
    ) -> requests.Response:
        """
        Retry a request after receiving a 403 Forbidden response.

        This method is extracted from the Client class and refactored to use the RetryHandler.

        Args:
            method (str): The HTTP method for the request.
            url (str): The URL for the request.
            kwargs (dict): Additional keyword arguments for the request.
            response (requests.Response): The response from the original request.
            session (requests.Session): The session to use for the retry.
            setup_auth_func (Callable[[], None]): Function to call to refresh auth before retrying.

        Returns:
            requests.Response: The response from the retry or the original response if no retry.
        """
        ...

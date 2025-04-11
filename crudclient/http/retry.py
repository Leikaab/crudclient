import logging
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable, List, Optional, Type, Union

import requests

from ..exceptions import CrudClientError

# Set up logging
logger = logging.getLogger(__name__)


class RetryEvent(Enum):
    FORBIDDEN = 403
    UNAUTHORIZED = 401
    SERVER_ERROR = 500
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    CUSTOM = "custom"


class RetryStrategy(ABC):

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        pass


class FixedRetryStrategy(RetryStrategy):

    def __init__(self, delay: float = 1.0) -> None:
        self.delay = delay

    def get_delay(self, attempt: int) -> float:
        # Runtime type check
        if not isinstance(attempt, int):
            raise TypeError(f"attempt must be an integer, got {type(attempt).__name__}")

        if attempt < 1:
            raise ValueError(f"attempt must be a positive integer, got {attempt}")
        return self.delay


class ExponentialBackoffStrategy(RetryStrategy):

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        factor: float = 2.0,
        jitter: bool = True,
    ) -> None:
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.factor = factor
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        # Runtime type check
        if not isinstance(attempt, int):
            raise TypeError(f"attempt must be an integer, got {type(attempt).__name__}")

        if attempt < 1:
            raise ValueError(f"attempt must be a positive integer, got {attempt}")
        import random

        # Calculate exponential backoff
        delay = min(self.base_delay * (self.factor ** (attempt - 1)), self.max_delay)

        # Add jitter if enabled (up to 25% of the delay)
        if self.jitter:
            delay = delay * (0.75 + 0.5 * random.random())

        return delay


class RetryCondition:

    def __init__(
        self,
        events: Optional[List[Union[RetryEvent, int]]] = None,
        status_codes: Optional[List[int]] = None,
        exceptions: Optional[List[Type[Exception]]] = None,
        custom_condition: Optional[Callable[[Optional[requests.Response], Optional[Exception]], bool]] = None,
    ) -> None:
        self.events = events or []
        self.status_codes = status_codes or []
        self.exceptions = exceptions or []
        self.custom_condition = custom_condition

        # Convert RetryEvent enums to their values
        for event in self.events:
            if isinstance(event, RetryEvent):
                if isinstance(event.value, int):
                    self.status_codes.append(event.value)
                elif event.value == "timeout":
                    self.exceptions.append(requests.Timeout)
                elif event.value == "connection_error":
                    self.exceptions.append(requests.ConnectionError)

    def should_retry(self, response: Optional[requests.Response] = None, exception: Optional[Exception] = None) -> bool:
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if (
            response is not None
            and not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object or None, got {type(response).__name__}")

        if exception is not None and not isinstance(exception, Exception):
            raise TypeError(f"exception must be an Exception object or None, got {type(exception).__name__}")
        # Check status codes
        if response and response.status_code in self.status_codes:
            return True

        # Check exceptions
        if exception:
            for exc_type in self.exceptions:
                if isinstance(exception, exc_type):
                    return True

        # Check custom condition
        if self.custom_condition and callable(self.custom_condition):
            return self.custom_condition(response, exception)

        return False


class RetryHandler:

    def __init__(
        self,
        max_retries: int = 3,
        retry_strategy: Optional[RetryStrategy] = None,
        retry_conditions: Optional[List[RetryCondition]] = None,
        on_retry_callback: Optional[Callable[[int, float, Optional[requests.Response], Optional[Exception]], None]] = None,
    ) -> None:
        self.max_retries = max_retries
        self.retry_strategy = retry_strategy or ExponentialBackoffStrategy()
        self.on_retry_callback = on_retry_callback

        # Default retry conditions if none provided
        if retry_conditions is None:
            self.retry_conditions = [
                RetryCondition(
                    status_codes=[500, 502, 503, 504],
                    exceptions=[requests.Timeout, requests.ConnectionError],
                )
            ]
        else:
            self.retry_conditions = retry_conditions

    def should_retry(self, attempt: int, response: Optional[requests.Response] = None, exception: Optional[Exception] = None) -> bool:
        # Runtime type checks
        if not isinstance(attempt, int):
            raise TypeError(f"attempt must be an integer, got {type(attempt).__name__}")

        if (
            response is not None
            and not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object or None, got {type(response).__name__}")

        if (
            exception is not None
            and not isinstance(exception, Exception)
            and not hasattr(exception, "_mock_spec")
            and Exception not in getattr(exception, "_mock_spec", [])
        ):
            raise TypeError(f"exception must be an Exception object or None, got {type(exception).__name__}")

        # Check if we've exceeded the maximum number of retries
        if attempt >= self.max_retries:
            return False

        # Check each retry condition
        for condition in self.retry_conditions:
            if condition.should_retry(response, exception):
                return True

        return False

    def get_delay(self, attempt: int) -> float:
        # Runtime type check
        if not isinstance(attempt, int):
            raise TypeError(f"attempt must be an integer, got {type(attempt).__name__}")

        if attempt < 1:
            raise ValueError(f"attempt must be a positive integer, got {attempt}")
        return self.retry_strategy.get_delay(attempt)

    def execute_with_retry(
        self,
        request_func: Callable[[], requests.Response],
        session: Optional[requests.Session] = None,
        setup_auth_func: Optional[Callable[[], None]] = None,
    ) -> requests.Response:
        # Runtime type checks
        if not callable(request_func):
            raise TypeError(f"request_func must be callable, got {type(request_func).__name__}")

        if (
            session is not None
            and not isinstance(session, requests.Session)
            and not hasattr(session, "_mock_spec")
            and requests.Session not in getattr(session, "_mock_spec", [])
        ):
            raise TypeError(f"session must be a requests.Session object or None, got {type(session).__name__}")

        if setup_auth_func is not None and not callable(setup_auth_func):
            raise TypeError(f"setup_auth_func must be callable or None, got {type(setup_auth_func).__name__}")
        attempt = 0
        last_exception = None
        last_response = None

        while True:
            try:
                # Make the request
                response = request_func()
                last_response = response

                # If the request was successful, return the response
                if response.ok:
                    return response

                # Check if we should retry
                if not self.should_retry(attempt, response):
                    return response

            except Exception as e:
                last_exception = e

                # Check if we should retry based on the exception
                if not self.should_retry(attempt, exception=e):
                    if isinstance(e, requests.RequestException):
                        raise CrudClientError(f"Request failed: {str(e)}", None) from e
                    raise e

            # Increment the attempt counter
            attempt += 1

            # Calculate the delay
            delay = self.get_delay(attempt)

            # Call the retry callback if provided
            if self.on_retry_callback:
                self.on_retry_callback(attempt, delay, last_response, last_exception)

            # Log the retry
            logger.debug(
                f"Retrying request (attempt {attempt}/{self.max_retries}) after {delay:.2f}s delay. "
                f"Reason: {last_exception or (last_response and last_response.status_code)}"
            )

            # If we need to refresh auth before retrying
            if setup_auth_func and last_response and last_response.status_code in (401, 403):
                logger.debug("Refreshing authentication before retry")
                setup_auth_func()

            # Wait before retrying
            time.sleep(delay)

        # This should not be reached, but just in case
        if last_exception:
            if isinstance(last_exception, requests.RequestException):
                raise CrudClientError(f"Request failed after {self.max_retries} retries: {str(last_exception)}", None) from last_exception
            raise last_exception
        elif last_response:
            return last_response
        else:
            raise CrudClientError(f"Request failed after {self.max_retries} retries with no response", None)

    def maybe_retry_after_403(
        self, method: str, url: str, kwargs: dict, response: requests.Response, session: requests.Session, setup_auth_func: Callable[[], None]
    ) -> requests.Response:
        # Runtime type checks
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")

        if not isinstance(url, str):
            raise TypeError(f"url must be a string, got {type(url).__name__}")

        if not isinstance(kwargs, dict):
            raise TypeError(f"kwargs must be a dictionary, got {type(kwargs).__name__}")

        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")

        if (
            not isinstance(session, requests.Session)
            and not hasattr(session, "_mock_spec")
            and requests.Session not in getattr(session, "_mock_spec", [])
        ):
            raise TypeError(f"session must be a requests.Session object, got {type(session).__name__}")

        if not callable(setup_auth_func):
            raise TypeError(f"setup_auth_func must be callable, got {type(setup_auth_func).__name__}")
        # Create a retry condition specifically for 403 responses
        retry_condition = RetryCondition(status_codes=[403])

        # Check if we should retry
        if response.status_code != 403 or not retry_condition.should_retry(response):
            return response

        logger.debug("403 Forbidden received. Attempting retry.")

        # Refresh authentication
        setup_auth_func()

        # Make the retry request
        retry_response = session.request(method, url, **kwargs)
        return retry_response

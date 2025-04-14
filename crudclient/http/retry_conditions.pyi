from enum import Enum
from typing import Callable, List, Optional, Type, Union

import requests

class RetryEvent(Enum):
    """Enumeration of common events that might trigger a retry."""

    FORBIDDEN = ...
    UNAUTHORIZED = ...
    SERVER_ERROR = ...
    TIMEOUT = ...
    CONNECTION_ERROR = ...
    CUSTOM = ...

class RetryCondition:
    """Defines conditions under which a request should be retried."""

    events: List[Union[RetryEvent, int]]
    status_codes: List[int]
    exceptions: List[Type[Exception]]
    custom_condition: Optional[Callable[[Optional[requests.Response], Optional[Exception]], bool]]

    def __init__(
        self,
        events: Optional[List[Union[RetryEvent, int]]] = None,
        status_codes: Optional[List[int]] = None,
        exceptions: Optional[List[Type[Exception]]] = None,
        custom_condition: Optional[Callable[[Optional[requests.Response], Optional[Exception]], bool]] = None,
    ) -> None:
        """Initializes the RetryCondition.

        Args:
            events: A list of RetryEvent enums or integer status codes to retry on.
                    These are processed to populate the `status_codes` and `exceptions` lists.
            status_codes: A list of specific HTTP status codes to retry on.
                          These are combined with codes derived from `events`.
            exceptions: A list of specific exception types to retry on.
                        These are combined with exception types derived from `events`.
            custom_condition: A callable that takes an optional response and optional
                              exception and returns True if a retry should occur.
                              This is checked *after* status codes and exceptions.
        """
        ...

    def should_retry(self, response: Optional[requests.Response] = None, exception: Optional[Exception] = None) -> bool:
        """Checks if a retry should occur based on the response or exception.

        Checks against `status_codes`, `exceptions`, and `custom_condition` in that order.

        Args:
            response: The HTTP response received (if any).
            exception: The exception raised during the request (if any).

        Returns:
            True if any configured condition matches, False otherwise.
        """
        ...

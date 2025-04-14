import logging
from enum import Enum
from typing import TYPE_CHECKING, Callable, List, Optional, Type, Union

import requests
from requests.exceptions import ConnectionError, Timeout

if TYPE_CHECKING:
    # Avoid potential circular imports if conditions need complex types
    pass

logger = logging.getLogger(__name__)


class RetryEvent(Enum):
    FORBIDDEN = 403
    UNAUTHORIZED = 401
    SERVER_ERROR = 500  # Generic 5xx, specific codes can be added too
    TIMEOUT = "timeout"
    CONNECTION_ERROR = "connection_error"
    CUSTOM = "custom"  # Placeholder for custom logic


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

        # Process events to populate status_codes and exceptions lists
        processed_events = set()
        for event in self.events:
            if event in processed_events:
                continue
            processed_events.add(event)

            if isinstance(event, RetryEvent):
                if isinstance(event.value, int):
                    if event.value not in self.status_codes:
                        self.status_codes.append(event.value)
                elif event.value == "timeout":
                    if Timeout not in self.exceptions:
                        self.exceptions.append(Timeout)
                elif event.value == "connection_error":
                    if ConnectionError not in self.exceptions:
                        self.exceptions.append(ConnectionError)
            elif isinstance(event, int):  # Allow raw status codes in events list
                if event not in self.status_codes:
                    self.status_codes.append(event)

        # Ensure uniqueness in final lists
        self.status_codes = sorted(list(set(self.status_codes)))
        # Cannot easily sort exception types, but set ensures uniqueness
        unique_exceptions = []
        seen_exceptions = set()
        for exc in self.exceptions:
            if exc not in seen_exceptions:
                unique_exceptions.append(exc)
                seen_exceptions.add(exc)
        self.exceptions = unique_exceptions

    def should_retry(self, response: Optional[requests.Response] = None, exception: Optional[Exception] = None) -> bool:
        # Basic type validation (lenient with mocks)
        if (
            response is not None
            and not isinstance(response, requests.Response)
            and not (hasattr(response, "_mock_spec") and requests.Response in getattr(response, "_mock_spec", []))
        ):
            logger.warning(f"Invalid type for response: {type(response).__name__}. Expected requests.Response or compatible mock.")
            return False

        if exception is not None and not isinstance(exception, Exception):
            logger.warning(f"Invalid type for exception: {type(exception).__name__}. Expected Exception or None.")
            return False

        # Check status codes
        if response is not None and response.status_code in self.status_codes:
            logger.debug(f"Retry condition met: Response status code {response.status_code} is in {self.status_codes}")
            return True

        # Check exceptions
        if exception is not None:
            for exc_type in self.exceptions:
                # Use issubclass check for broader exception matching if needed,
                # but isinstance is usually sufficient here.
                if isinstance(exception, exc_type):
                    logger.debug(f"Retry condition met: Exception type {type(exception).__name__} matches {exc_type.__name__}")
                    return True

        # Check custom condition
        if self.custom_condition and callable(self.custom_condition):
            try:
                custom_result = self.custom_condition(response, exception)
                if custom_result:
                    logger.debug("Retry condition met: Custom condition returned True")
                return custom_result
            except Exception as e:
                logger.error(f"Custom retry condition failed: {e}", exc_info=True)
                return False  # Don't retry if the condition itself fails

        return False

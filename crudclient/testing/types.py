"""
Type definitions for the crudclient testing framework.

This module provides type definitions and utility classes used throughout the testing framework.
"""

import requests
import json
from typing import Any, Dict, Optional
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union

# Type aliases for HTTP components
Headers = Dict[str, str]
QueryParams = Dict[str, str]
HttpMethod = str
StatusCode = int
RequestBody = Union[Dict[str, Any], List[Any], str, bytes, None]
ResponseBody = Union[Dict[str, Any], List[Any], str, bytes, None]
ResponseData = Dict[str, Any]

# Type aliases for spy functionality
SpyTarget = Any
CallRecord = Dict[str, Any]


class MockResponse(requests.Response):
    """
    A configurable mock response object that can be used to simulate various API responses.

    This class extends the requests.Response class to provide a convenient way to create
    mock responses for testing purposes.
    """

    def __init__(
        self,
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        content: Optional[bytes] = None,
        error: Optional[Exception] = None,
        delay_ms: int = 0,
    ):
        """
        Initialize a mock response.

        Args:
            status_code: HTTP status code
            json_data: JSON data to return
            text: Text content to return
            headers: HTTP headers
            content: Raw content as bytes
            error: Exception to raise when accessing response data
            delay_ms: Delay in milliseconds before returning the response
        """
        super().__init__()
        self.status_code = status_code
        self._json_data = json_data
        self._text = text if text is not None else (json.dumps(json_data) if json_data else "")
        self.headers.update(headers or {"Content-Type": "application/json"})
        self._content = content or self._text.encode("utf-8") or b""
        self.error = error
        self.delay_ms = delay_ms

        # Add headers to the response
        for key, value in self.headers.items():
            self.headers[key] = value

    def json(self) -> Any:
        """
        Return the JSON data.

        Returns:
            The parsed JSON data

        Raises:
            ValueError: If no JSON data is available
            Exception: If an error was configured
        """
        # Apply configured delay
        if self.delay_ms > 0:
            import time
            time.sleep(self.delay_ms / 1000.0)

        if self.error:
            raise self.error
        if self._json_data is None:
            raise ValueError("No JSON data available")
        return self._json_data

    @property
    def text(self) -> str:
        """
        Return the response text.

        Returns:
            The response text
        """
        # Apply configured delay
        if self.delay_ms > 0:
            import time
            time.sleep(self.delay_ms / 1000.0)

        return self._text

    @property
    def content(self) -> bytes:
        """
        Return the response content as bytes.

        Returns:
            The response content as bytes
        """
        # Apply configured delay
        if self.delay_ms > 0:
            import time
            time.sleep(self.delay_ms / 1000.0)

        return self._content or b""

    def raise_for_status(self) -> None:
        """
        Raise an exception if the status code indicates an error.

        Raises:
            AuthenticationError: If the status code is 401 or 403
            HTTPError: For other error status codes
        """
        if self.status_code >= 400:
            # Import here to avoid circular imports
            from crudclient.exceptions import AuthenticationError

            # For authentication errors, raise AuthenticationError
            if self.status_code in (401, 403):
                error_data = self._json_data if hasattr(self, '_json_data') and self._json_data else self.text
                raise AuthenticationError(f"Authentication failed: {error_data}", self)
            else:
                # For other errors, raise HTTPError
                raise requests.HTTPError(f"HTTP Error: {self.status_code}")

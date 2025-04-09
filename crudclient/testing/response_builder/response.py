"""
Mock response implementation for testing.

This module provides a configurable mock response class that can be used to simulate
various API responses in tests. It extends the requests.Response class to provide
a familiar interface while allowing for custom configuration of status codes,
response data, headers, and error conditions.
"""

import json
from typing import Any, Dict, Optional

import requests


class MockResponse(requests.Response):
    """
    A configurable mock response object that can be used to simulate various API responses.

    This class extends the standard requests.Response class to provide a realistic
    response object that can be configured with custom status codes, JSON data,
    text content, headers, and error conditions. It can be used to simulate both
    successful and error responses from APIs.
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
        Initialize a mock response with configurable properties.

        Args:
            status_code: HTTP status code for the response
            json_data: JSON data to return in the response body
            text: Text content to return in the response body
            headers: HTTP headers to include in the response
            content: Raw content as bytes to return in the response body
            error: Exception to raise when accessing response data
            delay_ms: Simulated network delay in milliseconds
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
        Return the JSON data from the response.

        This method simulates the behavior of the requests.Response.json() method,
        including applying any configured delay and raising any configured errors.

        Returns:
            The JSON data configured for this response

        Raises:
            Exception: If an error was configured for this response
            ValueError: If no JSON data was configured for this response
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

        This property simulates the behavior of the requests.Response.text property,
        including applying any configured delay.

        Returns:
            The text content configured for this response
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

        This property simulates the behavior of the requests.Response.content property,
        including applying any configured delay.

        Returns:
            The content configured for this response as bytes
        """
        # Apply configured delay
        if self.delay_ms > 0:
            import time
            time.sleep(self.delay_ms / 1000.0)

        return self._content or b""

    def raise_for_status(self) -> None:
        """
        Raise an exception if the status code indicates an error.

        This method simulates the behavior of the requests.Response.raise_for_status() method,
        raising appropriate exceptions based on the status code.

        Raises:
            AuthenticationError: If the status code is 401 or 403
            HTTPError: If the status code is 400 or higher
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

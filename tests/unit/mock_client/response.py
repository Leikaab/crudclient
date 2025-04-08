"""
Mock response implementation for testing.
"""

import json
from typing import Any, Dict, Optional

import requests


class MockResponse(requests.Response):
    """A configurable mock response object that can be used to simulate various API responses."""

    def __init__(
        self,
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        content: Optional[bytes] = None,
        error: Optional[Exception] = None,
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
        """
        super().__init__()
        self.status_code = status_code
        self._json_data = json_data
        self._text = text if text is not None else (json.dumps(json_data) if json_data else "")
        self.headers.update(headers or {"Content-Type": "application/json"})
        self._content = content or self._text.encode("utf-8") or b""
        self.error = error

        # Add headers to the response
        for key, value in self.headers.items():
            self.headers[key] = value

    def json(self) -> Any:
        """Return the JSON data."""
        if self.error:
            raise self.error
        if self._json_data is None:
            raise ValueError("No JSON data available")
        return self._json_data

    @property
    def text(self) -> str:
        """Return the response text."""
        return self._text

    @property
    def content(self) -> bytes:
        """Return the response content as bytes."""
        return self._content or b""

    def raise_for_status(self) -> None:
        """Raise an exception if the status code indicates an error."""
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP Error: {self.status_code}")

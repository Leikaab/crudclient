"""
Request recording for mock client.
"""

import time
from typing import Any, Dict, Optional

from .response import MockResponse


class RequestRecord:
    """Records details about a request made to the mock client."""

    def __init__(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        response: Optional[MockResponse] = None,
    ):
        """
        Initialize request record.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            data: Form data
            json: JSON data
            headers: HTTP headers
            response: Response returned for this request
        """
        self.method = method.upper()
        self.url = url
        self.params = params
        self.data = data
        self.json = json
        self.headers = headers
        self.response = response
        self.timestamp = time.time()

    def __repr__(self) -> str:
        """Return string representation of the request record."""
        return f"<RequestRecord {self.method} {self.url}>"

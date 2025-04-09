"""
Request recording for CRUD mock implementations.

This module provides a class for recording HTTP requests made to the CRUD mock classes,
which can be used for verification in tests.
"""

import time
from typing import Any, Dict, Optional

from crudclient.testing.response_builder.response import MockResponse


class RequestRecord:
    """
    Records details about a request made to the CRUD mock.

    This class stores information about an HTTP request, including the method,
    URL, parameters, data, and the response that was returned.
    """

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
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
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
        self.headers = headers or {}
        self.response = response
        self.timestamp = time.time()

        # Add URL parameters to the URL if they exist
        if params and params:
            param_str = "&".join(f"{k}={v}" for k, v in params.items())
            if "?" in self.url:
                self.url = f"{self.url}&{param_str}"
            else:
                self.url = f"{self.url}?{param_str}"

    def __repr__(self) -> str:
        """Return string representation of the request record."""
        return f"<RequestRecord {self.method} {self.url}>"

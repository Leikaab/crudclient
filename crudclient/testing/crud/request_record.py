import time
from typing import Any, Dict, Optional

from crudclient.testing.response_builder.response import MockResponse


class RequestRecord:
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
        return f"<RequestRecord {self.method} {self.url}>"

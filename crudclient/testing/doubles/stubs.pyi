import json
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

import requests

class Response:
    """
    Abstract base class defining the interface for an HTTP response object.
    Mimics parts of the interface of requests.Response or httpx.Response.
    """

    def __init__(self) -> None: ...
    @property
    def status_code(self) -> int:
        """The HTTP status code of the response."""
        ...

    @property
    def content(self) -> bytes:
        """The response body as bytes."""
        ...

    @property
    def text(self) -> str:
        """The response body decoded as text."""
        ...

    @property
    def headers(self) -> Dict[str, str]:
        """A dictionary of response headers."""
        ...

    def json(self) -> Any:
        """
        Parse the response body as JSON.

        Raises:
            ValueError: If the response body is not valid JSON.
        """
        ...

    def raise_for_status(self) -> None:
        """
        Raise an HTTPError for bad status codes (4xx or 5xx).
        """
        ...

class StubResponse(Response):
    """
    A concrete stub implementation of the Response interface for testing.

    Allows creating response objects with specific status codes, content, headers, etc.
    """

    _status_code: int
    _headers: Dict[str, str]
    _encoding: str
    _elapsed: timedelta
    _content: bytes
    _text: str
    _json_data: Any

    def __init__(
        self,
        status_code: int = 200,
        content: Optional[Union[str, bytes, Dict[str, Any], List[Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        encoding: str = "utf-8",
        elapsed: Optional[timedelta] = None,
    ) -> None:
        """
        Initialize the StubResponse.

        Args:
            status_code: The HTTP status code.
            content: The response body (can be dict, list, str, or bytes).
            headers: Response headers.
            encoding: Encoding for text/bytes conversion.
            elapsed: Simulated time elapsed for the request.
        """
        ...

    @property
    def status_code(self) -> int: ...
    @property
    def content(self) -> bytes: ...
    @property
    def text(self) -> str: ...
    @property
    def headers(self) -> Dict[str, str]: ...
    @property
    def encoding(self) -> str:
        """The encoding used for text decoding."""
        ...

    @property
    def elapsed(self) -> timedelta:
        """The simulated time elapsed for the request."""
        ...

    def json(self) -> Any: ...
    def raise_for_status(self) -> None: ...


from typing import Any, Dict, Optional, Tuple
from urllib.parse import urljoin

import requests
from requests import Response

from ..exceptions import RequestNotConfiguredError
from ..types import Headers, HttpMethod, QueryParams, RequestBody, ResponseBody, StatusCode


class MockHTTPClient:

    def __init__(self, base_url: str = "https://api.example.com") -> None:
        self.base_url = base_url
        self._configured_responses: Dict[Tuple[HttpMethod, str], Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]] = {}

    def reset(self) -> None:
        self._configured_responses = {}

    def configure_response(
        self,
        method: HttpMethod,
        path: str,
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None
    ) -> None:
        # Normalize the method to uppercase
        method = method.upper()

        # Normalize the path to remove leading slash if present
        path = path.lstrip('/')

        # Store the configured response
        self._configured_responses[(method, path)] = (
            status_code,
            data or {},
            headers or {},
            error
        )

    def _get_configured_response(
        self,
        method: HttpMethod,
        path: str
    ) -> Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]:
        # Normalize the method to uppercase
        method = method.upper()

        # Normalize the path to remove leading slash if present
        path = path.lstrip('/')

        # Get the configured response
        key = (method, path)
        if key not in self._configured_responses:
            raise RequestNotConfiguredError(method, path)

        return self._configured_responses[key]

    def request(
        self,
        method: HttpMethod,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
    ) -> Response:
        # Get the configured response
        status_code, response_body, response_headers, error = self._get_configured_response(
            method=method,
            path=path
        )

        # If an error is configured, raise it
        if error is not None:
            raise error

        # Create a Response object with the configured response
        url = urljoin(self.base_url, path)
        response = requests.Response()
        response.status_code = status_code
        response.headers.update(response_headers or {})
        response._content = (response_body.encode('utf-8') if isinstance(response_body, str)
                             else (response_body if response_body is not None else b''))
        response.url = url

        return response

    # Convenience methods for common HTTP methods

    def get(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        **kwargs: Any
    ) -> Response:
        return self.request(
            method="GET",
            path=path,
            headers=headers,
            params=params,
            **kwargs
        )

    def post(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
    ) -> Response:
        return self.request(
            method="POST",
            path=path,
            headers=headers,
            params=params,
            data=data,
            **kwargs
        )

    def put(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
    ) -> Response:
        return self.request(
            method="PUT",
            path=path,
            headers=headers,
            params=params,
            data=data,
            **kwargs
        )

    def delete(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        **kwargs: Any
    ) -> Response:
        return self.request(
            method="DELETE",
            path=path,
            headers=headers,
            params=params,
            **kwargs
        )

    def patch(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
    ) -> Response:
        return self.request(
            method="PATCH",
            path=path,
            headers=headers,
            params=params,
            data=data,
            **kwargs
        )

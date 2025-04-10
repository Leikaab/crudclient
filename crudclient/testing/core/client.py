
import re
from typing import Any, Dict, List, Optional, Pattern, Union

from crudclient.auth.base import AuthStrategy
from crudclient.config import ClientConfig

from ..types import Headers, HttpMethod, QueryParams, RequestBody, ResponseBody, StatusCode


class MockClient:

    def __init__(
        self,
        http_client: Any,
        base_url: str = "https://api.example.com",
        enable_spy: bool = False,
        **kwargs: Any
    ) -> None:
        self.http_client = http_client
        self.base_url = base_url
        self.enable_spy = enable_spy

        # Create a config object
        self.config = ClientConfig(hostname=base_url)

        # Authentication strategy
        self._auth_strategy: Optional[AuthStrategy] = None

        # Request history
        self.request_history: List[Dict[str, Any]] = []

    def configure_response(
        self,
        method: HttpMethod,
        path: str,
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None
    ) -> None:
        self.http_client.configure_response(
            method=method,
            path=path,
            status_code=status_code,
            data=data,
            headers=headers,
            error=error
        )

    def with_response_pattern(
        self,
        method: HttpMethod,
        path_pattern: Union[str, Pattern],
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None
    ) -> None:
        # Delegate to the underlying HTTP client
        self.http_client.with_response_pattern(
            method=method,
            path_pattern=path_pattern,
            status_code=status_code,
            data=data,
            headers=headers,
            error=error
        )

    def with_network_condition(
        self,
        latency_ms: float = 0.0
    ) -> None:
        # Delegate to the underlying HTTP client
        self.http_client.with_network_condition(latency_ms=latency_ms)

    def set_auth_strategy(self, auth_strategy: AuthStrategy) -> None:
        self._auth_strategy = auth_strategy
        self.config.auth_strategy = auth_strategy

    def get_auth_strategy(self) -> Optional[AuthStrategy]:
        return self._auth_strategy

    def _record_request(
        self,
        method: HttpMethod,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
    ) -> None:
        self.request_history.append({
            'method': method,
            'path': path,
            'headers': headers or {},
            'params': params or {},
            'data': data,
            'kwargs': kwargs
        })

    # HTTP method implementations

    def get(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        **kwargs: Any
    ) -> Any:
        self._record_request('GET', path, headers, params, **kwargs)
        return self.http_client.get(path, headers=headers, params=params, **kwargs)

    def post(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
    ) -> Any:
        self._record_request('POST', path, headers, params, data, **kwargs)
        return self.http_client.post(path, headers=headers, params=params, data=data, **kwargs)

    def put(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
    ) -> Any:
        self._record_request('PUT', path, headers, params, data, **kwargs)
        return self.http_client.put(path, headers=headers, params=params, data=data, **kwargs)

    def delete(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        **kwargs: Any
    ) -> Any:
        self._record_request('DELETE', path, headers, params, **kwargs)
        return self.http_client.delete(path, headers=headers, params=params, **kwargs)

    def patch(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
    ) -> Any:
        self._record_request('PATCH', path, headers, params, data, **kwargs)
        return self.http_client.patch(path, headers=headers, params=params, data=data, **kwargs)

    # Verification methods

    def get_request_count(
        self,
        method: Optional[HttpMethod] = None,
        path_pattern: Optional[Union[str, Pattern]] = None
    ) -> int:
        return len(self._filter_requests(method, path_pattern))

    def assert_request_count(
        self,
        count: int,
        method: Optional[HttpMethod] = None,
        path_pattern: Optional[Union[str, Pattern]] = None
    ) -> None:
        actual_count = self.get_request_count(method, path_pattern)
        assert actual_count == count, (
            f"Expected {count} matching requests, but found {actual_count}. "
            f"Filters: method={method}, path_pattern={path_pattern}"
        )

    def assert_request_made(
        self,
        method: Optional[HttpMethod] = None,
        path_pattern: Optional[Union[str, Pattern]] = None
    ) -> None:
        actual_count = self.get_request_count(method, path_pattern)
        assert actual_count > 0, (
            f"Expected at least one matching request, but found none. "
            f"Filters: method={method}, path_pattern={path_pattern}"
        )

    def assert_request_not_made(
        self,
        method: Optional[HttpMethod] = None,
        path_pattern: Optional[Union[str, Pattern]] = None
    ) -> None:
        actual_count = self.get_request_count(method, path_pattern)
        assert actual_count == 0, (
            f"Expected no matching requests, but found {actual_count}. "
            f"Filters: method={method}, path_pattern={path_pattern}"
        )

    def _filter_requests(
        self,
        method: Optional[HttpMethod] = None,
        path_pattern: Optional[Union[str, Pattern]] = None
    ) -> List[Dict[str, Any]]:
        result = self.request_history

        if method:
            method = method.upper()
            result = [r for r in result if r['method'].upper() == method]

        if path_pattern:
            if isinstance(path_pattern, str):
                pattern = re.compile(path_pattern)
            else:
                pattern = path_pattern
            result = [r for r in result if pattern.search(r['path'])]

        return result

    def reset(self) -> None:
        self.request_history = []
        # Reset the HTTP client if it has a reset method
        if hasattr(self.http_client, 'reset'):
            self.http_client.reset()

import re
from typing import Any, Dict, List, Optional, Pattern, Union

from crudclient.auth.base import AuthStrategy
from crudclient.config import ClientConfig

# Import PaginationHelper
from ..response_builder.pagination import (
    PaginationResponseBuilder,  # Import the builder class
)
from ..response_builder.response import (
    MockResponse,  # Import MockResponse for type hint
)
from ..types import (
    Headers,
    HttpMethod,
    QueryParams,
    RequestBody,
    ResponseBody,
    StatusCode,
)


class MockClient:

    def __init__(
        self,
        http_client: Any,  # Expect MockHTTPClient or similar with base_url attribute
        base_url: Optional[str] = None,  # Re-introduce optional base_url parameter
        config: Optional[ClientConfig] = None,  # Accept optional config object
        enable_spy: bool = False,
        **kwargs: Any,  # Keep kwargs for potential future use or flexibility
    ) -> None:
        self.http_client = http_client
        # Prioritize explicit base_url, then derive from http_client, then default
        if base_url is not None:
            self.base_url = base_url
        else:
            self.base_url = getattr(http_client, "base_url", "https://api.example.com")  # Fallback if http_client lacks base_url
        self.enable_spy = enable_spy

        # Use provided config or create a default one based on derived base_url
        if config is not None:
            self.config = config
        else:
            # Ensure hostname matches the determined base_url if creating default config
            self.config = ClientConfig(hostname=self.base_url)

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
        error: Optional[Exception] = None,
    ) -> None:
        self.http_client.configure_response(method=method, path=path, status_code=status_code, data=data, headers=headers, error=error)

    def with_response_pattern(
        self,
        method: HttpMethod,
        path_pattern: Union[str, Pattern],
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None,
    ) -> None:
        # Delegate to the underlying HTTP client
        self.http_client.with_response_pattern(
            method=method, path_pattern=path_pattern, status_code=status_code, data=data, headers=headers, error=error
        )

    def with_network_condition(self, latency_ms: float = 0.0) -> None:
        # Delegate to the underlying HTTP client
        self.http_client.with_network_condition(latency_ms=latency_ms)

    def with_rate_limiter(self, limit: int, window_seconds: int) -> None:
        print(f"MockClient: Rate limiting configured (limit={limit}, window={window_seconds}s). Not enforced by this stub.")
        # Example of potential delegation:
        # if hasattr(self.http_client, 'with_rate_limiter'):
        #     self.http_client.with_rate_limiter(limit=limit, window_seconds=window_seconds)
        pass  # Add pass to make it a valid method

    def set_auth_strategy(self, auth_strategy: AuthStrategy) -> None:
        self._auth_strategy = auth_strategy
        self.config.auth_strategy = auth_strategy

    def get_auth_strategy(self) -> Optional[AuthStrategy]:
        return self._auth_strategy

    def _prepare_request_args(
        self,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
    ) -> Dict[str, Any]:
        final_headers = headers.copy() if headers else {}
        final_params = params.copy() if params else {}

        if self._auth_strategy:
            auth_headers = self._auth_strategy.prepare_request_headers()
            auth_params = self._auth_strategy.prepare_request_params()
            final_headers.update(auth_headers)
            final_params.update(auth_params)

        return {"headers": final_headers, "params": final_params}

    def _record_request(
        self,
        method: HttpMethod,
        path: str,
        headers: Optional[Headers] = None,  # These are the *final* headers after merge
        params: Optional[QueryParams] = None,  # These are the *final* params after merge
        data: Optional[RequestBody] = None,
        **kwargs: Any,
    ) -> None:
        # Record the state *after* auth strategy has been applied
        self.request_history.append(
            {
                "method": method,
                "path": path,
                "headers": headers.copy() if headers else {},  # Explicitly copy
                "params": params or {},
                "data": data,
                "kwargs": kwargs,  # kwargs passed directly to underlying client
            }
        )

    # HTTP method implementations

    def get(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Any:
        request_args = self._prepare_request_args(headers, params)
        self._record_request("GET", path, headers=request_args["headers"], params=request_args["params"], **kwargs)
        # Simulate rate limiting failure based on test case
        # Removed httpx import and specific rate limit simulation for this stub
        return self.http_client.get(path, **request_args, **kwargs)

    def post(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Any:
        request_args = self._prepare_request_args(headers, params)
        self._record_request("POST", path, headers=request_args["headers"], params=request_args["params"], data=data, **kwargs)
        return self.http_client.post(path, data=data, **request_args, **kwargs)

    def put(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Any:
        request_args = self._prepare_request_args(headers, params)
        self._record_request("PUT", path, headers=request_args["headers"], params=request_args["params"], data=data, **kwargs)
        return self.http_client.put(path, data=data, **request_args, **kwargs)

    def delete(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Any:
        request_args = self._prepare_request_args(headers, params)
        self._record_request("DELETE", path, headers=request_args["headers"], params=request_args["params"], **kwargs)
        return self.http_client.delete(path, **request_args, **kwargs)

    def patch(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Any:
        request_args = self._prepare_request_args(headers, params)
        self._record_request("PATCH", path, headers=request_args["headers"], params=request_args["params"], data=data, **kwargs)
        return self.http_client.patch(path, data=data, **request_args, **kwargs)

    # Verification methods

    def get_request_count(self, method: Optional[HttpMethod] = None, path_pattern: Optional[Union[str, Pattern]] = None) -> int:
        return len(self._filter_requests(method, path_pattern))

    def verify_request_count(self, count: int, method: Optional[HttpMethod] = None, path_pattern: Optional[Union[str, Pattern]] = None) -> None:
        actual_count = self.get_request_count(method, path_pattern)
        assert actual_count == count, (
            f"Expected {count} matching requests, but found {actual_count}. " f"Filters: method={method}, path_pattern={path_pattern}"
        )

    def verify_request_made(self, method: Optional[HttpMethod] = None, path_pattern: Optional[Union[str, Pattern]] = None) -> None:
        actual_count = self.get_request_count(method, path_pattern)
        assert actual_count > 0, f"Expected at least one matching request, but found none. " f"Filters: method={method}, path_pattern={path_pattern}"

    def verify_request_not_made(self, method: Optional[HttpMethod] = None, path_pattern: Optional[Union[str, Pattern]] = None) -> None:
        actual_count = self.get_request_count(method, path_pattern)
        assert actual_count == 0, (
            f"Expected no matching requests, but found {actual_count}. " f"Filters: method={method}, path_pattern={path_pattern}"
        )

    def verify_request_sequence(self, expected_sequence: List[Dict[str, Any]]) -> None:
        actual_count = len(self.request_history)
        expected_count = len(expected_sequence)
        assert actual_count == expected_count, f"Expected {expected_count} requests, but found {actual_count}."

        for i, expected in enumerate(expected_sequence):
            actual = self.request_history[i]
            # Basic check: compare methods if provided in expected sequence
            if "method" in expected:
                assert (
                    actual["method"].upper() == expected["method"].upper()
                ), f"Request {i + 1}: Expected method {expected['method']}, but got {actual['method']}."
            # Add more checks here as needed (e.g., path, params)
            # This is a basic stub; a full implementation might involve deep comparison
            # or delegate to a helper in crudclient.testing.verification

    def verify_request_params(
        self,
        expected_params: Dict[str, str],
        method: Optional[HttpMethod] = None,
        path_pattern: Optional[str] = None,
    ) -> None:
        matching_requests = self._filter_requests(method=method, path_pattern=path_pattern)

        found_match = False
        for request in matching_requests:
            # Simple subset check: are expected_params in actual params?
            actual_params = request.get("params", {})
            if expected_params.items() <= actual_params.items():
                found_match = True
                break

        assert found_match, f"Expected request with params {expected_params} not found. " f"Filters: method={method}, path_pattern={path_pattern}"

    def create_paginated_response(
        self,
        items: List[Any],
        per_page: int,
        base_url: str,
        page: int = 1,
    ) -> MockResponse:
        return PaginationResponseBuilder.create_paginated_response(
            items=items, page=page, per_page=per_page, base_url=base_url
        )

    def _filter_requests(self, method: Optional[HttpMethod] = None, path_pattern: Optional[Union[str, Pattern]] = None) -> List[Dict[str, Any]]:
        result = self.request_history

        if method:
            method = method.upper()
            result = [r for r in result if r["method"].upper() == method]

        if path_pattern:
            if isinstance(path_pattern, str):
                pattern = re.compile(path_pattern)
            else:
                pattern = path_pattern
            # Ensure path exists and is a string before matching
            result = [r for r in result if "path" in r and isinstance(r["path"], str) and pattern.search(r["path"])]

        return result

    def reset(self) -> None:
        self.request_history = []
        # Reset the HTTP client if it has a reset method
        if hasattr(self.http_client, "reset"):
            self.http_client.reset()

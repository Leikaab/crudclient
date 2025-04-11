from typing import Any, Dict, List, Optional, Union

from crudclient.testing.core.client import MockClient
from crudclient.testing.types import Headers


# Adapter class to provide backward compatibility with old mock client API
class BackwardCompatibleMockClient(MockClient):
    """
    Adapter class that provides backward compatibility with the old mock client API.

    This class adds methods like with_response_pattern, with_network_condition, etc.
    that were present in the old mock client API but are not in the new one.
    """

    def _handle_response_compat(self, response: Any) -> Any:
        """Handles response compatibility, raising AuthError or returning data."""
        # If the response is a dict, just return it directly (already handled?)
        if isinstance(response, dict):
            return response

        # If the response is a Response-like object (real or mock)
        if hasattr(response, 'status_code'):
            # If it's an auth error, raise an AuthenticationError
            if response.status_code in [401, 403]:
                error_data: Any = {}
                try:
                    # Use .json() method if available, else use text
                    if hasattr(response, 'json') and callable(response.json):
                        error_data = response.json() or {}
                    elif hasattr(response, 'text'):
                        error_data = {"error": response.text or "Authentication failed"}
                    else:
                        error_data = {"error": "Authentication failed"}
                except Exception:  # Catch potential JSON parsing errors
                    error_data = {"error": getattr(response, 'text', "Authentication failed")}

                # Ensure we're raising the correct exception
                from crudclient.exceptions import AuthenticationError
                raise AuthenticationError(f"{response.status_code} Unauthorized: Authentication failed: {error_data}", response)

            # For other successful responses, extract the data
            try:
                # Use .json() method if available
                if hasattr(response, 'json') and callable(response.json):
                    return response.json()
                elif hasattr(response, 'text'):
                    return response.text
                else:
                    return response  # Return as-is if no json/text method
            except Exception:  # Catch potential JSON parsing errors
                return getattr(response, 'text', response)  # Fallback to text or original response

        # If it's not a dict or Response-like, return as-is
        return response

    def get(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Any:
        """
        Make a mock GET request with backward compatible response handling.
        """
        response = super().get(path, headers=headers, params=params, **kwargs)
        return self._handle_response_compat(response)

    def post(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[Any], str, bytes, None]] = None,
        **kwargs: Any
    ) -> Any:
        """
        Make a mock POST request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            The response data directly, not a Response object.
        """
        response = super().post(path, headers=headers, params=params, data=data, **kwargs)
        return self._handle_response_compat(response)

    def put(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[Any], str, bytes, None]] = None,
        **kwargs: Any
    ) -> Any:
        """
        Make a mock PUT request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            The response data directly, not a Response object.
        """
        response = super().put(path, headers=headers, params=params, data=data, **kwargs)
        return self._handle_response_compat(response)

    def delete(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Any:
        """
        Make a mock DELETE request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            The response data directly, not a Response object.
        """
        response = super().delete(path, headers=headers, params=params, **kwargs)
        return self._handle_response_compat(response)

    def patch(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[Any], str, bytes, None]] = None,
        **kwargs: Any
    ) -> Any:
        """
        Make a mock PATCH request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            The response data directly, not a Response object.
        """
        response = super().patch(path, headers=headers, params=params, data=data, **kwargs)
        return self._handle_response_compat(response)

    def with_response_pattern(  # type: ignore[override]
        self,
        method: str,
        url_pattern: str,
        response: Union[Dict[str, Any], List[Dict[str, Any]], str, Dict[str, Any]],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None
    ) -> 'BackwardCompatibleMockClient':
        """
        Configure a response pattern for the mock client.

        Args:
            method: HTTP method to match
            url_pattern: URL pattern to match
            response: Response data to return
            status_code: HTTP status code to return
            headers: HTTP headers to return

        Returns:
            self for method chaining
        """
        # Correctly delegate to the underlying MockHTTPClient's method
        self.http_client.with_response_pattern(
            method=method,
            path_pattern=url_pattern,  # Use url_pattern as path_pattern
            status_code=status_code,
            data=response,  # Pass the raw response data
            headers=headers,
            error=None  # Assuming no error is configured here
        )
        return self

    def with_network_condition(  # type: ignore[override]
        self,
        condition: str,
        **kwargs: Any
    ) -> 'BackwardCompatibleMockClient':
        """
        Configure a network condition for the mock client.

        Args:
            condition: Network condition to simulate
            **kwargs: Additional parameters for the condition

        Returns:
            self for method chaining
        """
        # This is a stub implementation - in a real implementation,
        # we would configure the network condition based on the parameters
        return self

    def add_expected_failure(
        self,
        method: str,
        path: str,  # Should be relative path for MockClient
        status_code: int,
        response_body: Optional[Union[Dict[str, Any], List[Any], str]] = None,
        headers: Optional[Dict[str, str]] = None,
        expected_headers: Optional[Dict[str, str]] = None,  # Pass through header requirements
    ) -> None:
        """Adds an expected failure response, mapping to MockClient.add_response."""
        # Convert to the format MockClient expects for add_response
        # MockClient doesn't have a dedicated failure mechanism,
        # just responses with non-2xx status codes. We also need to handle
        # matching based on expected headers for the MFA retry case.
        # Use with_response_pattern instead of add_response
        if isinstance(response_body, (dict, list)):
            self.with_response_pattern(
                method=method,
                url_pattern=path,
                response=response_body,
                status_code=status_code,
                headers=headers
            )
        elif isinstance(response_body, str):
            # Handle string response bodies
            self.with_response_pattern(
                method=method,
                url_pattern=path,
                response=response_body,
                status_code=status_code,
                headers=headers
            )
        else:
            # Handle None or other types
            self.with_response_pattern(
                method=method,
                url_pattern=path,
                response={},  # Empty dict as default
                status_code=status_code,
                headers=headers
            )

    def with_rate_limiter(  # type: ignore[override]
        self,
        limit: int,
        window_seconds: int
    ) -> 'BackwardCompatibleMockClient':
        """
        Configure a rate limiter for the mock client.

        Args:
            limit: Number of requests allowed in the window
            window_seconds: Window size in seconds

        Returns:
            self for method chaining
        """
        # This is a stub implementation - in a real implementation,
        # we would configure the rate limiter based on the parameters
        return self

    def create_paginated_response(  # type: ignore[override]
        self,
        **kwargs: Any
    ) -> Any:
        """
        Create a paginated response.

        Args:
            **kwargs: Parameters for the paginated response

        Returns:
            A paginated response object
        """
        # This is a stub implementation - in a real implementation,
        # we would create a paginated response based on the parameters
        return {}

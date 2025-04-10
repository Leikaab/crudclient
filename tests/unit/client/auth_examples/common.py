"""
Common imports and utilities for authentication examples.
"""

from typing import Any, Dict, List, Optional, Union

from requests.auth import AuthBase
from crudclient.exceptions import AuthenticationError

from crudclient.testing.auth import create_api_key_auth_mock, create_basic_auth_mock, create_bearer_auth_mock, create_custom_auth_mock
from crudclient.testing.core.client import MockClient
from crudclient.testing.core.http_client import MockHTTPClient
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
        data: Optional[Dict[str, Any]] = None,
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
        data: Optional[Dict[str, Any]] = None,
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
        data: Optional[Dict[str, Any]] = None,
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


# Function for backward compatibility
def create_mock_client(**kwargs):
    """Create a mock client with the given configuration."""
    # Create a mock HTTP client
    base_url = kwargs.get('base_url', "https://api.example.com")
    http_client = MockHTTPClient(base_url=base_url)

    # Create a mock client with the mock HTTP client
    enable_spy = kwargs.get('enable_spy', False)
    mock_client = BackwardCompatibleMockClient(
        http_client=http_client,
        enable_spy=enable_spy
    )

    # Configure auth if specified
    if 'auth_type' in kwargs and 'auth_config' in kwargs:
        auth_type = kwargs['auth_type']
        auth_config = kwargs['auth_config']

        # Check if this is a failure scenario
        should_fail = auth_config.get('should_fail', False)
        failure_type = auth_config.get('failure_type', 'invalid_credentials')
        failure_message = auth_config.get('message', 'Authentication failed')

        # The should_fail logic previously here was incorrect.
        # Failure scenarios should be configured in the test itself by setting up
        # a 401/403 response using client.with_response_pattern or configure_response.
        # The BackwardCompatibleMockClient adapter will then correctly raise
        # AuthenticationError based on the response status code.

        # Configure the auth strategy
        if auth_type == "basic":
            basic_auth_mock = create_basic_auth_mock(
                username=auth_config.get('username', ''),
                password=auth_config.get('password', '')
            )
            mock_client.set_auth_strategy(basic_auth_mock.get_auth_strategy())
        elif auth_type == "bearer":
            bearer_auth_mock = create_bearer_auth_mock(
                token=auth_config.get('token', '')
            )
            mock_client.set_auth_strategy(bearer_auth_mock.get_auth_strategy())
        elif auth_type == "apikey":
            api_key_auth_mock = create_api_key_auth_mock(
                api_key=auth_config.get('api_key', ''),
                header_name=auth_config.get('header_name'),
                param_name=auth_config.get('param_name')
            )
            mock_client.set_auth_strategy(api_key_auth_mock.get_auth_strategy())
        elif auth_type == "custom":
            custom_auth_mock = create_custom_auth_mock(
                header_callback=auth_config.get('header_callback'),
                param_callback=auth_config.get('param_callback')
            )
            mock_client.set_auth_strategy(custom_auth_mock.get_auth_strategy())

    return mock_client


class MockMFAAuth(AuthBase):
    """
    Mock Multi-Factor Authentication strategy for testing.

    This class simulates a Multi-Factor Authentication flow where:
    1. Initial request fails with 401 and a WWW-Authenticate challenge
    2. Client code provides an MFA token
    3. Subsequent request with the token succeeds
    """

    def __init__(self) -> None:
        """Initialize the MFA auth strategy."""
        self.mfa_token: Optional[str] = None
        self.last_challenge: Optional[str] = None  # Store the last WWW-Authenticate header

    def __call__(self, r):
        """Required by requests.auth.AuthBase but not used in our testing."""
        return r

    def handle_response_sync(self, response, request) -> Optional[Any]:
        """Handles 401 responses to potentially trigger MFA flow."""
        self.last_challenge = response.headers.get("WWW-Authenticate")
        if response.status_code == 401 and self.last_challenge:
            # Simulate "user" providing the token based on the challenge
            if "mfa_token_required" in self.last_challenge:
                self.mfa_token = "mock-mfa-12345"  # Simulate getting the token
                # Re-prepare the original request with the MFA token
                # Add the MFA token header for the retry attempt
                new_headers = request.headers.copy() if request.headers else {}
                new_headers["X-MFA-Token"] = self.mfa_token  # Add the token
                # Create a new request object to retry
                # Use a generic approach to avoid import issues
                new_request = type(request)(
                    method=request.method,
                    url=str(request.url),  # Ensure URL is string
                    params=request.params,
                    json=getattr(request, 'json', None),  # Handle potential absence
                    data=getattr(request, 'data', None),  # Handle potential absence
                    headers=new_headers,
                    extensions=getattr(request, 'extensions', {}) or {},  # Preserve extensions
                )
                return new_request  # Signal to retry with this new request
        return None  # No retry needed

    def enrich_request_sync(self, request) -> Any:
        """Adds MFA token header if available."""
        # This might be called before the *first* request too,
        # but handle_response_sync sets the token *after* the first failure.
        # The retry mechanism should use the request returned by handle_response_sync.
        if self.mfa_token:
            # Ensure headers exist and are mutable (or create new request)
            if hasattr(request, 'headers') and isinstance(request.headers, dict):
                request.headers["X-MFA-Token"] = self.mfa_token
            else:
                # This case indicates an incompatible Request object or missing headers attribute
                pass  # Or raise TypeError("Request headers are not a mutable dict")
        return request

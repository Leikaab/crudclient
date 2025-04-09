"""
Common imports and utilities for authentication examples.
"""

from typing import Any, Dict, List, Optional, Union

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

    def get(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Any:
        """
        Make a mock GET request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            The response data directly, not a Response object.
        """
        response = super().get(path, headers=headers, params=params, **kwargs)

        # If the response is a dict, just return it directly
        if isinstance(response, dict):
            return response

        # If the response is a Response object
        if hasattr(response, 'status_code'):
            # If it's an auth error, raise an AuthenticationError
            if response.status_code in [401, 403]:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": "Authentication failed"}

                # Include 401 and Unauthorized in the error message
                status_code = response.status_code
                raise AuthenticationError(f"401 Unauthorized: Authentication failed: {error_data}")

            # For other responses, extract the data
            try:
                return response.json()
            except:
                return response.text

        return response

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

        # If the response is a dict, just return it directly
        if isinstance(response, dict):
            return response

        # If the response is a Response object
        if hasattr(response, 'status_code'):
            # If it's an auth error, raise an AuthenticationError
            if response.status_code in [401, 403]:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": "Authentication failed"}

                # Include 401 and Unauthorized in the error message
                status_code = response.status_code
                raise AuthenticationError(f"401 Unauthorized: Authentication failed: {error_data}")

            # For other responses, extract the data
            try:
                return response.json()
            except:
                return response.text

        return response

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

        # If the response is a dict, just return it directly
        if isinstance(response, dict):
            return response

        # If the response is a Response object
        if hasattr(response, 'status_code'):
            # If it's an auth error, raise an AuthenticationError
            if response.status_code in [401, 403]:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": "Authentication failed"}

                # Include 401 and Unauthorized in the error message
                status_code = response.status_code
                raise AuthenticationError(f"401 Unauthorized: Authentication failed: {error_data}")

            # For other responses, extract the data
            try:
                return response.json()
            except:
                return response.text

        return response

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

        # If the response is a dict, just return it directly
        if isinstance(response, dict):
            return response

        # If the response is a Response object
        if hasattr(response, 'status_code'):
            # If it's an auth error, raise an AuthenticationError
            if response.status_code in [401, 403]:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": "Authentication failed"}

                # Include 401 and Unauthorized in the error message
                status_code = response.status_code
                raise AuthenticationError(f"401 Unauthorized: Authentication failed: {error_data}")

            # For other responses, extract the data
            try:
                return response.json()
            except:
                return response.text

        return response

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

        # If the response is a dict, just return it directly
        if isinstance(response, dict):
            return response

        # If the response is a Response object
        if hasattr(response, 'status_code'):
            # If it's an auth error, raise an AuthenticationError
            if response.status_code in [401, 403]:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": "Authentication failed"}

                # Include 401 and Unauthorized in the error message
                status_code = response.status_code
                raise AuthenticationError(f"401 Unauthorized: Authentication failed: {error_data}")

            # For other responses, extract the data
            try:
                return response.json()
            except:
                return response.text

        return response

    def with_response_pattern(
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
        # Check if response is a dict with specific keys that indicate it's a response object
        if isinstance(response, dict) and any(key in response for key in ['status_code', 'json_data', 'headers']):
            # It's already a response object, extract the components
            response_status_code = response.get('status_code', status_code)
            response_data = response.get('json_data', {})
            response_headers = response.get('headers', headers)
        else:
            # It's just the response data
            response_status_code = status_code
            response_data = response
            response_headers = headers

        # Configure the HTTP client to return the response directly
        # This is a workaround for the issue with the Response object
        def mock_response(*args, **kwargs):
            return response_data

        # Override the HTTP method to return the response directly
        if method.upper() == 'GET':
            self.http_client.get = mock_response
        elif method.upper() == 'POST':
            self.http_client.post = mock_response
        elif method.upper() == 'PUT':
            self.http_client.put = mock_response
        elif method.upper() == 'DELETE':
            self.http_client.delete = mock_response
        elif method.upper() == 'PATCH':
            self.http_client.patch = mock_response

        return self

    def with_network_condition(
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

    def with_rate_limiter(
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

    def create_paginated_response(
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

        if should_fail:
            # For failure scenarios, we need to configure the client to raise an exception
            # with the specific error message

            # Create a function that raises an AuthenticationError with the specific message
            def raise_auth_error(*args, **kwargs):
                error_data = {"error": failure_message}
                raise AuthenticationError(f"401 Unauthorized: {failure_message}")

            # Override the HTTP methods to raise the exception
            http_client.get = raise_auth_error
            http_client.post = raise_auth_error
            http_client.put = raise_auth_error
            http_client.delete = raise_auth_error
            http_client.patch = raise_auth_error

        # Configure the auth strategy
        if auth_type == "basic":
            auth_mock = create_basic_auth_mock(
                username=auth_config.get('username', ''),
                password=auth_config.get('password', '')
            )
            mock_client.set_auth_strategy(auth_mock.get_auth_strategy())
        elif auth_type == "bearer":
            auth_mock = create_bearer_auth_mock(
                token=auth_config.get('token', '')
            )
            mock_client.set_auth_strategy(auth_mock.get_auth_strategy())
        elif auth_type == "apikey":
            auth_mock = create_api_key_auth_mock(
                api_key=auth_config.get('api_key', ''),
                header_name=auth_config.get('header_name'),
                param_name=auth_config.get('param_name')
            )
            mock_client.set_auth_strategy(auth_mock.get_auth_strategy())
        elif auth_type == "custom":
            auth_mock = create_custom_auth_mock(
                header_callback=auth_config.get('header_callback'),
                param_callback=auth_config.get('param_callback')
            )
            mock_client.set_auth_strategy(auth_mock.get_auth_strategy())

    return mock_client

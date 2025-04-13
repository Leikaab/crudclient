"""
Helper functions for asserting conditions on CRUD mock requests.

This module provides utility functions for checking request payloads,
operation parameters, response handling, and error handling in CRUD mock tests.
"""

from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from crudclient.testing.response_builder.response import MockResponse

# Define a Request class that represents the structure of request objects
# stored in request_history

class Request:
    """
    Represents a request made to a mock API.

    This class defines the structure of request objects stored in
    the request_history of CRUD mocks.
    """

    url: str
    """The URL of the request"""

    method: str
    """The HTTP method of the request (GET, POST, PUT, PATCH, DELETE)"""

    params: Optional[Dict[str, Any]]
    """Query parameters sent with the request"""

    data: Optional[Dict[str, Any]]
    """Form data sent with the request"""

    json: Optional[Dict[str, Any]]
    """JSON data sent with the request"""

    response: MockResponse
    """The response returned for this request"""

def check_request_payload(
    requests: List[Request],
    payload: Dict[str, Any],
    url_pattern: Optional[str],
    match_all: bool,
) -> None:
    """
    Check that requests were made with a specific payload.

    Args:
        requests: List of requests to check
        payload: Expected payload (key-value pairs)
        url_pattern: URL pattern used to filter the requests (for error messages)
        match_all: If True, all requests must have the payload; otherwise, at least one must match

    Raises:
        AssertionError: If no matching request has the expected payload
    """
    ...

def check_operation_parameters(
    requests: List[Request],
    expected_params: Dict[str, Any],
    url_pattern: str,
    method: Optional[str],
) -> None:
    """
    Check that operations were called with specific parameters.

    Args:
        requests: List of requests to check
        expected_params: Expected parameters (can be in params, data, or json)
        url_pattern: URL pattern used to filter the requests (for error messages)
        method: HTTP method used to filter the requests (for error messages)

    Raises:
        AssertionError: If no matching requests or parameters don't match
    """
    ...

def check_response_handling(
    requests: List[Request],
    expected_status: int,
    expected_data: Optional[Dict[str, Any]],
    url_pattern: str,
    method: Optional[str],
) -> None:
    """
    Check that responses were handled correctly.

    Args:
        requests: List of requests to check
        expected_status: Expected HTTP status code
        expected_data: Expected response data (optional)
        url_pattern: URL pattern used to filter the requests (for error messages)
        method: HTTP method used to filter the requests (for error messages)

    Raises:
        AssertionError: If no matching requests or responses don't match
    """
    ...

def check_error_handling(
    requests: List[Request],
    expected_error_type: Type[Exception],
    expected_status: Optional[int],
    url_pattern: str,
    method: Optional[str],
) -> bool:
    """
    Check that errors were handled correctly.

    Args:
        requests: List of requests to check
        expected_error_type: Expected exception type
        expected_status: Expected HTTP status code (optional)
        url_pattern: URL pattern used to filter the requests (for error messages)
        method: HTTP method used to filter the requests (for error messages)

    Returns:
        True if a matching error was found in the request history, False otherwise

    Raises:
        AssertionError: If no matching requests or errors don't match
    """
    ...

def check_query_parameters(
    requests: List[Request],
    expected_params: Dict[str, Any],
    url_pattern: str,
    method: Optional[str],
) -> None:
    """
    Checks if at least one matching request contains the expected query parameters.

    Args:
        requests: List of requests to check
        expected_params: Expected query parameters
        url_pattern: URL pattern used to filter the requests (for error messages)
        method: HTTP method used to filter the requests (for error messages)

    Raises:
        AssertionError: If no matching requests or parameters don't match
    """
    ...

def check_body_parameters(
    requests: List[Request],
    expected_params: Dict[str, Any],
    url_pattern: str,
    method: Optional[str],
) -> None:
    """
    Checks if at least one matching request contains the expected body (data or json) parameters.

    Args:
        requests: List of requests to check
        expected_params: Expected body parameters
        url_pattern: URL pattern used to filter the requests (for error messages)
        method: HTTP method used to filter the requests (for error messages)

    Raises:
        AssertionError: If no matching requests or parameters don't match
    """
    ...

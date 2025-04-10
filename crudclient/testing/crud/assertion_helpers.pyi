from typing import Any, Callable, Dict, List, Optional, Type

from crudclient.testing.response_builder.response import MockResponse

# Placeholder for the actual Request object type
# TODO: Replace 'Any' with the actual Request type if available
Request = Any


def check_request_payload(
    requests: List[Request],
    payload: Dict[str, Any],
    url_pattern: Optional[str],
    match_all: bool,
) -> None:
    """
    Asserts that requests contain the specified payload.

    Args:
        requests: List of filtered request objects to check.
        payload: Expected payload dictionary. Values can be literals or callables for validation.
        url_pattern: The URL pattern used for filtering (for error messages).
        match_all: If True, all requests must match. If False, at least one must match.

    Raises:
        AssertionError: If the payload assertion fails.
    """
    ...


def check_operation_parameters(
    requests: List[Request],
    expected_params: Dict[str, Any],
    url_pattern: str,
    method: Optional[str],
) -> None:
    """
    Asserts that requests contain the specified parameters in params, data, or json.

    Args:
        requests: List of filtered request objects to check.
        expected_params: Dictionary of expected parameter key-value pairs.
        url_pattern: The URL pattern used for filtering (for error messages).
        method: The HTTP method used for filtering (for error messages).

    Raises:
        AssertionError: If the parameter assertion fails.
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
    Asserts that requests resulted in responses with the expected status and data.

    Args:
        requests: List of filtered request objects to check.
        expected_status: The expected HTTP status code.
        expected_data: Optional dictionary of expected key-value pairs in the response JSON.
        url_pattern: The URL pattern used for filtering (for error messages).
        method: The HTTP method used for filtering (for error messages).

    Raises:
        AssertionError: If the response assertion fails.
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
    Checks if the expected error was handled correctly in the request history.

    Args:
        requests: List of filtered request objects to check.
        expected_error_type: The expected type of exception.
        expected_status: The expected HTTP status code associated with the error (optional).
        url_pattern: The URL pattern used for filtering (for error messages).
        method: The HTTP method used for filtering (for error messages).

    Returns:
        True if a matching error was found in the request history, False otherwise.

    Raises:
        AssertionError: If an error is found but its type or status code doesn't match.
    """
    ...

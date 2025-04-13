"""
Simple mock client core functionality for testing.

This module provides the core functionality for the SimpleMockClient, a lightweight
mock client implementation that doesn't inherit from the real Client class.
This approach avoids the complexities of the real HTTP client while providing
a simple interface for testing.
"""

from typing import Any, Callable, Dict, List, Union

from crudclient.testing.crud.request_record import RequestRecord
from crudclient.testing.response_builder.response import MockResponse

class SimpleMockClientCore:
    """
    A simple mock client that doesn't inherit from the real Client class.

    This implementation avoids all the complexities of the real HTTP client
    while providing a simple interface for testing API interactions. It allows
    configuring response patterns based on request characteristics and maintains
    a history of all requests for verification.
    """

    response_patterns: List[Dict[str, Any]]
    request_history: List[RequestRecord]
    default_response: MockResponse

    def __init__(self) -> None:
        """
        Initialize the simple mock client.

        Sets up empty response patterns and request history, and configures
        a default 404 response for unmatched requests.
        """
        ...

    def with_response_pattern(
        self, method: str, url_pattern: str, response: Union[MockResponse, Dict[str, Any], str, Callable[..., MockResponse]], **kwargs: Any
    ) -> "SimpleMockClientCore":
        """
        Add a response pattern to the mock client.

        This method configures how the mock client should respond to specific
        request patterns. It supports various response formats and can match
        requests based on method, URL pattern, and other request attributes.

        Args:
            method: HTTP method to match (e.g., GET, POST)
            url_pattern: Regex pattern to match request URLs
            response: Response to return (MockResponse, dict, string, or callable)
            **kwargs: Additional request attributes to match (params, data, json, headers)
                     and configuration options like max_calls

        Returns:
            The mock client instance for method chaining
        """
        ...

    def with_default_response(self, response: Union[MockResponse, Dict[str, Any], str]) -> "SimpleMockClientCore":
        """
        Set the default response for unmatched requests.

        This response will be used when no configured pattern matches
        the incoming request.

        Args:
            response: Default response to return (MockResponse, dict, or string)

        Returns:
            The mock client instance for method chaining
        """
        ...

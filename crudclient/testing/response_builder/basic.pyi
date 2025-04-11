"""
Basic response builder utilities for mock client.

This module provides utilities for building basic API responses with structured data,
nested structures, and GraphQL format. These utilities help create consistent and
realistic mock responses for testing API interactions.
"""

from typing import Any, Dict, List, Optional

from .response import MockResponse

class BasicResponseBuilder:
    """
    Builder for creating basic API responses.

    This class provides static methods for creating various types of API responses
    with structured data, including responses with metadata, links, and nested
    structures. It also supports GraphQL-specific response formats.
    """

    @staticmethod
    def create_response(
        status_code: int = 200,
        data: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
        """
        Create a mock response with structured data.

        This method creates a response with a standardized structure that includes
        data, metadata, links, and errors sections, following common API design patterns.

        Args:
            status_code: HTTP status code for the response
            data: Primary response data
            metadata: Response metadata such as pagination info or timestamps
            links: HATEOAS links for resource navigation
            errors: Error details if the response represents an error
            headers: HTTP headers to include in the response

        Returns:
            A MockResponse instance with the specified structure and content
        """
        ...

    @staticmethod
    def create_nested_response(
        structure: Dict[str, Any],
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
        """
        Create a response with a nested structure.

        This method allows for creating responses with arbitrary nested structures,
        which is useful for testing APIs that return complex, deeply nested JSON.

        Args:
            structure: Nested structure for the response body
            status_code: HTTP status code for the response
            headers: HTTP headers to include in the response

        Returns:
            A MockResponse instance with the specified nested structure
        """
        ...

    @staticmethod
    def create_graphql_response(
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        extensions: Optional[Dict[str, Any]] = None,
    ) -> MockResponse:
        """
        Create a GraphQL response.

        This method creates responses that follow the GraphQL specification format,
        which includes data, errors, and extensions sections.

        Args:
            data: GraphQL data response containing the requested fields
            errors: GraphQL errors if any occurred during execution
            extensions: GraphQL extensions for additional metadata

        Returns:
            A MockResponse instance formatted according to GraphQL specification
        """
        ...

    @staticmethod
    def created(
        data: Any,
        location: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
        """
        Creates a 201 Created response.

        Args:
            data: Primary response data
            location: Location header value for the created resource
            metadata: Response metadata
            links: HATEOAS links for resource navigation
            headers: Additional HTTP headers

        Returns:
            A MockResponse with 201 status code and the specified data
        """
        ...

    @staticmethod
    def no_content(headers: Optional[Dict[str, str]] = None) -> MockResponse:
        """
        Creates a 204 No Content response.

        Args:
            headers: HTTP headers to include in the response

        Returns:
            A MockResponse with 204 status code and no content
        """
        ...

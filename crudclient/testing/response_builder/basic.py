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
        response_body: Dict[str, Any] = {}

        if data is not None:
            response_body["data"] = data

        if metadata is not None:
            response_body["metadata"] = metadata

        if links is not None:
            response_body["links"] = links

        if errors is not None:
            response_body["errors"] = errors

        return MockResponse(
            status_code=status_code,
            json_data=response_body,
            headers=headers or {"Content-Type": "application/json"}
        )

    @staticmethod
    def create_nested_response(
        structure: Dict[str, Any],
        status_code: int = 200,
    ) -> MockResponse:
        """
        Create a response with a nested structure.

        This method allows for creating responses with arbitrary nested structures,
        which is useful for testing APIs that return complex, deeply nested JSON.

        Args:
            structure: Nested structure for the response body
            status_code: HTTP status code for the response

        Returns:
            A MockResponse instance with the specified nested structure
        """
        return MockResponse(
            status_code=status_code,
            json_data=structure,
            headers={"Content-Type": "application/json"}
        )

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
        response_body: Dict[str, Any] = {}

        if data is not None:
            response_body["data"] = data

        if errors is not None:
            response_body["errors"] = errors

        if extensions is not None:
            response_body["extensions"] = extensions

        return MockResponse(
            status_code=200 if not errors else 400,
            json_data=response_body,
            headers={"Content-Type": "application/json"}
        )

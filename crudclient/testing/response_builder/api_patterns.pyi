"""
API pattern builder utilities for mock client.

This module provides utilities for creating mock responses that follow common API patterns,
such as REST resources, nested resources, batch operations, GraphQL endpoints, and OAuth flows.
"""

from typing import Any, Callable, Dict, List, Optional, Union

from .response import MockResponse

class APIPatternBuilder:
    """
    Builder for creating mock responses that follow common API patterns.

    This class provides static methods for generating response patterns that match
    common API design patterns, making it easier to create realistic mock APIs
    for testing client code.
    """

    @staticmethod
    def rest_resource(
        base_path: str,
        resource_id_pattern: str = r"\d+",
        list_response: Optional[Union[List[Dict[str, Any]], Callable[..., MockResponse]]] = None,
        get_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        create_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        update_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        delete_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        search_response: Optional[Union[List[Dict[str, Any]], Callable[..., MockResponse]]] = None,
        filter_response: Optional[Union[List[Dict[str, Any]], Callable[..., MockResponse]]] = None,
        patch_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create response patterns for a standard REST resource.

        This method generates response patterns for standard REST operations
        (list, get, create, update, delete) on a resource, as well as search
        and filter operations.

        Args:
            base_path: The base URL path for the resource (e.g., "users")
            resource_id_pattern: Regex pattern to match resource IDs in URLs
            list_response: Response for GET requests to the collection (list operation)
            get_response: Response for GET requests to a specific resource
            create_response: Response for POST requests to the collection (create operation)
            update_response: Response for PUT requests to a specific resource
            delete_response: Response for DELETE requests to a specific resource
            search_response: Response for GET requests with a search parameter
            filter_response: Response for GET requests with filter parameters
            patch_response: Response for PATCH requests to a specific resource

        Returns:
            A list of response pattern dictionaries that can be used with a mock client
        """
        ...

    @staticmethod
    def nested_resource(
        parent_path: str,
        child_path: str,
        parent_id_pattern: str = r"\d+",
        child_id_pattern: str = r"\d+",
        list_response: Optional[Union[List[Dict[str, Any]], Callable[..., MockResponse]]] = None,
        get_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        create_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        update_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        delete_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create response patterns for a nested resource.

        This method generates response patterns for operations on a resource that is
        nested under a parent resource (e.g., /users/{user_id}/posts/{post_id}).

        Args:
            parent_path: The path of the parent resource (e.g., "users")
            child_path: The path of the child resource (e.g., "posts")
            parent_id_pattern: Regex pattern to match parent resource IDs
            child_id_pattern: Regex pattern to match child resource IDs
            list_response: Response for GET requests to the child collection
            get_response: Response for GET requests to a specific child resource
            create_response: Response for POST requests to the child collection
            update_response: Response for PUT requests to a specific child resource
            delete_response: Response for DELETE requests to a specific child resource

        Returns:
            A list of response pattern dictionaries that can be used with a mock client
        """
        ...

    @staticmethod
    def batch_operations(
        base_path: str,
        batch_create_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        batch_update_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        batch_delete_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create response patterns for batch operations.

        This method generates response patterns for batch operations (create, update, delete)
        on a resource, which are commonly used for bulk operations.

        Args:
            base_path: The base URL path for the resource (e.g., "users")
            batch_create_response: Response for batch create operations
            batch_update_response: Response for batch update operations
            batch_delete_response: Response for batch delete operations

        Returns:
            A list of response pattern dictionaries that can be used with a mock client
        """
        ...

    @staticmethod
    def graphql_endpoint(
        url_pattern: str = r"/graphql$",
        query_matchers: Optional[Dict[str, Union[Dict[str, Any], Callable[..., MockResponse]]]] = None,
        default_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create response patterns for a GraphQL endpoint.

        This method generates response patterns for a GraphQL endpoint, with support
        for matching specific queries and providing appropriate responses.

        Args:
            url_pattern: Regex pattern to match the GraphQL endpoint URL
            query_matchers: Dictionary mapping query patterns to responses
            default_response: Default response for queries that don't match any pattern

        Returns:
            A list of response pattern dictionaries that can be used with a mock client
        """
        ...

    @staticmethod
    def oauth_flow(
        token_url_pattern: str = r"/oauth/token$",
        success_response: Optional[Dict[str, Any]] = None,
        error_response: Optional[Dict[str, Any]] = None,
        valid_credentials: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create response patterns for an OAuth token endpoint.

        This method generates response patterns for an OAuth token endpoint,
        with support for validating credentials and returning appropriate
        success or error responses.

        Args:
            token_url_pattern: Regex pattern to match the token endpoint URL
            success_response: Response to return for valid credentials
            error_response: Response to return for invalid credentials
            valid_credentials: Dictionary of valid credentials to check against

        Returns:
            A list of response pattern dictionaries that can be used with a mock client
        """
        ...

"""
API patterns for mock client response configuration.

This module provides pre-configured patterns for common API types like REST and GraphQL.
These patterns can be used to quickly set up mock responses for different API architectures
without having to manually configure each endpoint.
"""

from typing import Any, Callable, Dict, List, Optional, Union, Tuple

from .response import MockResponse


class APIPatternBuilder:
    """
    Builder for creating common API response patterns.

    This class provides static methods to generate response patterns for various
    API architectures including REST resources, nested resources, batch operations,
    GraphQL endpoints, and OAuth flows. These patterns can be used to configure
    mock clients with realistic API behavior.
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
        Create patterns for a REST resource with standard CRUD operations.

        This method generates response patterns for standard REST operations including
        list, get, create, update, delete, search, filter, and patch. Each operation
        can be configured with a specific response or response factory.

        Args:
            base_path: Base path for the resource (e.g., "/users")
            resource_id_pattern: Regex pattern for resource IDs
            list_response: Response for list operation (GET on collection)
            get_response: Response for get operation (GET on resource)
            create_response: Response for create operation (POST on collection)
            update_response: Response for update operation (PUT on resource)
            delete_response: Response for delete operation (DELETE on resource)
            search_response: Response for search operation (GET with search params)
            filter_response: Response for filter operation (GET with filter params)
            patch_response: Response for partial update operation (PATCH on resource)

        Returns:
            List of response patterns for the resource that can be used to configure
            a mock client.
        """
        patterns = []

        # Ensure base_path starts with / and doesn't end with /
        base_path = f"/{base_path.strip('/')}"

        # GET collection (list)
        if list_response is not None:
            patterns.append({
                "method": "GET",
                "url_pattern": f"{base_path}$",
                "response": list_response
            })

        # GET resource (read)
        if get_response is not None:
            patterns.append({
                "method": "GET",
                "url_pattern": f"{base_path}/{resource_id_pattern}$",
                "response": get_response
            })

        # POST collection (create)
        if create_response is not None:
            patterns.append({
                "method": "POST",
                "url_pattern": f"{base_path}$",
                "response": create_response
            })

        # PUT resource (update)
        if update_response is not None:
            patterns.append({
                "method": "PUT",
                "url_pattern": f"{base_path}/{resource_id_pattern}$",
                "response": update_response
            })

        # PATCH resource (partial update)
        if patch_response is not None:
            patterns.append({
                "method": "PATCH",
                "url_pattern": f"{base_path}/{resource_id_pattern}$",
                "response": patch_response
            })

        # DELETE resource (delete)
        if delete_response is not None:
            patterns.append({
                "method": "DELETE",
                "url_pattern": f"{base_path}/{resource_id_pattern}$",
                "response": delete_response
            })

        # GET collection with search (search)
        if search_response is not None:
            patterns.append({
                "method": "GET",
                "url_pattern": f"{base_path}$",
                "params_matcher": lambda params: params and "search" in params,
                "response": search_response
            })

        # GET collection with filters (filter)
        if filter_response is not None:
            patterns.append({
                "method": "GET",
                "url_pattern": f"{base_path}$",
                "params_matcher": lambda params: params and any(
                    key != "search" and key != "page" and key != "limit"
                    for key in params.keys()
                ),
                "response": filter_response
            })

        return patterns

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
        Create patterns for a nested REST resource (e.g., /users/{id}/posts).

        This method generates response patterns for nested resources, which are common
        in RESTful APIs for representing hierarchical relationships between resources.

        Args:
            parent_path: Base path for the parent resource (e.g., "users")
            child_path: Base path for the child resource (e.g., "posts")
            parent_id_pattern: Regex pattern for parent resource IDs
            child_id_pattern: Regex pattern for child resource IDs
            list_response: Response for list operation (GET on child collection)
            get_response: Response for get operation (GET on child resource)
            create_response: Response for create operation (POST on child collection)
            update_response: Response for update operation (PUT on child resource)
            delete_response: Response for delete operation (DELETE on child resource)

        Returns:
            List of response patterns for the nested resource that can be used to
            configure a mock client.
        """
        patterns = []

        # Ensure paths are properly formatted
        parent_path = parent_path.strip('/')
        child_path = child_path.strip('/')
        base_path = f"/{parent_path}/{parent_id_pattern}/{child_path}"

        # GET child collection (list)
        if list_response is not None:
            patterns.append({
                "method": "GET",
                "url_pattern": f"{base_path}$",
                "response": list_response
            })

        # GET child resource (read)
        if get_response is not None:
            patterns.append({
                "method": "GET",
                "url_pattern": f"{base_path}/{child_id_pattern}$",
                "response": get_response
            })

        # POST child collection (create)
        if create_response is not None:
            patterns.append({
                "method": "POST",
                "url_pattern": f"{base_path}$",
                "response": create_response
            })

        # PUT child resource (update)
        if update_response is not None:
            patterns.append({
                "method": "PUT",
                "url_pattern": f"{base_path}/{child_id_pattern}$",
                "response": update_response
            })

        # DELETE child resource (delete)
        if delete_response is not None:
            patterns.append({
                "method": "DELETE",
                "url_pattern": f"{base_path}/{child_id_pattern}$",
                "response": delete_response
            })

        return patterns

    @staticmethod
    def batch_operations(
        base_path: str,
        batch_create_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        batch_update_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        batch_delete_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create patterns for batch operations on a resource.

        This method generates response patterns for batch operations, which allow
        clients to perform operations on multiple resources in a single request.

        Args:
            base_path: Base path for the resource (e.g., "/users")
            batch_create_response: Response for batch create operation
            batch_update_response: Response for batch update operation
            batch_delete_response: Response for batch delete operation

        Returns:
            List of response patterns for batch operations that can be used to
            configure a mock client.
        """
        patterns = []

        # Ensure base_path starts with / and doesn't end with /
        base_path = f"/{base_path.strip('/')}"
        batch_path = f"{base_path}/batch"

        # POST batch create
        if batch_create_response is not None:
            patterns.append({
                "method": "POST",
                "url_pattern": f"{batch_path}/create$",
                "response": batch_create_response
            })

        # PUT/PATCH batch update
        if batch_update_response is not None:
            patterns.append({
                "method": "PUT",
                "url_pattern": f"{batch_path}/update$",
                "response": batch_update_response
            })
            patterns.append({
                "method": "PATCH",
                "url_pattern": f"{batch_path}/update$",
                "response": batch_update_response
            })

        # DELETE batch delete
        if batch_delete_response is not None:
            patterns.append({
                "method": "POST",  # Often POST with IDs in body for batch delete
                "url_pattern": f"{batch_path}/delete$",
                "response": batch_delete_response
            })

        return patterns

    @staticmethod
    def graphql_endpoint(
        url_pattern: str = r"/graphql$",
        query_matchers: Optional[Dict[str, Union[Dict[str, Any], Callable[..., MockResponse]]]] = None,
        default_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create patterns for a GraphQL endpoint.

        This method generates response patterns for GraphQL endpoints, allowing
        different responses based on the query content.

        Args:
            url_pattern: Regex pattern for the GraphQL endpoint
            query_matchers: Dict mapping query patterns to responses
            default_response: Default response for unmatched queries

        Returns:
            List of response patterns for the GraphQL endpoint that can be used to
            configure a mock client.
        """
        patterns = []

        # Add patterns for specific queries
        if query_matchers:
            for query_pattern, response in query_matchers.items():
                patterns.append({
                    "method": "POST",
                    "url_pattern": url_pattern,
                    "json_matcher": lambda json_data, pattern=query_pattern: (
                        isinstance(json_data, dict)
                        and "query" in json_data
                        and pattern in json_data["query"]
                    ),
                    "response": response
                })

        # Add default response for unmatched queries
        if default_response is not None:
            patterns.append({
                "method": "POST",
                "url_pattern": url_pattern,
                "response": default_response
            })

        return patterns

    @staticmethod
    def oauth_flow(
        token_url_pattern: str = r"/oauth/token$",
        success_response: Optional[Dict[str, Any]] = None,
        error_response: Optional[Dict[str, Any]] = None,
        valid_credentials: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create patterns for an OAuth 2.0 flow.

        This method generates response patterns for OAuth 2.0 authentication flows,
        including token requests and responses.

        Args:
            token_url_pattern: Regex pattern for the token endpoint
            success_response: Response for successful token requests
            error_response: Response for failed token requests
            valid_credentials: Dict of valid credentials for authentication

        Returns:
            List of response patterns for the OAuth flow that can be used to
            configure a mock client.
        """
        if success_response is None:
            success_response = {
                "access_token": "mock-access-token",
                "token_type": "bearer",
                "expires_in": 3600,
                "refresh_token": "mock-refresh-token",
                "scope": "read write"
            }

        if error_response is None:
            error_response = {
                "error": "invalid_grant",
                "error_description": "Invalid credentials"
            }

        if valid_credentials is None:
            valid_credentials = {
                "client_id": "valid-client-id",
                "client_secret": "valid-client-secret"
            }

        def token_response_factory(**kwargs):
            data = kwargs.get('data', {})

            # Check if credentials match
            for key, value in valid_credentials.items():
                if key not in data or data[key] != value:
                    return MockResponse(status_code=401, json_data=error_response)

            return MockResponse(status_code=200, json_data=success_response)

        patterns = [
            {
                "method": "POST",
                "url_pattern": token_url_pattern,
                "response": token_response_factory
            }
        ]

        return patterns

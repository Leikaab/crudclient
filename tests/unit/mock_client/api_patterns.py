"""
API patterns for mock client.

This module provides pre-configured patterns for common API types like REST and GraphQL.
"""

from typing import Any, Dict, List, Optional, Union, Callable

from .response import MockResponse


class APIPatternBuilder:
    """Builder for creating common API patterns."""

    @staticmethod
    def rest_resource(
        base_path: str,
        resource_id_pattern: str = r"\d+",
        list_response: Optional[Union[List[Dict[str, Any]], Callable[..., MockResponse]]] = None,
        get_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        create_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        update_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
        delete_response: Optional[Union[Dict[str, Any], Callable[..., MockResponse]]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Create patterns for a REST resource with standard CRUD operations.

        Args:
            base_path: Base path for the resource (e.g., "/users")
            resource_id_pattern: Regex pattern for resource IDs
            list_response: Response for list operation (GET on collection)
            get_response: Response for get operation (GET on resource)
            create_response: Response for create operation (POST on collection)
            update_response: Response for update operation (PUT on resource)
            delete_response: Response for delete operation (DELETE on resource)

        Returns:
            List of response patterns for the resource
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

        # DELETE resource (delete)
        if delete_response is not None:
            patterns.append({
                "method": "DELETE",
                "url_pattern": f"{base_path}/{resource_id_pattern}$",
                "response": delete_response
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

        Args:
            url_pattern: Regex pattern for the GraphQL endpoint
            query_matchers: Dict mapping query patterns to responses
            default_response: Default response for unmatched queries

        Returns:
            List of response patterns for the GraphQL endpoint
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

        Args:
            token_url_pattern: Regex pattern for the token endpoint
            success_response: Response for successful token requests
            error_response: Response for failed token requests
            valid_credentials: Dict of valid credentials for authentication

        Returns:
            List of response patterns for the OAuth flow
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

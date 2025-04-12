"""
Mock implementation for update (PUT/PATCH) operations in CRUD testing.

This module provides a mock implementation for testing update operations,
allowing configuration of responses for specific update scenarios, including
conditional updates, concurrency control, and error simulation.
"""

# crudclient/testing/crud/update.pyi
from typing import Any, Dict, Union

from crudclient.exceptions import NotFoundError

from .base import BaseCrudMock

class UpdateMock(BaseCrudMock):
    """
    Mocks CRUD update (PUT/PATCH) operations, allowing configuration of responses
    for specific update scenarios, including conditional updates, concurrency control,
    and error simulation.

    This mock tracks request history and allows verification of update calls.
    It supports both full (PUT) and partial (PATCH) updates.
    """

    def __init__(self) -> None:
        """Initializes the UpdateMock with default settings."""
        ...

    def put(self, url: str, **kwargs: Any) -> Any:
        """
        Simulates a PUT request for a full resource update.

        Records the request and returns a configured response based on matching patterns
        or the default response. Handles parent_id processing if enabled.

        Args:
            url: The URL for the PUT request.
            **kwargs: Additional arguments passed to the underlying HTTP client,
                      including params, data, json, headers, and parent_id.

        Returns:
            The response body, typically a dictionary for JSON responses or a string.

        Raises:
            Configured exceptions based on matching patterns (e.g., NotFoundError,
            ConcurrencyError).
        """
        ...

    def patch(self, url: str, **kwargs: Any) -> Any:
        """
        Simulates a PATCH request for a partial resource update.

        Records the request and returns a configured response based on matching patterns
        or the default response. Handles parent_id processing if enabled.

        Args:
            url: The URL for the PATCH request.
            **kwargs: Additional arguments passed to the underlying HTTP client,
                      including params, data, json, headers, and parent_id.

        Returns:
            The response body, typically a dictionary for JSON responses or a string.

        Raises:
            Configured exceptions based on matching patterns (e.g., NotFoundError,
            ConcurrencyError).
        """
        ...

    def with_update_response(self, url_pattern: str, updated_data: Dict[str, Any], **kwargs: Any) -> "UpdateMock":
        """
        Configures a successful response (200 OK) for a PUT request matching the URL pattern.

        Args:
            url_pattern: A regex string to match the request URL.
            updated_data: The dictionary to be returned as the JSON response body.
            **kwargs: Additional criteria for matching the request (e.g., params, json, headers).

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        ...

    def with_partial_update_response(
        self, url_pattern: str, partial_data: Dict[str, Any], full_response_data: Dict[str, Any], **kwargs: Any
    ) -> "UpdateMock":
        """
        Configures a successful response (200 OK) for a PATCH request matching the URL pattern
        and specific partial data.

        Args:
            url_pattern: A regex string to match the request URL.
            partial_data: The dictionary representing the partial update data expected in the
                          PATCH request body (matched against kwargs['json']).
            full_response_data: The dictionary to be returned as the full JSON response body.
            **kwargs: Additional criteria for matching the request (e.g., params, headers).

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        ...

    def with_conditional_update(
        self, url_pattern: str, condition_field: str, condition_value: Any, success_data: Dict[str, Any], error_data: Dict[str, Any], **kwargs: Any
    ) -> "UpdateMock":
        """
        Configures a conditional response for PUT/PATCH requests based on a field in the request body.

        If the `condition_field` in the request JSON matches `condition_value`, a 200 OK
        response with `success_data` is returned. Otherwise, a 422 Unprocessable Entity
        response with `error_data` is returned.

        Args:
            url_pattern: A regex string to match the request URL.
            condition_field: The key in the request JSON body to check.
            condition_value: The value to compare against the `condition_field`.
            success_data: The dictionary returned as JSON on successful condition match (200 OK).
            error_data: The dictionary returned as JSON on failed condition match (422 Unprocessable Entity).
            **kwargs: Additional criteria for matching the request (e.g., params, headers).

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        ...

    def with_not_found(self, url_pattern: str, **kwargs: Any) -> "UpdateMock":
        """
        Configures the mock to raise a NotFoundError (simulating a 404 response)
        for PUT/PATCH requests matching the URL pattern.

        Args:
            url_pattern: A regex string to match the request URL.
            **kwargs: Additional criteria for matching the request (e.g., params, json, headers).

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        ...

    def with_stored_resource(self, resource_id: Union[str, int], resource: Dict[str, Any]) -> "UpdateMock":
        """
        Stores an initial version of a resource for concurrency control testing.

        Initializes the resource's version to 1 and calculates an initial ETag.
        This resource can then be used in conjunction with `with_concurrency_control`.

        Args:
            resource_id: The unique identifier for the resource.
            resource: The dictionary representing the initial state of the resource.

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        ...

    def with_concurrency_control(self, url_pattern: str, control_type: str = "etag", version_field: str = "version") -> "UpdateMock":
        """
        Enables concurrency control simulation for PUT/PATCH requests matching the URL pattern.

        This method overrides the standard `put` and `patch` behavior for matching URLs.
        It checks for concurrency conflicts based on the specified `control_type` ('etag' or 'version')
        using internally stored resources (added via `with_stored_resource`).

        - If 'etag', it checks the 'If-Match' request header against the stored ETag.
        - If 'version', it checks the `version_field` in the request JSON against the stored version.

        If a conflict is detected, a `ConcurrencyError` is raised. If the check passes,
        the stored resource is updated, the version is incremented, a new ETag is generated,
        and the updated resource is returned.

        Args:
            url_pattern: A regex string to match the request URL (typically including a
                         capture group for the resource ID, e.g., r'/items/(\d+)$').
            control_type: The concurrency control mechanism ('etag' or 'version'). Defaults to 'etag'.
            version_field: The field name used for version checking if `control_type` is 'version'.
                           Defaults to 'version'.

        Returns:
            The UpdateMock instance for chaining configurations.

        Raises:
            ConcurrencyError: If an ETag or version mismatch is detected.
        """
        ...

    def with_optimistic_locking(self, url_pattern: str, version_field: str = "version") -> "UpdateMock":
        """
        Alias for `with_concurrency_control` specifically configured for version-based optimistic locking.

        Args:
            url_pattern: A regex string to match the request URL.
            version_field: The field name used for version checking. Defaults to 'version'.

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        ...

    def with_etag_concurrency(self, url_pattern: str) -> "UpdateMock":
        """
        Alias for `with_concurrency_control` specifically configured for ETag-based concurrency control.

        Args:
            url_pattern: A regex string to match the request URL.

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        ...

    def with_concurrency_conflict(self, url_pattern: str, resource_id: Union[str, int], **kwargs: Any) -> "UpdateMock":
        """
        Configures the mock to return a 409 Conflict response for a specific resource ID
        matching the URL pattern.

        Useful for testing how the client handles concurrency conflicts reported by the server.

        Args:
            url_pattern: A regex string to match the base request URL (e.g., r'/items').
                         The resource ID will be appended to this pattern.
            resource_id: The specific ID of the resource that should trigger a conflict.
            **kwargs: Additional criteria for matching the request (e.g., params, json, headers).

        Returns:
            The UpdateMock instance for chaining configurations.
        """
        ...

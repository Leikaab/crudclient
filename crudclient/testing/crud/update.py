"""
Mock implementation for Update operations.

This module provides a specialized mock for Update operations with support for
partial updates, concurrency control, and optimistic locking.
"""

import copy
import json
import re
from typing import Any, Dict, Union

from crudclient.exceptions import NotFoundError
from crudclient.testing.response_builder.response import MockResponse

from .base import BaseCrudMock
from .exceptions import ConcurrencyError
from .request_record import RequestRecord


class UpdateMock(BaseCrudMock):
    """
    Mock for Update operations.

    Features:
    - Support for partial updates
    - Support for concurrency control via ETag/If-Match headers
    - Support for optimistic locking via version fields
    - Simulation of concurrency conflicts
    """

    def __init__(self):
        """
        Initialize the Update mock.

        Sets up default response and storage for resources that can be updated.
        """
        super().__init__()
        self.default_response = MockResponse(
            status_code=200,
            json_data={"id": 1, "name": "Updated Resource"}
        )
        self._stored_resources = {}  # id -> resource dict
        self._resource_versions = {}  # id -> version number
        self._resource_etags = {}  # id -> ETag value

    def put(self, url: str, **kwargs: Any) -> Any:
        """
        Handle PUT requests.

        Args:
            url: Request URL
            **kwargs: Request parameters (params, data, json, headers, parent_id)

        Returns:
            Response data (dict, list, or string)
        """
        # Process parent_id if present in kwargs
        parent_id = kwargs.pop('parent_id', None)
        if parent_id and self._parent_id_handling:
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method="PUT",
            url=url,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers=kwargs.get('headers')
        )
        self.request_history.append(record)

        # Find a matching pattern
        pattern = self._find_matching_pattern("PUT", url, **kwargs)

        if pattern:
            response_obj = pattern['response']

            # Handle callable responses
            if callable(response_obj):
                response_obj = response_obj(**kwargs)

            # Handle errors
            if 'error' in pattern and pattern['error']:
                raise pattern['error']

            # Ensure response_obj is a MockResponse
            if not isinstance(response_obj, MockResponse):
                if isinstance(response_obj, dict):
                    response_obj = MockResponse(json_data=response_obj)
                elif isinstance(response_obj, list):
                    response_obj = MockResponse(text=json.dumps(response_obj))
                elif isinstance(response_obj, str):
                    response_obj = MockResponse(text=response_obj)
                else:
                    response_obj = MockResponse(text=str(response_obj))

            record.response = response_obj

            # Return the appropriate response format
            if hasattr(response_obj, '_json_data') and response_obj._json_data is not None:
                return response_obj._json_data
            return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        if hasattr(self.default_response, '_json_data') and self.default_response._json_data is not None:
            return self.default_response._json_data
        return self.default_response.text

    def patch(self, url: str, **kwargs: Any) -> Any:
        """
        Handle PATCH requests.

        Args:
            url: Request URL
            **kwargs: Request parameters (params, data, json, headers, parent_id)

        Returns:
            Response data (dict, list, or string)
        """
        # Process parent_id if present in kwargs
        parent_id = kwargs.pop('parent_id', None)
        if parent_id and self._parent_id_handling:
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method="PATCH",
            url=url,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers=kwargs.get('headers')
        )
        self.request_history.append(record)

        # Find a matching pattern
        pattern = self._find_matching_pattern("PATCH", url, **kwargs)

        if pattern:
            response_obj = pattern['response']

            # Handle callable responses
            if callable(response_obj):
                response_obj = response_obj(**kwargs)

            # Handle errors
            if 'error' in pattern and pattern['error']:
                raise pattern['error']

            # Ensure response_obj is a MockResponse
            if not isinstance(response_obj, MockResponse):
                if isinstance(response_obj, dict):
                    response_obj = MockResponse(json_data=response_obj)
                elif isinstance(response_obj, list):
                    response_obj = MockResponse(text=json.dumps(response_obj))
                elif isinstance(response_obj, str):
                    response_obj = MockResponse(text=response_obj)
                else:
                    response_obj = MockResponse(text=str(response_obj))

            record.response = response_obj

            # Return the appropriate response format
            if hasattr(response_obj, '_json_data') and response_obj._json_data is not None:
                return response_obj._json_data
            return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        if hasattr(self.default_response, '_json_data') and self.default_response._json_data is not None:
            return self.default_response._json_data
        return self.default_response.text

    def with_update_response(
        self,
        url_pattern: str,
        updated_data: Dict[str, Any],
        **kwargs: Any
    ) -> 'UpdateMock':
        """
        Configure an update response.

        Args:
            url_pattern: URL pattern to match
            updated_data: Data to return in the response
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=200,
                json_data=updated_data
            ),
            **kwargs
        )
        return self

    def with_partial_update_response(
        self,
        url_pattern: str,
        partial_data: Dict[str, Any],
        full_response_data: Dict[str, Any],
        **kwargs: Any
    ) -> 'UpdateMock':
        """
        Configure a partial update response.

        This method allows specifying both the partial data expected in the request
        and the full data to be returned in the response.

        Args:
            url_pattern: URL pattern to match
            partial_data: Partial data expected in the request
            full_response_data: Full data to return in the response
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=200,
                json_data=full_response_data
            ),
            json=partial_data,
            **kwargs
        )
        return self

    def with_conditional_update(
        self,
        url_pattern: str,
        condition_field: str,
        condition_value: Any,
        success_data: Dict[str, Any],
        error_data: Dict[str, Any],
        **kwargs: Any
    ) -> 'UpdateMock':
        """
        Configure a conditional update response.

        Args:
            url_pattern: URL pattern to match
            condition_field: Field to check in the request
            condition_value: Expected value for the condition field
            success_data: Data to return if condition is met
            error_data: Data to return if condition is not met
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        def conditional_response(**request_kwargs):
            request_json = request_kwargs.get('json', {})
            if request_json.get(condition_field) == condition_value:
                return MockResponse(
                    status_code=200,
                    json_data=success_data
                )
            else:
                return MockResponse(
                    status_code=422,
                    json_data=error_data
                )

        self.with_response(
            url_pattern=url_pattern,
            response=conditional_response,
            **kwargs
        )
        return self

    def with_not_found(
        self,
        url_pattern: str,
        **kwargs: Any
    ) -> 'UpdateMock':
        """
        Configure a not found response.

        Args:
            url_pattern: URL pattern to match
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        # Create a mock response for not found error
        mock_response = MockResponse(
            status_code=404,
            json_data={"error": "Resource not found"}
        )

        # Create the error instance
        error_instance = NotFoundError(
            f"HTTP error occurred: 404, Resource not found"
        )

        # Add to response patterns
        self.response_patterns.append({
            'url_pattern': url_pattern,
            'response': mock_response,
            'error': error_instance,
            'params': kwargs.get('params'),
            'data': kwargs.get('data'),
            'json': kwargs.get('json'),
            'headers': kwargs.get('headers'),
            'max_calls': kwargs.get('max_calls', float('inf')),
            'call_count': 0
        })
        return self

    def with_stored_resource(self, resource_id: Union[str, int], resource: Dict[str, Any]) -> 'UpdateMock':
        """
        Configure the mock with a stored resource that can be updated.

        Args:
            resource_id: The ID of the resource
            resource: The resource data

        Returns:
            Self for method chaining
        """
        str_id = str(resource_id)
        self._stored_resources[str_id] = copy.deepcopy(resource)
        self._resource_versions[str_id] = 1  # Initial version
        self._resource_etags[str_id] = f'W/"{hash(json.dumps(resource))}"'  # Initial ETag

        return self

    def with_concurrency_control(
        self,
        url_pattern: str,
        control_type: str = 'etag',
        version_field: str = 'version'
    ) -> 'UpdateMock':
        """
        Configure the mock to support concurrency control.

        Args:
            url_pattern: URL pattern to match
            control_type: Type of concurrency control ('etag' or 'version')
            version_field: Field name for version-based concurrency control

        Returns:
            Self for method chaining
        """
        # Override the put method to handle concurrency control
        original_put = self.put

        def put_with_concurrency_control(url: str, **kwargs: Any) -> Any:
            # Check if this URL matches the pattern
            if re.search(url_pattern, url):
                # Extract the resource ID from the URL
                id_match = re.search(r'/([^/]+)$', url)
                if id_match:
                    resource_id = id_match.group(1)

                    # If the resource exists
                    if resource_id in self._stored_resources:
                        # Check concurrency control based on the type
                        if control_type == 'etag':
                            # ETag-based concurrency control
                            headers = kwargs.get('headers', {})
                            if_match = headers.get('If-Match')
                            current_etag = self._resource_etags.get(resource_id, '')

                            if if_match and if_match != current_etag:
                                # ETag mismatch - resource has been modified
                                raise ConcurrencyError("Resource has been modified by another request")

                        elif control_type == 'version':
                            # Version-based concurrency control
                            json_data = kwargs.get('json', {})
                            if version_field in json_data:
                                client_version = json_data[version_field]
                                current_version = self._resource_versions.get(resource_id, 1)

                                if client_version != current_version:
                                    # Version mismatch - resource has been modified
                                    raise ConcurrencyError(f"Expected version {current_version}, got {client_version}")

                        # If concurrency check passes, update the resource
                        json_data = kwargs.get('json', {})

                        # Update the stored resource
                        updated_resource = copy.deepcopy(self._stored_resources[resource_id])

                        # Full update - replace the entire resource
                        updated_resource.update(json_data)
                        # Ensure the ID is preserved
                        updated_resource['id'] = self._stored_resources[resource_id].get('id')

                        # Update version and ETag
                        self._resource_versions[resource_id] = self._resource_versions.get(resource_id, 1) + 1
                        updated_resource[version_field] = self._resource_versions[resource_id]
                        self._resource_etags[resource_id] = f'W/"{hash(json.dumps(updated_resource))}"'

                        # Store the updated resource
                        self._stored_resources[resource_id] = updated_resource

                        # Return the updated resource
                        return updated_resource

            # If no matching resource or pattern, call the original put method
            return original_put(url, **kwargs)

        # Replace the put method with our wrapper
        self.put = put_with_concurrency_control

        # Also override the patch method for partial updates
        original_patch = self.patch

        def patch_with_concurrency_control(url: str, **kwargs: Any) -> Any:
            # Check if this URL matches the pattern
            if re.search(url_pattern, url):
                # Extract the resource ID from the URL
                id_match = re.search(r'/([^/]+)$', url)
                if id_match:
                    resource_id = id_match.group(1)

                    # If the resource exists
                    if resource_id in self._stored_resources:
                        # Check concurrency control based on the type
                        if control_type == 'etag':
                            # ETag-based concurrency control
                            headers = kwargs.get('headers', {})
                            if_match = headers.get('If-Match')
                            current_etag = self._resource_etags.get(resource_id, '')

                            if if_match and if_match != current_etag:
                                # ETag mismatch - resource has been modified
                                raise ConcurrencyError("Resource has been modified by another request")

                        elif control_type == 'version':
                            # Version-based concurrency control
                            json_data = kwargs.get('json', {})
                            if version_field in json_data:
                                client_version = json_data[version_field]
                                current_version = self._resource_versions.get(resource_id, 1)

                                if client_version != current_version:
                                    # Version mismatch - resource has been modified
                                    raise ConcurrencyError(f"Expected version {current_version}, got {client_version}")

                        # If concurrency check passes, update the resource
                        json_data = kwargs.get('json', {})

                        # Update the stored resource
                        updated_resource = copy.deepcopy(self._stored_resources[resource_id])

                        # Partial update - update only the provided fields
                        updated_resource.update(json_data)

                        # Update version and ETag
                        self._resource_versions[resource_id] = self._resource_versions.get(resource_id, 1) + 1
                        updated_resource[version_field] = self._resource_versions[resource_id]
                        self._resource_etags[resource_id] = f'W/"{hash(json.dumps(updated_resource))}"'

                        # Store the updated resource
                        self._stored_resources[resource_id] = updated_resource

                        # Return the updated resource
                        return updated_resource

            # If no matching resource or pattern, call the original patch method
            return original_patch(url, **kwargs)

        # Replace the patch method with our wrapper
        self.patch = patch_with_concurrency_control

        return self

    def with_optimistic_locking(
        self,
        url_pattern: str,
        version_field: str = 'version'
    ) -> 'UpdateMock':
        """
        Configure the mock to support optimistic locking via a version field.

        Args:
            url_pattern: URL pattern to match
            version_field: Field name for the version

        Returns:
            Self for method chaining
        """
        return self.with_concurrency_control(url_pattern, 'version', version_field)

    def with_etag_concurrency(self, url_pattern: str) -> 'UpdateMock':
        """
        Configure the mock to support ETag-based concurrency control.

        Args:
            url_pattern: URL pattern to match

        Returns:
            Self for method chaining
        """
        return self.with_concurrency_control(url_pattern, 'etag')

    def with_concurrency_conflict(
        self,
        url_pattern: str,
        resource_id: Union[str, int],
        **kwargs: Any
    ) -> 'UpdateMock':
        """
        Configure the mock to simulate a concurrency conflict for a specific resource.

        Args:
            url_pattern: URL pattern to match
            resource_id: The ID of the resource that will have a conflict
            **kwargs: Additional parameters for the response pattern

        Returns:
            Self for method chaining
        """
        # Create a response that simulates a concurrency conflict
        conflict_response = MockResponse(
            status_code=409,  # Conflict
            json_data={
                "error": "Concurrency conflict",
                "message": "Resource has been modified by another request",
                "resourceId": str(resource_id)
            },
            error=ConcurrencyError("Resource has been modified by another request")
        )

        # Add the conflict response for the specific resource
        self.with_response(
            url_pattern=f"{url_pattern}/{resource_id}$",
            response=conflict_response,
            **kwargs
        )

        return self

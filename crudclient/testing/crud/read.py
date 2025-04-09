"""
Mock implementation for Read operations.

This module provides a specialized mock for Read operations with support for
filtering, sorting, field selection, and pagination.
"""

import copy
import json
import re
from typing import Any, Dict, List

from crudclient.exceptions import NotFoundError
from crudclient.testing.response_builder.response import MockResponse

from .base import BaseCrudMock
from .request_record import RequestRecord


class ReadMock(BaseCrudMock):
    """
    Mock for Read operations.

    Features:
    - Support for filtering by field values
    - Support for sorting by fields
    - Support for field selection (partial responses)
    - Pagination support
    """

    def __init__(self):
        """
        Initialize the Read mock.

        Sets up default response and storage for resources that can be queried.
        """
        super().__init__()
        self.default_response = MockResponse(
            status_code=200,
            json_data={"id": 1, "name": "Read Resource"}
        )
        self._stored_resources = []  # List of resources that can be queried

    def get(self, url: str, **kwargs: Any) -> Any:
        """
        Handle GET requests.

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
            method="GET",
            url=url,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers=kwargs.get('headers')
        )
        self.request_history.append(record)

        # Find a matching pattern
        pattern = self._find_matching_pattern("GET", url, **kwargs)

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

    def with_single_resource(
        self,
        url_pattern: str,
        resource_data: Dict[str, Any],
        **kwargs: Any
    ) -> 'ReadMock':
        """
        Configure a single resource response.

        Args:
            url_pattern: URL pattern to match
            resource_data: Resource data to return
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=200,
                json_data=resource_data
            ),
            **kwargs
        )
        return self

    def with_resource_list(
        self,
        url_pattern: str,
        resources: List[Dict[str, Any]],
        **kwargs: Any
    ) -> 'ReadMock':
        """
        Configure a resource list response.

        Args:
            url_pattern: URL pattern to match
            resources: List of resource data to return
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=200,
                text=json.dumps(resources)
            ),
            **kwargs
        )
        return self

    def with_stored_resources(self, resources: List[Dict[str, Any]]) -> 'ReadMock':
        """
        Configure the mock with a list of resources that can be queried.

        This method sets up the mock to handle GET requests with filtering,
        sorting, and field selection based on the provided resources.

        Args:
            resources: List of resource dictionaries

        Returns:
            Self for method chaining
        """
        self._stored_resources = copy.deepcopy(resources)

        # Create a function to handle GET requests with filtering, sorting, and field selection
        def handle_get_request(url: str, **kwargs: Any) -> Any:
            # Check if this is a request for a specific resource by ID
            resource_id_match = re.search(r'/(\d+)$', url)
            if resource_id_match:
                resource_id = int(resource_id_match.group(1))
                # Find the resource with the matching ID
                for resource in self._stored_resources:
                    if resource.get('id') == resource_id:
                        # Apply field selection if specified
                        if 'fields' in kwargs.get('params', {}):
                            fields = kwargs['params']['fields'].split(',')
                            return {field: resource[field] for field in fields if field in resource}
                        return resource

                # Resource not found
                return MockResponse(
                    status_code=404,
                    json_data={"error": "Resource not found"},
                    error=NotFoundError("Resource not found")
                )

            # This is a list request, apply filtering, sorting, and pagination
            result = self._stored_resources.copy()

            # Apply filtering
            if 'params' in kwargs and kwargs['params']:
                params = kwargs['params']
                for key, value in params.items():
                    if key not in ('sort', 'fields', 'page', 'limit'):
                        # Simple equality filter
                        result = [r for r in result if str(r.get(key)) == str(value)]

            # Apply sorting
            if 'params' in kwargs and 'sort' in kwargs['params']:
                sort_fields = kwargs['params']['sort'].split(',')
                for field in reversed(sort_fields):
                    reverse = False
                    if field.startswith('-'):
                        field = field[1:]
                        reverse = True
                    result.sort(key=lambda r: r.get(field, ''), reverse=reverse)

            # Apply pagination
            if 'params' in kwargs and ('page' in kwargs['params'] or 'limit' in kwargs['params']):
                page = int(kwargs['params'].get('page', 1))
                limit = int(kwargs['params'].get('limit', 10))
                start = (page - 1) * limit
                end = start + limit
                result = result[start:end]

            # Apply field selection
            if 'params' in kwargs and 'fields' in kwargs['params']:
                fields = kwargs['params']['fields'].split(',')
                result = [{field: r.get(field) for field in fields if field in r} for r in result]

            return result

        # Replace the get method with our custom implementation
        self.get = handle_get_request

        return self

    def with_field_selection(self, url_pattern: str, **kwargs: Any) -> 'ReadMock':
        """
        Configure the mock to support field selection via the 'fields' parameter.

        Args:
            url_pattern: URL pattern to match
            **kwargs: Additional parameters for the response pattern

        Returns:
            Self for method chaining
        """
        def field_selection_response(**request_kwargs):
            # Get the requested fields
            params = request_kwargs.get('params', {})
            if 'fields' in params:
                fields = params['fields'].split(',')
                # Get the original response
                original_response = self.default_response
                if hasattr(original_response, '_json_data') and original_response._json_data:
                    # Filter the response to include only the requested fields
                    filtered_data = {field: original_response._json_data.get(field)
                                     for field in fields
                                     if field in original_response._json_data}
                    return MockResponse(
                        status_code=200,
                        json_data=filtered_data
                    )

            # If no field selection or invalid fields, return None to use the default response
            return None

        self.with_response(
            url_pattern=url_pattern,
            response=field_selection_response,
            **kwargs
        )
        return self

    def with_filtering(self, url_pattern: str, **kwargs: Any) -> 'ReadMock':
        """
        Configure the mock to support filtering by field values.

        Args:
            url_pattern: URL pattern to match
            **kwargs: Additional parameters for the response pattern

        Returns:
            Self for method chaining
        """
        def filtering_response(**request_kwargs):
            # Get the filter parameters
            params = request_kwargs.get('params', {})
            if not params:
                return None

            # Check if this is a list request with filter parameters
            filter_params = {k: v for k, v in params.items()
                             if k not in ('sort', 'fields', 'page', 'limit')}

            if filter_params and self._stored_resources:
                # Apply filters to the stored resources
                filtered_resources = self._stored_resources.copy()
                for key, value in filter_params.items():
                    filtered_resources = [r for r in filtered_resources
                                          if str(r.get(key)) == str(value)]

                return MockResponse(
                    status_code=200,
                    text=json.dumps(filtered_resources if len(filtered_resources) > 0 else [])
                )

            # If no filtering or no stored resources, return None to use the default response
            return None

        self.with_response(
            url_pattern=url_pattern,
            response=filtering_response,
            **kwargs
        )
        return self

    def with_sorting(self, url_pattern: str, **kwargs: Any) -> 'ReadMock':
        """
        Configure the mock to support sorting by fields.

        Args:
            url_pattern: URL pattern to match
            **kwargs: Additional parameters for the response pattern

        Returns:
            Self for method chaining
        """
        def sorting_response(**request_kwargs):
            # Get the sort parameter
            params = request_kwargs.get('params', {})
            if 'sort' in params and self._stored_resources:
                sort_fields = params['sort'].split(',')
                sorted_resources = self._stored_resources.copy()

                # Apply sorting for each field in reverse order (last field has highest priority)
                for field in reversed(sort_fields):
                    reverse = False
                    if field.startswith('-'):
                        field = field[1:]
                        reverse = True

                    sorted_resources.sort(key=lambda r: r.get(field, ''), reverse=reverse)

                return MockResponse(
                    status_code=200,
                    text=json.dumps(sorted_resources)
                )

            # If no sorting or no stored resources, return None to use the default response
            return None

        self.with_response(
            url_pattern=url_pattern,
            response=sorting_response,
            **kwargs
        )
        return self

    def with_pagination(self, url_pattern: str, **kwargs: Any) -> 'ReadMock':
        """
        Configure the mock to support pagination via page and limit parameters.

        Args:
            url_pattern: URL pattern to match
            **kwargs: Additional parameters for the response pattern

        Returns:
            Self for method chaining
        """
        def pagination_response(**request_kwargs):
            # Get the pagination parameters
            params = request_kwargs.get('params', {})
            if ('page' in params or 'limit' in params) and self._stored_resources:
                page = int(params.get('page', 1))
                limit = int(params.get('limit', 10))

                # Calculate the slice of resources to return
                start = (page - 1) * limit
                end = start + limit
                paginated_resources = self._stored_resources[start:end]

                # Create a paginated response with metadata
                return MockResponse(
                    status_code=200,
                    json_data={
                        "data": paginated_resources,
                        "meta": {
                            "page": page,
                            "limit": limit,
                            "total": len(self._stored_resources),
                            "pages": (len(self._stored_resources) + limit - 1) // limit,
                            "total_count": len(self._stored_resources),
                            "total_pages": (len(self._stored_resources) + limit - 1) // limit
                        }
                    }
                )

            # If no pagination or no stored resources, return None to use the default response
            return None

        self.with_response(
            url_pattern=url_pattern,
            response=pagination_response,
            **kwargs
        )

        # Override the get method to handle pagination
        original_get = self.get

        def get_with_pagination(url: str, **kwargs: Any) -> Any:
            # Check if this URL matches the pagination pattern
            if re.search(url_pattern, url):
                params = kwargs.get('params', {})
                if 'page' in params or 'limit' in params:
                    # This is a paginated request
                    page = int(params.get('page', 1))
                    limit = int(params.get('limit', 10))

                    # Get all resources
                    all_resources = self._stored_resources

                    # Calculate pagination
                    start = (page - 1) * limit
                    end = start + limit
                    paginated_data = all_resources[start:end]

                    # Return paginated response
                    return {
                        "data": paginated_data,
                        "meta": {
                            "page": page,
                            "limit": limit,
                            "total": len(all_resources),
                            "pages": (len(all_resources) + limit - 1) // limit,
                            "total_count": len(all_resources),
                            "total_pages": (len(all_resources) + limit - 1) // limit
                        }
                    }

            # If not a paginated request or pattern doesn't match, use original method
            return original_get(url, **kwargs)

        # Replace the get method with our wrapper
        self.get = get_with_pagination

        return self

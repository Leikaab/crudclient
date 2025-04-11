"""
Read operation mock for testing.

This module provides a mock for the Read operation in CRUD APIs, allowing for
testing of GET requests with various response patterns, filtering, sorting,
pagination, and field selection capabilities.
"""

import copy
import json
import re
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Union

from crudclient.testing.response_builder.response import MockResponse

from .base import BaseCrudMock

if TYPE_CHECKING:
    from .request_record import RequestRecord

class ReadMock(BaseCrudMock):
    """
    Mock for Read operations in CRUD APIs.

    This class provides functionality for mocking GET requests with various
    response patterns, including support for filtering, sorting, pagination,
    and field selection. It can be used to test API clients that perform
    read operations.
    """

    _parent_id_handling: bool
    request_history: List["RequestRecord"]

    def __init__(self) -> None:
        """
        Initialize the Read mock.

        Sets up the default response and stored resources list.
        """
        ...

    def get(self, url: str, **kwargs: Any) -> Any:
        """
        Handle GET requests.

        Records the request and returns a response based on matching patterns.

        Args:
            url: The URL to request
            **kwargs: Additional request parameters, including parent_id

        Returns:
            The mock response data
        """
        ...

    def with_single_resource(self, url_pattern: str, resource_data: Dict[str, Any], **kwargs: Any) -> "ReadMock":
        """
        Configure a response for a single resource.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            resource_data: Resource data to return
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

    def with_resource_list(self, url_pattern: str, resources: List[Dict[str, Any]], **kwargs: Any) -> "ReadMock":
        """
        Configure a response for a list of resources.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            resources: List of resource data to return
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

    def set_stored_resources(self, resources: List[Dict[str, Any]]) -> "ReadMock":
        """
        Set a list of resources that the mock will use for dynamic filtering,
        sorting, and pagination based on request parameters.

        Args:
            resources: A list of dictionaries representing the resources.

        Returns:
            Self for method chaining
        """
        ...

    def with_stored_resources(self, resources: List[Dict[str, Any]]) -> "ReadMock":
        """
        Configure the mock with a list of resources for dynamic querying.

        This method sets up the mock to handle GET requests dynamically based on
        the provided resources, supporting filtering, sorting, pagination, and
        field selection through query parameters.

        Args:
            resources: List of resource data to store and query

        Returns:
            Self for method chaining
        """
        ...

    def with_field_selection(self, url_pattern: str, **kwargs: Any) -> "ReadMock":
        """
        Configure the mock to support field selection.

        This method sets up the mock to handle the 'fields' query parameter,
        returning only the requested fields from the resource data.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

    def with_filtering(self, url_pattern: str, **kwargs: Any) -> "ReadMock":
        """
        Configure the mock to support filtering.

        This method sets up the mock to handle query parameters as filters,
        returning only resources that match the filter criteria.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

    def with_sorting(self, url_pattern: str, **kwargs: Any) -> "ReadMock":
        """
        Configure the mock to support sorting.

        This method sets up the mock to handle the 'sort' query parameter,
        returning resources sorted by the specified fields.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

    def with_pagination(self, url_pattern: str, **kwargs: Any) -> "ReadMock":
        """
        Configure the mock to support pagination.

        This method sets up the mock to handle the 'page' and 'limit' query parameters,
        returning a paginated response with metadata.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

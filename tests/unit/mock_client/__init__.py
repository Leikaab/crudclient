"""
Enhanced mock Client implementation for testing.

This module provides a sophisticated mock Client implementation with configurable behavior,
support for complex response scenarios, and helpers for verifying client usage patterns.
"""

from crudclient.testing.response_builder.api_patterns import APIPatternBuilder
from crudclient.testing.core.client import MockClient
from crudclient.testing.core.http_client import MockHTTPClient as MockHttpClient
from crudclient.testing.factory.simple_mock import create_simple_mock_client
from crudclient.testing.core.network import NetworkCondition
from crudclient.testing.helpers.pagination import PaginationHelper
from crudclient.testing.helpers.partial_response import PartialResponseHelper
from crudclient.testing.response_builder.patterns import ResponsePattern
from crudclient.testing.helpers.rate_limit import RateLimitHelper
from crudclient.testing.response_builder.response import MockResponse
from crudclient.testing.response_builder import (
    ResponseBuilder, EntityRelationshipBuilder,
    ValidationErrorBuilder, BusinessLogicConstraintBuilder
)
from crudclient.testing.factory.simple_mock import SimpleMockClient
from crudclient.testing.verification import Verifier

# Define verification classes for backward compatibility


class RequestVerifier:
    """
    Backward compatibility class for verifying requests.

    This class provides a compatibility layer for code that expects to use
    the RequestVerifier class from tests.unit.mock_client.
    """

    @staticmethod
    def verify_request_made(client, method=None, url_pattern=None):
        """
        Verify that a request was made.

        Args:
            client: The client to verify
            method: Optional HTTP method to filter by
            url_pattern: Optional URL pattern to filter by

        Returns:
            True if the request was made, False otherwise
        """
        if hasattr(client, 'assert_request_made'):
            client.assert_request_made(method, url_pattern)
            return True
        return False

    @staticmethod
    def verify_request_not_made(client, method=None, url_pattern=None):
        """
        Verify that a request was not made.

        Args:
            client: The client to verify
            method: Optional HTTP method to filter by
            url_pattern: Optional URL pattern to filter by

        Returns:
            True if the request was not made, False otherwise
        """
        if hasattr(client, 'assert_request_not_made'):
            client.assert_request_not_made(method, url_pattern)
            return True
        return False

    @staticmethod
    def verify_request_count(client, count, method=None, url_pattern=None):
        """
        Verify that a specific number of requests were made.

        Args:
            client: The client to verify
            count: The expected number of requests
            method: Optional HTTP method to filter by
            url_pattern: Optional URL pattern to filter by

        Returns:
            True if the request count matches, False otherwise
        """
        if hasattr(client, 'assert_request_count'):
            client.assert_request_count(count, method, url_pattern)
            return True
        return False


class ResponseVerifier:
    """
    Backward compatibility class for verifying responses.

    This class provides a compatibility layer for code that expects to use
    the ResponseVerifier class from tests.unit.mock_client.
    """

    @staticmethod
    def verify_response_status(response, expected_status):
        """
        Verify that a response has the expected status code.

        Args:
            response: The response to verify
            expected_status: The expected status code

        Returns:
            True if the status code matches, False otherwise
        """
        if hasattr(response, 'status_code'):
            assert response.status_code == expected_status, f"Expected status {expected_status}, got {response.status_code}"
            return True
        return False

    @staticmethod
    def verify_response_json(response, expected_json):
        """
        Verify that a response has the expected JSON data.

        Args:
            response: The response to verify
            expected_json: The expected JSON data

        Returns:
            True if the JSON data matches, False otherwise
        """
        if hasattr(response, 'json'):
            json_data = response.json()
            assert json_data == expected_json, f"Expected JSON {expected_json}, got {json_data}"
            return True
        return False


class APIVerifier:
    """
    Backward compatibility class for verifying API interactions.

    This class provides a compatibility layer for code that expects to use
    the APIVerifier class from tests.unit.mock_client.
    """

    @staticmethod
    def verify_endpoint_called(api, endpoint):
        """
        Verify that an API endpoint was called.

        Args:
            api: The API to verify
            endpoint: The endpoint to check

        Returns:
            True if the endpoint was called, False otherwise
        """
        if hasattr(api, 'assert_endpoint_called'):
            api.assert_endpoint_called(endpoint)
            return True
        return False


def create_mock_client(config=None, **kwargs):
    """
    Create a pre-configured MockClient instance.

    This function provides backward compatibility for code that
    expects to import create_mock_client from tests.unit.mock_client.

    Args:
        config: Optional client configuration
        **kwargs: Additional configuration options

    Returns:
        A configured MockClient instance
    """
    from crudclient.testing.core.client import MockClient
    from crudclient.testing.core.http_client import MockHTTPClient

    # Create a mock HTTP client
    http_client = MockHTTPClient(base_url=config.hostname if config else "https://api.example.com")

    # Create a mock client with the mock HTTP client
    mock_client = MockClient(
        http_client=http_client,
        **kwargs
    )
    return mock_client


__all__ = [
    # Core mock components
    'MockResponse',
    'MockHttpClient',
    'ResponsePattern',
    'NetworkCondition',
    'PaginationHelper',
    'RateLimitHelper',
    'PartialResponseHelper',
    'MockClient',
    'SimpleMockClient',
    # Factory functions
    'create_mock_client',
    'create_simple_mock_client',  # Re-exported from crudclient.testing.factory


    # API pattern builders
    'APIPatternBuilder',

    # Response builders
    'ResponseBuilder',
    'EntityRelationshipBuilder',
    'ValidationErrorBuilder',
    'BusinessLogicConstraintBuilder',

    # Verification helpers
    'RequestVerifier',
    'ResponseVerifier',
    'APIVerifier',
]

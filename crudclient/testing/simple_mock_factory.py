# crudclient/testing/simple_mock_factory.py

from typing import Any

from crudclient.testing.factory_helpers import (
    _add_error_responses_to_simple_mock,
    _create_api_patterns,
)
from crudclient.testing.simple_mock import SimpleMockClient


def create_simple_mock_client(**kwargs: Any) -> SimpleMockClient:
    client = SimpleMockClient()

    # Set default response if specified
    if "default_response" in kwargs:
        client.with_default_response(kwargs["default_response"])

    # Add API-specific patterns based on api_type
    api_type = kwargs.get("api_type")
    if api_type:
        patterns = _create_api_patterns(api_type, **kwargs)  # Use helper from factory_helpers
        for pattern in patterns:
            # Adapt pattern for SimpleMockClient's with_response_pattern
            response_dict = {
                "status_code": pattern.get("status_code", 200),
                "json_data": pattern.get("data"),
                "headers": pattern.get("headers"),
                "text_data": pattern.get("text"),  # Assuming text might be used
                "error": pattern.get("error"),
            }
            # Filter out None values
            response_dict = {k: v for k, v in response_dict.items() if v is not None}

            # Ensure method and url_pattern are strings, providing defaults if None
            method = pattern.get("method", "GET") or "GET"
            url_pattern = pattern.get("path", r".*") or r".*"
            client.with_response_pattern(
                method=method,
                url_pattern=url_pattern,  # Use 'path' from MockClient pattern as 'url_pattern'
                response=response_dict,
            )

    # Add common error responses if specified
    if "error_responses" in kwargs:
        _add_error_responses_to_simple_mock(client, kwargs["error_responses"])  # Use helper from factory_helpers

    # Add response patterns if specified
    patterns = kwargs.get("response_patterns", [])
    for pattern in patterns:
        # Adapt pattern for SimpleMockClient's with_response_pattern
        response_dict = {
            "status_code": pattern.get("status_code", 200),
            "json_data": pattern.get("data"),
            "headers": pattern.get("headers"),
            "text_data": pattern.get("text"),
            "error": pattern.get("error"),
        }
        # Filter out None values
        response_dict = {k: v for k, v in response_dict.items() if v is not None}

        # Ensure method and url_pattern are strings, providing defaults if None
        method = pattern.get("method", "GET") or "GET"
        url_pattern = pattern.get("path", r".*") or r".*"
        client.with_response_pattern(
            method=method,
            url_pattern=url_pattern,  # Use 'path' from MockClient pattern as 'url_pattern'
            response=response_dict,
        )

    return client

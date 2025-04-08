"""
Tests for the SimpleMockClient implementation.
"""

import pytest

from tests.unit.mock_client import SimpleMockClient, MockResponse


def test_simple_mock_basic_response():
    """Test that the mock client returns the configured response."""
    # Create a mock client
    client = SimpleMockClient()

    # Configure a response pattern
    client.with_response_pattern(
        method="GET",
        url_pattern=r"/test$",
        response={"message": "Hello, world!"}
    )

    # Make a request that matches the pattern
    response = client.get("/test")

    # Verify the response
    assert response == '{"message": "Hello, world!"}'

    # Verify request history
    assert len(client.request_history) == 1
    assert client.request_history[0].method == "GET"
    assert client.request_history[0].url.endswith("/test")


def test_simple_mock_multiple_patterns():
    """Test multiple response patterns with different HTTP methods."""
    # Create a mock client
    client = SimpleMockClient()

    # Configure the mock client with multiple response patterns
    client.with_response_pattern(
        method="GET",
        url_pattern=r"/users$",
        response={"users": [{"id": 1}, {"id": 2}]}
    )

    client.with_response_pattern(
        method="POST",
        url_pattern=r"/users$",
        response={"id": 3, "created": True}
    )

    client.with_response_pattern(
        method="GET",
        url_pattern=r"/users/1$",
        response={"id": 1, "name": "User One"}
    )

    # Make requests that match the patterns
    users_response = client.get("/users")
    create_response = client.post("/users", data={"name": "New User"})
    user_one_response = client.get("/users/1")

    # Verify the responses
    assert '{"users": [{"id": 1}, {"id": 2}]}' == users_response
    assert '{"id": 3, "created": true}' == create_response
    assert '{"id": 1, "name": "User One"}' == user_one_response


def test_simple_mock_parameter_matching():
    """Test matching requests based on query parameters."""
    # Create a mock client
    client = SimpleMockClient()

    # Configure the mock client with parameter matching
    client.with_response_pattern(
        method="GET",
        url_pattern=r"/search$",
        params={"q": "test"},
        response={"results": ["test result"]}
    )

    client.with_response_pattern(
        method="GET",
        url_pattern=r"/search$",
        params={"q": "other"},
        response={"results": ["other result"]}
    )

    # Make requests with different parameters
    test_response = client.get("/search", params={"q": "test"})
    other_response = client.get("/search", params={"q": "other"})

    # Verify the responses
    assert '{"results": ["test result"]}' == test_response
    assert '{"results": ["other result"]}' == other_response


def test_simple_mock_default_response():
    """Test default response for unmatched requests."""
    # Create a mock client
    client = SimpleMockClient()

    # Configure a default response
    client.with_default_response({"error": "Custom error message"})

    # Make a request that doesn't match any pattern
    response = client.get("/nonexistent")

    # Verify the response
    assert '{"error": "Custom error message"}' == response


def test_simple_mock_request_verification():
    """Test request verification helpers."""
    # Create a mock client
    client = SimpleMockClient()

    # Configure response patterns
    client.with_response_pattern(
        method="GET",
        url_pattern=r"/users$",
        response={"users": []}
    )

    client.with_response_pattern(
        method="POST",
        url_pattern=r"/users$",
        response={"id": 1}
    )

    # Make some requests
    client.get("/users", params={"page": "1"})
    client.post("/users", json={"name": "Test User"})
    client.get("/users", params={"page": "2"})

    # Verify request count
    client.assert_request_count(3)
    client.assert_request_count(2, method="GET")
    client.assert_request_count(1, method="POST")

    # Verify request sequence
    client.assert_request_sequence([
        {"method": "GET"},
        {"method": "POST"},
        {"method": "GET"}
    ])

    # Verify request parameters
    client.assert_request_params(
        {"page": "1"},
        method="GET",
        url_pattern=r"/users$"
    )

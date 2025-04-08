"""
Tests for the MockClient implementation.
"""

import pytest

from tests.unit.mock_client import MockClient, MockResponse


def test_mock_client_basic_response():
    """Test that the mock client returns the configured response."""
    # Create a mock client
    client = MockClient(config={"hostname": "https://mock-api.example.com", "version": "v1"})

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


def test_mock_client_rate_limiting():
    """Test that the mock client simulates rate limiting."""
    # Create a mock client with rate limiting
    client = MockClient(config={"hostname": "https://mock-api.example.com", "version": "v1"})
    client.with_rate_limiter(limit=2, window_seconds=60)

    # Configure a response pattern
    client.with_response_pattern(
        method="GET",
        url_pattern=r"/test$",
        response={"message": "Hello, world!"}
    )

    # First two requests should succeed
    response1 = client.get("/test")
    response2 = client.get("/test")

    assert response1 == '{"message": "Hello, world!"}'
    assert response2 == '{"message": "Hello, world!"}'

    # Third request should be rate limited
    response3 = client.get("/test")
    assert isinstance(response3, str) and "Rate limit exceeded" in response3


def test_mock_client_network_conditions():
    """Test that the mock client simulates network conditions."""
    # Create a mock client with network conditions
    client = MockClient(config={"hostname": "https://mock-api.example.com", "version": "v1"})
    client.with_network_condition(
        error_rate_percentage=100.0,  # Always raise an error
        error_factory=lambda: Exception("Simulated network error")
    )

    # Configure a response pattern
    client.with_response_pattern(
        method="GET",
        url_pattern=r"/test$",
        response={"message": "Hello, world!"}
    )

    # Request should raise an error
    with pytest.raises(Exception) as excinfo:
        client.get("/test")

    assert "Simulated network error" in str(excinfo.value)


def test_mock_client_request_verification():
    """Test the request verification helpers."""
    # Create a mock client
    client = MockClient(config={"hostname": "https://mock-api.example.com", "version": "v1"})

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

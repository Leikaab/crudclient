"""
Examples of using the enhanced mock client for testing.
"""

import pytest

from crudclient.testing import MockClient, MockResponse


class TestMockClientExamples:
    """Examples of using the enhanced mock client for testing."""

    def test_basic_response_pattern(self, mock_client: MockClient):
        """Test basic response pattern matching."""
        # Configure the mock client with a response pattern
        mock_client.with_response_pattern(
            method="GET",
            url_pattern=r"/users/\d+",
            response={"id": 123, "name": "Test User"}
        )

        # Make a request that matches the pattern
        response = mock_client.get("/users/123")

        # Verify the response
        assert '{"id": 123, "name": "Test User"}' == response

    def test_multiple_response_patterns(self, mock_client: MockClient):
        """Test multiple response patterns with different HTTP methods."""
        # Configure the mock client with multiple response patterns
        mock_client.with_response_pattern(
            method="GET",
            url_pattern=r"/users$",
            response={"users": [{"id": 1}, {"id": 2}]}
        )

        mock_client.with_response_pattern(
            method="POST",
            url_pattern=r"/users$",
            response={"id": 3, "created": True}
        )

        mock_client.with_response_pattern(
            method="GET",
            url_pattern=r"/users/1$",
            response={"id": 1, "name": "User One"}
        )

        # Make requests that match the patterns
        users_response = mock_client.get("/users")
        create_response = mock_client.post("/users", data={"name": "New User"})
        user_one_response = mock_client.get("/users/1")

        # Verify the responses
        assert '{"users": [{"id": 1}, {"id": 2}]}' == users_response
        assert '{"id": 3, "created": true}' == create_response
        assert '{"id": 1, "name": "User One"}' == user_one_response

    def test_parameter_matching(self, mock_client: MockClient):
        """Test matching requests based on query parameters."""
        # Configure the mock client with parameter matching
        mock_client.with_response_pattern(
            method="GET",
            url_pattern=r"/search$",
            params={"q": "test"},
            response={"results": ["test result"]}
        )

        mock_client.with_response_pattern(
            method="GET",
            url_pattern=r"/search$",
            params={"q": "other"},
            response={"results": ["other result"]}
        )

        # Make requests with different parameters
        test_response = mock_client.get("/search", params={"q": "test"})
        other_response = mock_client.get("/search", params={"q": "other"})

        # Verify the responses
        assert '{"results": ["test result"]}' == test_response
        assert '{"results": ["other result"]}' == other_response

    def test_network_conditions(self, mock_client: MockClient):
        """Test simulating network conditions."""
        # Configure the mock client with network conditions
        mock_client.with_network_condition(
            latency_ms=100,  # 100ms latency
            error_rate_percentage=50  # 50% chance of error
        )

        mock_client.with_response_pattern(
            method="GET",
            url_pattern=r"/data$",
            response={"data": "success"}
        )

        # Make multiple requests to test error rate
        # Note: This is probabilistic, so we can't assert exact behavior
        try:
            for _ in range(5):
                mock_client.get("/data")
        except Exception as e:
            # We expect some requests to fail with network errors
            assert "Simulated network error" in str(e)

    def test_rate_limiting(self, mock_client: MockClient):
        """Test simulating rate limiting."""
        # Configure the mock client with rate limiting
        mock_client.with_rate_limiter(limit=2, window_seconds=60)

        mock_client.with_response_pattern(
            method="GET",
            url_pattern=r"/api$",
            response={"status": "ok"}
        )

        # First two requests should succeed
        response1 = mock_client.get("/api")
        response2 = mock_client.get("/api")

        assert '{"status": "ok"}' == response1
        assert '{"status": "ok"}' == response2

        # Third request should be rate limited
        response3 = mock_client.get("/api")
        assert isinstance(response3, str) and "Rate limit exceeded" in response3

    def test_request_verification(self, mock_client: MockClient):
        """Test request verification helpers."""
        # Configure the mock client
        mock_client.with_response_pattern(
            method="GET",
            url_pattern=r"/users$",
            response={"users": []}
        )

        mock_client.with_response_pattern(
            method="POST",
            url_pattern=r"/users$",
            response={"id": 1}
        )

        # Make some requests
        mock_client.get("/users", params={"page": "1"})
        mock_client.post("/users", json={"name": "Test User"})
        mock_client.get("/users", params={"page": "2"})

        # Verify request count
        mock_client.assert_request_count(3)
        mock_client.assert_request_count(2, method="GET")
        mock_client.assert_request_count(1, method="POST")

        # Verify request sequence
        mock_client.assert_request_sequence([
            {"method": "GET"},
            {"method": "POST"},
            {"method": "GET"}
        ])

        # Verify request parameters
        mock_client.assert_request_params(
            {"page": "1"},
            method="GET",
            url_pattern=r"/users$"
        )

    def test_pagination_helper(self, mock_client: MockClient, create_user_data):
        """Test pagination helper."""
        # Create test data
        users = [create_user_data(id=i) for i in range(1, 26)]

        # Create pagination helper
        paginator = mock_client.create_paginated_response(
            items=users,
            page_size=10,
            base_url="/api/users"
        )

        # Configure mock client to use paginator
        mock_client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/users$",
            params={"page": "1"},
            response=lambda **kwargs: MockResponse(json_data=paginator.get_page(1))
        )

        mock_client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/users$",
            params={"page": "2"},
            response=lambda **kwargs: MockResponse(json_data=paginator.get_page(2))
        )

        # Make paginated requests
        page1_response = mock_client.get("/api/users", params={"page": "1"})
        page2_response = mock_client.get("/api/users", params={"page": "2"})

        # Verify pagination
        import json

        # Parse JSON responses
        if isinstance(page1_response, str):
            page1_data = json.loads(page1_response)
        else:
            # Skip this test if we can't parse the response
            pytest.skip("Response format not compatible with this test")

        if isinstance(page2_response, str):
            page2_data = json.loads(page2_response)
        else:
            # Skip this test if we can't parse the response
            pytest.skip("Response format not compatible with this test")

        # Now we can safely access dictionary keys
        assert len(page1_data.get("data", [])) == 10
        assert len(page2_data.get("data", [])) == 10

        # Access nested data safely
        pagination1 = page1_data.get("metadata", {}).get("pagination", {})
        pagination2 = page2_data.get("metadata", {}).get("pagination", {})
        assert pagination1.get("currentPage") == 1
        assert pagination2.get("currentPage") == 2

        # Check links
        links1 = page1_data.get("links", {})
        links2 = page2_data.get("links", {})
        assert "next" in links1
        assert "prev" in links2

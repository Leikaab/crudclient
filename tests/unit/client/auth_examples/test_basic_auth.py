"""
Examples of using Basic Authentication mocking utilities.

This module demonstrates how to use the Basic Authentication mocking utilities
in real-world testing scenarios.
"""

import pytest
from apiconfig.testing.auth_verification import AuthHeaderVerification

from crudclient.exceptions import AuthenticationError

from .common import create_mock_client


class TestBasicAuthExamples:
    """Examples of using Basic Authentication mocks."""

    def test_basic_auth_success_scenario(self):
        """Example of testing a successful Basic Auth scenario."""
        # Create a mock client with Basic Auth
        client = create_mock_client(auth_type="basic", auth_config={"username": "testuser", "password": "testpass"})

        # Configure a successful response
        client.with_response_pattern(method="GET", path_pattern=r"/api/users", data={"data": [{"id": 1, "name": "Test User"}]})

        # Make a request
        response = client.get("/api/users")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Test User"

        # Verify the auth header was sent correctly
        assert client.get_call_count() == 1
        request = client.get_calls()[0]
        assert "Authorization" in request.kwargs["headers"]
        assert request.kwargs["headers"]["Authorization"].startswith("Basic ")

        # Use verification helpers
        assert AuthHeaderVerification.verify_basic_auth_header(
            request.kwargs["headers"]["Authorization"],
            expected_username="testuser",
            expected_password="testpass",
        )

    def test_basic_auth_failure_scenario(self):
        """Example of testing a Basic Auth failure scenario."""
        # Create a mock client with Basic Auth configured to fail
        client = create_mock_client(
            auth_type="basic",
            auth_config={
                "username": "testuser",
                "password": "wrong_password",
                "should_fail": True,
                "failure_type": "invalid_credentials",
                "status_code": 401,
                "message": "Invalid username or password",
            },
        )

        # Configure an auth error response
        client.with_response_pattern(
            method="GET", path_pattern=r"/api/users", data={"error": "Unauthorized", "message": "Invalid username or password"}, status_code=401
        )

        # Make a request and expect it to fail
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/users")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "Invalid username or password" in str(excinfo.value)

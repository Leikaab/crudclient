"""
Examples of using Basic Authentication mocking utilities.

This module demonstrates how to use the Basic Authentication mocking utilities
in real-world testing scenarios.
"""

from .common import (
    pytest, AuthenticationError, create_mock_client,
    create_basic_auth_mock, AuthVerificationHelpers
)


class TestBasicAuthExamples:
    """Examples of using Basic Authentication mocks."""

    def test_basic_auth_success_scenario(self):
        """Example of testing a successful Basic Auth scenario."""
        # Create a mock client with Basic Auth
        client = create_mock_client(
            auth_type="basic",
            auth_config={
                "username": "testuser",
                "password": "testpass"
            }
        )

        # Configure a successful response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/users",
            response={"data": [{"id": 1, "name": "Test User"}]}
        )

        # Make a request
        response = client.get("/api/users")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Test User"

        # Verify the auth header was sent correctly
        assert len(client.request_history) == 1
        request = client.request_history[0]
        assert "Authorization" in request.headers
        assert request.headers["Authorization"].startswith("Basic ")

        # Use verification helpers
        assert AuthVerificationHelpers.verify_basic_auth_header(request.headers["Authorization"])
        username, password = AuthVerificationHelpers.extract_basic_auth_credentials(
            request.headers["Authorization"]
        )
        assert username == "testuser"
        assert password == "testpass"

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
                "message": "Invalid username or password"
            }
        )

        # Configure an auth error response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/users",
            response={
                "error": "Unauthorized",
                "message": "Invalid username or password"
            },
            status_code=401
        )

        # Make a request and expect it to fail
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/users")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "Invalid username or password" in str(excinfo.value)

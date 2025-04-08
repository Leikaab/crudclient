"""
Examples of using API Key Authentication mocking utilities.

This module demonstrates how to use the API Key Authentication mocking utilities
in real-world testing scenarios.
"""

from .common import (
    pytest, AuthenticationError, create_mock_client,
    create_api_key_auth_mock, AuthVerificationHelpers
)


class TestApiKeyAuthExamples:
    """Examples of using API Key Authentication mocks."""

    def test_api_key_header_auth_success_scenario(self):
        """Example of testing a successful API Key header auth scenario."""
        # Create a mock client with API Key header auth
        client = create_mock_client(
            auth_type="apikey",
            auth_config={
                "api_key": "valid_api_key",
                "header_name": "X-API-Key"
            }
        )

        # Configure a successful response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/data",
            response={"data": [{"id": 1, "value": "Test Data"}]}
        )

        # Make a request
        response = client.get("/api/data")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["value"] == "Test Data"

        # Verify the auth header was sent correctly
        assert len(client.request_history) == 1
        request = client.request_history[0]
        assert "X-API-Key" in request.headers
        assert request.headers["X-API-Key"] == "valid_api_key"

    def test_api_key_param_auth_success_scenario(self):
        """Example of testing a successful API Key param auth scenario."""
        # Create a mock client with API Key param auth
        client = create_mock_client(
            auth_type="apikey",
            auth_config={
                "api_key": "valid_api_key",
                "param_name": "api_key"
            }
        )

        # Configure a successful response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/data",
            response={"data": [{"id": 1, "value": "Test Data"}]}
        )

        # Make a request
        response = client.get("/api/data")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["value"] == "Test Data"

        # Verify the auth param was sent correctly
        assert len(client.request_history) == 1
        request = client.request_history[0]
        assert "api_key=valid_api_key" in request.url

    def test_api_key_auth_failure_scenario(self):
        """Example of testing an API Key auth failure scenario."""
        # Create a mock client with API Key auth configured to fail
        client = create_mock_client(
            auth_type="apikey",
            auth_config={
                "api_key": "invalid_api_key",
                "header_name": "X-API-Key",
                "should_fail": True,
                "failure_type": "invalid_api_key",
                "status_code": 401,
                "message": "Invalid API Key"
            }
        )

        # Configure an auth error response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/data",
            response={
                "error": "Unauthorized",
                "message": "Invalid API Key"
            },
            status_code=401
        )

        # Make a request and expect it to fail
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/data")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "Invalid API Key" in str(excinfo.value)

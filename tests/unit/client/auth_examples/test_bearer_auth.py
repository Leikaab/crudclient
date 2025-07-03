"""
Examples of using Bearer Authentication mocking utilities.

This module demonstrates how to use the Bearer Authentication mocking utilities
in real-world testing scenarios.
"""

import pytest

from crudclient.exceptions import AuthenticationError

from .common import create_mock_client


class TestBearerAuthExamples:
    """Examples of using Bearer Authentication mocks."""

    def test_bearer_auth_success_scenario(self) -> None:
        """Example of testing a successful Bearer Auth scenario."""
        # Create a mock client with Bearer Auth
        client = create_mock_client(auth_type="bearer", auth_config={"token": "valid_token"})

        # Configure a successful response
        client.with_response_pattern(method="GET", path_pattern=r"/api/resources", data={"data": [{"id": 1, "name": "Resource 1"}]})

        # Make a request
        response = client.get("/api/resources")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Resource 1"

        # Verify the auth header was sent correctly
        assert client.get_call_count() == 1
        calls = client.get_calls()
        request_call = calls[0]
        assert "Authorization" in request_call.kwargs["headers"]
        assert request_call.kwargs["headers"]["Authorization"] == "Bearer valid_token"

    def test_bearer_auth_token_expiration_scenario(self) -> None:
        """Example of testing a Bearer Auth token expiration scenario."""
        # Create a mock client with Bearer Auth configured with an expired token
        client = create_mock_client(auth_type="bearer", auth_config={"token": "expired_token", "token_expired": True})

        # Configure an auth error response for expired token
        client.with_response_pattern(
            method="GET", path_pattern=r"/api/resources", data={"error": "Unauthorized", "message": "Token expired"}, status_code=401
        )

        # Make a request and expect it to fail
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/resources")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "Token expired" in str(excinfo.value)

    def test_bearer_auth_token_refresh_scenario(self) -> None:
        """Example of testing a Bearer Auth token refresh scenario."""
        # Create a mock client with Bearer Auth configured. The initial token value
        # doesn't matter much as the first request will be intercepted by the 401 pattern.
        client = create_mock_client(
            auth_type="bearer", auth_config={"token": "expired_token", "refresh_token": "valid_refresh_token"}  # May be needed by auth logic
        )

        # Configure an auth error response for expired token
        client.with_response_pattern(
            method="GET", path_pattern=r"/api/resources", data={"error": "Unauthorized", "message": "Token expired"}, status_code=401
        )

        # Configure the token refresh endpoint response
        client.with_response_pattern(
            method="POST",
            path_pattern=r"/oauth/token",
            data={"access_token": "new_token", "refresh_token": "new_refresh_token", "expires_in": 3600},
        )

        # In a real implementation, the client would handle token refresh automatically
        # For this example, we'll simulate the refresh process manually

        # First attempt should fail with 401 due to the configured response pattern
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/resources")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "Token expired" in str(excinfo.value)

        # Now simulate the token refresh process
        # In a real implementation, this would be handled by the client
        refresh_response = client.post("/oauth/token", json={"grant_type": "refresh_token", "refresh_token": "valid_refresh_token"})

        # Update the auth strategy with a new BearerAuth instance
        # (apiconfig's BearerAuth is immutable, so we need to create a new one)
        from crudclient.testing.auth import create_bearer_auth_mock

        new_bearer_mock = create_bearer_auth_mock(token=refresh_response["access_token"])
        client.set_auth_strategy(new_bearer_mock.get_auth_strategy())

        # Now configure the successful response for the resource endpoint *after* the failed attempt
        client.with_response_pattern(
            method="GET",
            path_pattern=r"/api/resources",
            data={"data": [{"id": 1, "name": "Resource 1"}]},
            status_code=200,  # Ensure status code is set for success
        )

        # Try the request again with the (hopefully) updated token
        response = client.get("/api/resources")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Resource 1"

        # Optionally, verify the correct token was used in the second GET request header
        assert client.get_call_count() == 3  # Initial GET, POST refresh, Second GET
        calls = client.get_calls()
        second_get_request = calls[2]
        assert "Authorization" in second_get_request.kwargs["headers"]
        assert second_get_request.kwargs["headers"]["Authorization"] == "Bearer new_token"

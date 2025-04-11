"""
Examples of using Bearer Authentication mocking utilities.

This module demonstrates how to use the Bearer Authentication mocking utilities
in real-world testing scenarios.
"""

import pytest

from crudclient.auth.bearer import BearerAuth  # Added import
from crudclient.exceptions import AuthenticationError

from .common import create_mock_client


class TestBearerAuthExamples:
    """Examples of using Bearer Authentication mocks."""

    def test_bearer_auth_success_scenario(self):
        """Example of testing a successful Bearer Auth scenario."""
        # Create a mock client with Bearer Auth
        client = create_mock_client(auth_type="bearer", auth_config={"token": "valid_token"})

        # Configure a successful response
        client.with_response_pattern(method="GET", url_pattern=r"/api/resources", response={"data": [{"id": 1, "name": "Resource 1"}]})

        # Make a request
        response = client.get("/api/resources")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Resource 1"

        # Verify the auth header was sent correctly
        assert len(client.request_history) == 1
        request = client.request_history[0]
        assert "Authorization" in request["headers"]
        assert request["headers"]["Authorization"] == "Bearer valid_token"

    def test_bearer_auth_token_expiration_scenario(self):
        """Example of testing a Bearer Auth token expiration scenario."""
        # Create a mock client with Bearer Auth configured with an expired token
        client = create_mock_client(auth_type="bearer", auth_config={"token": "expired_token", "token_expired": True})

        # Configure an auth error response for expired token
        client.with_response_pattern(
            method="GET", url_pattern=r"/api/resources", response={"error": "Unauthorized", "message": "Token expired"}, status_code=401
        )

        # Make a request and expect it to fail
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/resources")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "Token expired" in str(excinfo.value)

    def test_bearer_auth_token_refresh_scenario(self):
        """Example of testing a Bearer Auth token refresh scenario."""
        # Create a mock client with Bearer Auth configured. The initial token value
        # doesn't matter much as the first request will be intercepted by the 401 pattern.
        client = create_mock_client(
            auth_type="bearer", auth_config={"token": "expired_token", "refresh_token": "valid_refresh_token"}  # May be needed by auth logic
        )

        # Configure an auth error response for expired token
        client.with_response_pattern(
            method="GET", url_pattern=r"/api/resources", response={"error": "Unauthorized", "message": "Token expired"}, status_code=401
        )

        # Configure the token refresh endpoint response
        client.with_response_pattern(
            method="POST",
            url_pattern=r"/oauth/token",
            response={"access_token": "new_token", "refresh_token": "new_refresh_token", "expires_in": 3600},
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

        # Update the token within the client's BearerAuth strategy instance
        auth_strategy = client.get_auth_strategy()
        assert auth_strategy is not None, "Auth strategy should be set"
        # Ensure it's a BearerAuth instance before accessing .token
        if isinstance(auth_strategy, BearerAuth):
            auth_strategy.token = refresh_response["access_token"]
        else:
            pytest.fail(f"Expected BearerAuth strategy, but got {type(auth_strategy)}")

        # Now configure the successful response for the resource endpoint *after* the failed attempt
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/resources",
            response={"data": [{"id": 1, "name": "Resource 1"}]},
            status_code=200,  # Ensure status code is set for success
        )

        # Try the request again with the (hopefully) updated token
        response = client.get("/api/resources")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Resource 1"

        # Optionally, verify the correct token was used in the second GET request header
        assert len(client.request_history) == 3  # Initial GET, POST refresh, Second GET
        second_get_request = client.request_history[2]
        assert "Authorization" in second_get_request["headers"]
        assert second_get_request["headers"]["Authorization"] == "Bearer new_token"

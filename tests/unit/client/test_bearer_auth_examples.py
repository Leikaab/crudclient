import pytest

from crudclient.exceptions import AuthenticationError
from tests.unit.client.auth_examples.common import create_mock_client


class TestBearerAuthExamples:
    """Examples of using Bearer Authentication mocks."""

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_bearer_auth_success_scenario(self):
        """Example of testing a successful Bearer Auth scenario."""
        # Create a mock client with Bearer Auth
        client = create_mock_client(
            auth_type="bearer",
            auth_config={
                "token": "valid_token"
            }
        )

        # Configure a successful response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/resources",
            response={"data": [{"id": 1, "name": "Resource 1"}]}
        )

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

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_bearer_auth_token_expiration_scenario(self):
        """Example of testing a Bearer Auth token expiration scenario."""
        # Create a mock client with Bearer Auth configured with an expired token
        client = create_mock_client(
            auth_type="bearer",
            auth_config={
                "token": "expired_token",
                "token_expired": True
            }
        )

        # Configure an auth error response for expired token
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/resources",
            response={
                "error": "Unauthorized",
                "message": "Token expired"
            },
            status_code=401
        )

        # Make a request and expect it to fail
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/resources")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "Token expired" in str(excinfo.value)

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_bearer_auth_token_refresh_scenario(self):
        """Example of testing a Bearer Auth token refresh scenario."""
        # Create a mock client with Bearer Auth configured with an expired token that can be refreshed
        client = create_mock_client(
            auth_type="bearer",
            auth_config={
                "token": "expired_token",
                "token_expired": True,
                "refresh_token": "valid_refresh_token"
            }
        )

        # Configure an auth error response for expired token
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/resources",
            response={
                "error": "Unauthorized",
                "message": "Token expired"
            },
            status_code=401
        )

        # Configure a token refresh response
        client.with_response_pattern(
            method="POST",
            url_pattern=r"/oauth/token",
            response={
                "access_token": "new_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 3600
            }
        )

        # Configure a successful response for the retry with new token
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/resources",
            response={"data": [{"id": 1, "name": "Resource 1"}]},
            headers={"Authorization": "Bearer new_token"}
        )

        # In a real implementation, the client would handle token refresh automatically
        # For this example, we'll simulate the refresh process manually

        # First attempt will fail with 401
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/resources")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "Token expired" in str(excinfo.value)

        # Now simulate token refresh
        # In a real implementation, this would be handled by the client
        refresh_response = client.post("/oauth/token", json={
            "grant_type": "refresh_token",
            "refresh_token": "valid_refresh_token"
        })

        # Update the client's auth header with the new token
        client.http_client.session_manager.session.headers["Authorization"] = f"Bearer {refresh_response['access_token']}"

        # Try the request again with the new token
        response = client.get("/api/resources")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Resource 1"

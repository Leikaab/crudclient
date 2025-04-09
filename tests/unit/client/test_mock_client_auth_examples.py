"""
Examples of using the authentication mocking utilities.

This module demonstrates how to use the authentication mocking utilities
in real-world testing scenarios.
"""

import pytest

from crudclient.config import ClientConfig
from crudclient.exceptions import AuthenticationError
from crudclient.testing.auth import AuthVerificationHelpers, create_custom_auth_mock
from tests.unit.client.auth_examples.common import create_mock_client


class TestBasicAuthExamples:
    """Examples of using Basic Authentication mocks."""

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
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
        assert "Authorization" in request["headers"]
        assert request["headers"]["Authorization"].startswith("Basic ")

        # Use verification helpers
        assert AuthVerificationHelpers.verify_basic_auth_header(request["headers"]["Authorization"])
        username, password = AuthVerificationHelpers.extract_basic_auth_credentials(
            request["headers"]["Authorization"]
        )
        assert username == "testuser"
        assert password == "testpass"

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
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


class TestApiKeyAuthExamples:
    """Examples of using API Key Authentication mocks."""

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
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
        assert "X-API-Key" in request["headers"]
        assert request["headers"]["X-API-Key"] == "valid_api_key"

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
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
        assert "api_key=valid_api_key" in request["path"]


class TestCustomAuthExamples:
    """Examples of using Custom Authentication mocks."""

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_custom_auth_success_scenario(self):
        """Example of testing a successful Custom Auth scenario."""
        # Define custom auth callbacks
        def header_callback():
            return {
                "X-Custom-Auth": "custom_value",
                "X-Timestamp": "12345678"
            }

        def param_callback():
            return {"tenant": "test_tenant"}

        # Create a mock client with Custom Auth
        client = create_mock_client(
            auth_type="custom",
            auth_config={
                "header_callback": header_callback,
                "param_callback": param_callback
            }
        )

        # Configure a successful response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/custom",
            response={"data": [{"id": 1, "name": "Custom Data"}]}
        )

        # Make a request
        response = client.get("/api/custom")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Custom Data"

        # Verify the auth headers and params were sent correctly
        assert len(client.request_history) == 1
        request = client.request_history[0]
        assert "X-Custom-Auth" in request["headers"]
        assert request["headers"]["X-Custom-Auth"] == "custom_value"
        assert "X-Timestamp" in request["headers"]
        assert request["headers"]["X-Timestamp"] == "12345678"
        assert "tenant=test_tenant" in request["path"]

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_custom_auth_failure_scenario(self):
        """Example of testing a Custom Auth failure scenario."""
        # Define a custom auth callback that will fail
        def failing_header_callback():
            raise ValueError("Failed to generate auth headers")

        # Create a mock client with failing Custom Auth
        client = create_mock_client(
            config=ClientConfig(hostname="https://api.example.com", version="v1")
        )

        # Set up the auth strategy manually
        auth_mock = create_custom_auth_mock(header_callback=failing_header_callback)
        client.config.auth_strategy = auth_mock.get_auth_strategy()

        # Configure a response (though it won't be reached)
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/custom",
            response={"data": [{"id": 1, "name": "Custom Data"}]}
        )

        # Make a request and expect it to fail
        with pytest.raises(ValueError) as excinfo:
            client.get("/api/custom")

        # Verify the error
        assert "Failed to generate auth headers" in str(excinfo.value)


class TestMultiFactorAuthExamples:
    """Examples of using Multi-Factor Authentication mocks."""

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_mfa_required_scenario(self):
        """Example of testing an MFA required scenario."""
        # Create a mock client with Bearer Auth that requires MFA
        client = create_mock_client(
            auth_type="bearer",
            auth_config={
                "token": "valid_token",
                "mfa_required": True,
                "mfa_verified": False
            }
        )

        # Configure an MFA required response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/secure",
            response={
                "error": "Unauthorized",
                "message": "MFA verification required"
            },
            status_code=401
        )

        # Make a request and expect it to fail
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/secure")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "MFA verification required" in str(excinfo.value)

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_mfa_verification_success_scenario(self):
        """Example of testing a successful MFA verification scenario."""
        # Create a mock client with Bearer Auth that requires MFA
        client = create_mock_client(
            auth_type="bearer",
            auth_config={
                "token": "valid_token",
                "mfa_required": True,
                "mfa_verified": False
            }
        )

        # Configure an MFA required response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/secure",
            response={
                "error": "Unauthorized",
                "message": "MFA verification required"
            },
            status_code=401
        )

        # Configure an MFA verification response
        client.with_response_pattern(
            method="POST",
            url_pattern=r"/api/mfa/verify",
            response={
                "status": "success",
                "message": "MFA verified successfully"
            }
        )

        # Configure a successful response after MFA verification
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/secure",
            response={"data": [{"id": 1, "name": "Secure Data"}]},
            headers={"X-MFA-Verified": "true"}
        )

        # First attempt will fail with 401
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/secure")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "MFA verification required" in str(excinfo.value)

        # Now verify MFA
        mfa_response = client.post("/api/mfa/verify", json={
            "code": "123456"
        })

        # Verify the MFA response
        assert mfa_response["status"] == "success"

        # Update the client's headers to include MFA verification
        client.http_client.session_manager.session.headers["X-MFA-Verified"] = "true"

        # Try the request again with MFA verified
        response = client.get("/api/secure")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Secure Data"

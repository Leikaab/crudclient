"""
Tests for authentication mocking utilities.

This module contains tests for the authentication mocking utilities,
including specialized mock factories for Basic, Bearer, and Custom auth strategies.
"""

import base64
import pytest
from unittest.mock import MagicMock

from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import ApiKeyAuth, CustomAuth
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.exceptions import AuthenticationError

from .auth import (
    BasicAuthMock, BearerAuthMock, ApiKeyAuthMock, CustomAuthMock,
    create_basic_auth_mock, create_bearer_auth_mock,
    create_api_key_auth_mock, create_custom_auth_mock,
    AuthVerificationHelpers
)
from .factory import create_mock_client


class TestBasicAuthMock:
    """Tests for BasicAuthMock."""

    def test_basic_auth_mock_creation(self):
        """Test creating a BasicAuthMock."""
        # Arrange & Act
        auth_mock = create_basic_auth_mock(username="testuser", password="testpass")

        # Assert
        assert isinstance(auth_mock, BasicAuthMock)
        assert auth_mock.username == "testuser"
        assert auth_mock.password == "testpass"

        # Verify the auth strategy
        auth_strategy = auth_mock.get_auth_strategy()
        assert isinstance(auth_strategy, BasicAuth)
        assert auth_strategy.username == "testuser"
        assert auth_strategy.password == "testpass"

        # Verify headers
        headers = auth_strategy.prepare_request_headers()
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")

        # Decode and verify credentials
        encoded_part = headers["Authorization"][6:]  # Skip "Basic "
        decoded = base64.b64decode(encoded_part).decode('utf-8')
        assert decoded == "testuser:testpass"

    def test_basic_auth_mock_chainable_config(self):
        """Test chainable configuration of BasicAuthMock."""
        # Arrange & Act
        auth_mock = (create_basic_auth_mock()
                     .with_credentials("newuser", "newpass")
                     .with_failure(failure_type="invalid_credentials", status_code=401)
                     .with_custom_header("X-Custom", "value"))

        # Assert
        assert auth_mock.username == "newuser"
        assert auth_mock.password == "newpass"
        assert auth_mock.should_fail is True
        assert auth_mock.failure_type == "invalid_credentials"
        assert auth_mock.failure_status_code == 401
        assert auth_mock.custom_headers == {"X-Custom": "value"}

    def test_basic_auth_verification(self):
        """Test verification helpers for Basic Auth."""
        # Arrange
        auth_mock = create_basic_auth_mock(username="testuser", password="testpass")
        auth_strategy = auth_mock.get_auth_strategy()
        headers = auth_strategy.prepare_request_headers()

        # Act & Assert
        assert auth_mock.verify_auth_header(headers["Authorization"]) is True
        assert AuthVerificationHelpers.verify_basic_auth_header(headers["Authorization"]) is True

        # Test with invalid header
        assert auth_mock.verify_auth_header("NotBasic xyz") is False
        assert AuthVerificationHelpers.verify_basic_auth_header("NotBasic xyz") is False

        # Test credential extraction
        username, password = AuthVerificationHelpers.extract_basic_auth_credentials(headers["Authorization"])
        assert username == "testuser"
        assert password == "testpass"


class TestBearerAuthMock:
    """Tests for BearerAuthMock."""

    def test_bearer_auth_mock_creation(self):
        """Test creating a BearerAuthMock."""
        # Arrange & Act
        auth_mock = create_bearer_auth_mock(token="test_token")

        # Assert
        assert isinstance(auth_mock, BearerAuthMock)
        assert auth_mock.token == "test_token"

        # Verify the auth strategy
        auth_strategy = auth_mock.get_auth_strategy()
        assert isinstance(auth_strategy, BearerAuth)
        assert auth_strategy.token == "test_token"

        # Verify headers
        headers = auth_strategy.prepare_request_headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token"

    def test_bearer_auth_mock_token_expiration(self):
        """Test token expiration in BearerAuthMock."""
        # Arrange
        auth_mock = create_bearer_auth_mock().with_expired_token()

        # Act & Assert
        assert auth_mock.is_token_expired() is True
        assert auth_mock.should_fail_auth() is True

        # Test with refresh token
        auth_mock = (create_bearer_auth_mock()
                     .with_expired_token()
                     .with_refresh_token("refresh_token"))

        # First check should indicate expired but not fail due to refresh capability
        assert auth_mock.is_token_expired() is True
        assert auth_mock.can_refresh_token() is True
        assert auth_mock.should_fail_auth() is False

        # Refresh the token
        assert auth_mock.refresh() is True
        assert auth_mock.is_token_expired() is False
        assert auth_mock.token != "valid_token"  # Token should be changed
        assert auth_mock.token in auth_mock.issued_tokens  # New token should be tracked

    def test_bearer_auth_mock_chainable_config(self):
        """Test chainable configuration of BearerAuthMock."""
        # Arrange & Act
        auth_mock = (create_bearer_auth_mock()
                     .with_token("new_token")
                     .with_token_expiration(expires_in_seconds=3600)
                     .with_refresh_token("refresh_token", max_refresh_attempts=5)
                     .with_custom_header("X-Custom", "value"))

        # Assert
        assert auth_mock.token == "new_token"
        assert auth_mock.token_expired is False
        assert auth_mock.token_expiry_time is not None
        assert auth_mock.refresh_token == "refresh_token"
        assert auth_mock.max_refresh_attempts == 5
        assert auth_mock.custom_headers == {"X-Custom": "value"}

    def test_bearer_auth_verification(self):
        """Test verification helpers for Bearer Auth."""
        # Arrange
        auth_mock = create_bearer_auth_mock(token="test_token")
        auth_strategy = auth_mock.get_auth_strategy()
        headers = auth_strategy.prepare_request_headers()

        # Act & Assert
        assert auth_mock.verify_auth_header(headers["Authorization"]) is True
        assert AuthVerificationHelpers.verify_bearer_auth_header(headers["Authorization"]) is True

        # Test with invalid header
        assert auth_mock.verify_auth_header("NotBearer xyz") is False
        assert AuthVerificationHelpers.verify_bearer_auth_header("NotBearer xyz") is False

        # Test token extraction
        token = AuthVerificationHelpers.extract_bearer_token(headers["Authorization"])
        assert token == "test_token"

        # Test token usage verification
        assert auth_mock.verify_token_usage("test_token") is True
        assert auth_mock.verify_token_usage("wrong_token") is False


class TestApiKeyAuthMock:
    """Tests for ApiKeyAuthMock."""

    def test_api_key_auth_mock_header_creation(self):
        """Test creating an ApiKeyAuthMock with header authentication."""
        # Arrange & Act
        auth_mock = create_api_key_auth_mock(
            api_key="test_api_key",
            header_name="X-API-Key"
        )

        # Assert
        assert isinstance(auth_mock, ApiKeyAuthMock)
        assert auth_mock.api_key == "test_api_key"
        assert auth_mock.header_name == "X-API-Key"
        assert auth_mock.param_name is None

        # Verify the auth strategy
        auth_strategy = auth_mock.get_auth_strategy()
        assert isinstance(auth_strategy, ApiKeyAuth)

        # Verify headers
        headers = auth_strategy.prepare_request_headers()
        assert "X-API-Key" in headers
        assert headers["X-API-Key"] == "test_api_key"

        # Verify params
        params = auth_strategy.prepare_request_params()
        assert params == {}

    def test_api_key_auth_mock_param_creation(self):
        """Test creating an ApiKeyAuthMock with parameter authentication."""
        # Arrange & Act
        auth_mock = create_api_key_auth_mock(
            api_key="test_api_key",
            header_name=None,
            param_name="api_key"
        )

        # Assert
        assert isinstance(auth_mock, ApiKeyAuthMock)
        assert auth_mock.api_key == "test_api_key"
        assert auth_mock.header_name is None
        assert auth_mock.param_name == "api_key"

        # Verify the auth strategy
        auth_strategy = auth_mock.get_auth_strategy()
        assert isinstance(auth_strategy, ApiKeyAuth)

        # Verify headers
        headers = auth_strategy.prepare_request_headers()
        assert headers == {}

        # Verify params
        params = auth_strategy.prepare_request_params()
        assert "api_key" in params
        assert params["api_key"] == "test_api_key"

    def test_api_key_auth_mock_chainable_config(self):
        """Test chainable configuration of ApiKeyAuthMock."""
        # Arrange & Act - Header auth
        header_auth_mock = (create_api_key_auth_mock()
                            .with_api_key("new_api_key")
                            .as_header("X-Custom-API-Key")
                            .with_failure(failure_type="invalid_api_key"))

        # Assert - Header auth
        assert header_auth_mock.api_key == "new_api_key"
        assert header_auth_mock.header_name == "X-Custom-API-Key"
        assert header_auth_mock.param_name is None
        assert header_auth_mock.should_fail is True
        assert header_auth_mock.failure_type == "invalid_api_key"

        # Arrange & Act - Param auth
        param_auth_mock = (create_api_key_auth_mock()
                           .with_api_key("new_api_key")
                           .as_param("custom_api_key")
                           .with_failure(failure_type="invalid_api_key"))

        # Assert - Param auth
        assert param_auth_mock.api_key == "new_api_key"
        assert param_auth_mock.header_name is None
        assert param_auth_mock.param_name == "custom_api_key"
        assert param_auth_mock.should_fail is True
        assert param_auth_mock.failure_type == "invalid_api_key"


class TestCustomAuthMock:
    """Tests for CustomAuthMock."""

    def test_custom_auth_mock_creation(self):
        """Test creating a CustomAuthMock."""
        # Arrange
        def header_callback():
            return {"X-Custom-Auth": "custom_value"}

        def param_callback():
            return {"custom_param": "param_value"}

        # Act
        auth_mock = create_custom_auth_mock(
            header_callback=header_callback,
            param_callback=param_callback
        )

        # Assert
        assert isinstance(auth_mock, CustomAuthMock)
        assert auth_mock.header_callback == header_callback
        assert auth_mock.param_callback == param_callback

        # Verify the auth strategy
        auth_strategy = auth_mock.get_auth_strategy()
        assert isinstance(auth_strategy, CustomAuth)

        # Verify headers
        headers = auth_strategy.prepare_request_headers()
        assert "X-Custom-Auth" in headers
        assert headers["X-Custom-Auth"] == "custom_value"

        # Verify params
        params = auth_strategy.prepare_request_params()
        assert "custom_param" in params
        assert params["custom_param"] == "param_value"

    def test_custom_auth_mock_failing_callback(self):
        """Test CustomAuthMock with a failing callback."""
        # Arrange & Act
        auth_mock = create_custom_auth_mock().with_failing_callback("Test failure")
        auth_strategy = auth_mock.get_auth_strategy()

        # Assert
        with pytest.raises(ValueError, match="Test failure"):
            auth_strategy.prepare_request_headers()

    def test_custom_auth_mock_chainable_config(self):
        """Test chainable configuration of CustomAuthMock."""
        # Arrange
        def new_header_callback():
            return {"X-New-Auth": "new_value"}

        def new_param_callback():
            return {"new_param": "new_value"}

        # Act
        auth_mock = (create_custom_auth_mock()
                     .with_header_callback(new_header_callback)
                     .with_param_callback(new_param_callback)
                     .with_mfa_required(verified=False))

        # Assert
        assert auth_mock.header_callback == new_header_callback
        assert auth_mock.param_callback == new_param_callback
        assert auth_mock.mfa_required is True
        assert auth_mock.mfa_verified is False


class TestAuthMockIntegration:
    """Tests for integrating auth mocks with the mock client."""

    def test_mock_client_with_basic_auth(self):
        """Test creating a mock client with Basic Auth."""
        # Arrange & Act
        client = create_mock_client(
            auth_type="basic",
            auth_config={
                "username": "testuser",
                "password": "testpass"
            }
        )

        # Assert
        assert client.config.auth_strategy is not None
        assert isinstance(client.config.auth_strategy, BasicAuth)
        assert client.config.auth_strategy.username == "testuser"
        assert client.config.auth_strategy.password == "testpass"

    def test_mock_client_with_bearer_auth(self):
        """Test creating a mock client with Bearer Auth."""
        # Arrange & Act
        client = create_mock_client(
            auth_type="bearer",
            auth_config={
                "token": "test_token",
                "token_expired": True,
                "refresh_token": "refresh_token"
            }
        )

        # Assert
        assert client.config.auth_strategy is not None
        assert isinstance(client.config.auth_strategy, BearerAuth)
        assert client.config.auth_strategy.token == "test_token"

    def test_mock_client_with_api_key_auth(self):
        """Test creating a mock client with API Key Auth."""
        # Arrange & Act
        client = create_mock_client(
            auth_type="apikey",
            auth_config={
                "api_key": "test_api_key",
                "header_name": "X-API-Key"
            }
        )

        # Assert
        assert client.config.auth_strategy is not None
        assert isinstance(client.config.auth_strategy, ApiKeyAuth)

        # Verify headers
        headers = client.config.auth_strategy.prepare_request_headers()
        assert "X-API-Key" in headers
        assert headers["X-API-Key"] == "test_api_key"

    def test_mock_client_with_custom_auth(self):
        """Test creating a mock client with Custom Auth."""
        # Arrange
        def header_callback():
            return {"X-Custom-Auth": "custom_value"}

        # Act
        client = create_mock_client(
            auth_type="custom",
            auth_config={
                "header_callback": header_callback
            }
        )

        # Assert
        assert client.config.auth_strategy is not None
        assert isinstance(client.config.auth_strategy, CustomAuth)

        # Verify headers
        headers = client.config.auth_strategy.prepare_request_headers()
        assert "X-Custom-Auth" in headers
        assert headers["X-Custom-Auth"] == "custom_value"

    def test_auth_verification_helpers_with_mock_client(self):
        """Test using auth verification helpers with a mock client."""
        # Arrange
        client = create_mock_client(
            auth_type="bearer",
            auth_config={
                "token": "test_token"
            }
        )

        # Configure a successful response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/resource",
            response={"data": "success"}
        )

        # Act
        response = client.get("/api/resource")

        # Assert
        # Check that the request was made with the correct auth header
        assert len(client.request_history) == 1
        request = client.request_history[0]
        assert "Authorization" in request.headers
        assert request.headers["Authorization"] == "Bearer test_token"

        # Use verification helpers
        assert AuthVerificationHelpers.verify_bearer_auth_header(request.headers["Authorization"]) is True
        token = AuthVerificationHelpers.extract_bearer_token(request.headers["Authorization"])
        assert token == "test_token"

        # Use assertion helpers
        AuthVerificationHelpers.assert_auth_header_format(request.headers, "bearer")
        AuthVerificationHelpers.assert_token_usage(request.headers, "test_token", "bearer")


class TestAuthFailureScenarios:
    """Tests for authentication failure scenarios."""

    def test_expired_token_scenario(self):
        """Test handling of expired token scenario."""
        # Arrange
        client = create_mock_client(
            auth_type="bearer",
            auth_config={
                "token": "test_token",
                "token_expired": True
            }
        )

        # Configure an auth error response for expired token
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/resource",
            response={
                "error": "Unauthorized",
                "message": "Token expired"
            },
            status_code=401
        )

        # Act & Assert
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/resource")

        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "Token expired" in str(excinfo.value)

    def test_token_refresh_scenario(self):
        """Test token refresh scenario."""
        # Arrange
        # Create a mock for the auth strategy that can be refreshed
        auth_mock = create_bearer_auth_mock(token="old_token")
        auth_mock.with_expired_token().with_refresh_token("refresh_token")

        # Create a client config with our auth strategy
        config = ClientConfig(
            hostname="https://api.example.com",
            version="v1"
        )
        config.auth_strategy = auth_mock.get_auth_strategy()

        # Create a mock client
        client = create_mock_client(config=config)

        # Configure responses for token refresh and subsequent request
        client.with_response_pattern(
            method="POST",
            url_pattern=r"/oauth/token",
            response={
                "access_token": "new_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 3600
            }
        )

        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/resource",
            response={"data": "success"}
        )

        # Mock the refresh method
        original_refresh = auth_mock.refresh
        auth_mock.refresh = MagicMock(side_effect=original_refresh)

        # Act
        # This would normally trigger a token refresh in a real implementation
        # For our test, we'll manually refresh and then make the request
        auth_mock.refresh()
        response = client.get("/api/resource")

        # Assert
        assert auth_mock.refresh.called
        assert auth_mock.token != "old_token"
        assert not auth_mock.is_token_expired()

    def test_mfa_required_scenario(self):
        """Test multi-factor authentication required scenario."""
        # Arrange
        client = create_mock_client(
            auth_type="bearer",
            auth_config={
                "token": "test_token",
                "mfa_required": True,
                "mfa_verified": False
            }
        )

        # Configure an auth error response for MFA required
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/resource",
            response={
                "error": "Unauthorized",
                "message": "MFA verification required"
            },
            status_code=401
        )

        # Act & Assert
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/resource")

        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "MFA verification required" in str(excinfo.value)

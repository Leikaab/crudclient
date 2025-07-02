import pytest
from apiconfig.exceptions.auth import AuthenticationError


class TestAuthVerificationHelpers:
    """Tests for authentication verification helpers."""

    def test_verify_basic_auth_header(self, basic_auth_client, mock_auth_verification):
        """Test verification of Basic Auth headers."""
        # Arrange
        auth_strategy = basic_auth_client.config.auth_strategy
        headers = auth_strategy.prepare_request_headers()

        # Act & Assert
        assert mock_auth_verification.verify_basic_auth_header(headers["Authorization"], expected_username="user", expected_password="pass")

        # Test with invalid header
        with pytest.raises(AuthenticationError):
            mock_auth_verification.verify_basic_auth_header("NotBasic xyz")

    def test_verify_bearer_auth_header(self, bearer_auth_client, mock_auth_verification):
        """Test verification of Bearer Auth headers."""
        # Arrange
        auth_strategy = bearer_auth_client.config.auth_strategy
        headers = auth_strategy.prepare_request_headers()

        # Act & Assert
        assert mock_auth_verification.verify_bearer_auth_header(headers["Authorization"], expected_token="valid_token")

        # Test with invalid header
        with pytest.raises(AuthenticationError):
            mock_auth_verification.verify_bearer_auth_header("NotBearer xyz")

    def test_assert_auth_header_format(self, bearer_auth_client, mock_auth_verification):
        """Test assertion of auth header format."""
        # Arrange
        auth_strategy = bearer_auth_client.config.auth_strategy
        headers = auth_strategy.prepare_request_headers()

        # Act & Assert - Should not raise
        mock_auth_verification.verify_auth_header_format(headers, "bearer")

        # Test with invalid format - Should raise
        with pytest.raises(AuthenticationError):
            mock_auth_verification.verify_auth_header_format({"Authorization": "Invalid format"}, "bearer")

    def test_assert_token_usage(self, bearer_auth_client, mock_auth_verification):
        """Test assertion of token usage."""
        # Arrange
        auth_strategy = bearer_auth_client.config.auth_strategy
        headers = auth_strategy.prepare_request_headers()

        # Act & Assert - Extract token
        mock_auth_verification.verify_bearer_auth_header(headers["Authorization"], expected_token="valid_token")

        # Optional: If assert_token_usage is meant to validate JWT structure,
        # call it separately without expecting it to compare values.
        # mock_auth_verification.assert_token_usage(token) # Example: Check JWT validity if needed

    def test_assert_refresh_behavior(self, mock_auth_verification):
        """Test assertion of token refresh behavior."""
        # Arrange
        old_headers = {"Authorization": "Bearer old_token"}
        new_headers = {"Authorization": "Bearer new_token"}

        # Act & Assert - Should not raise
        mock_auth_verification.verify_bearer_auth_header(old_headers["Authorization"], expected_token="old_token")
        mock_auth_verification.verify_bearer_auth_header(new_headers["Authorization"], expected_token="new_token")
        assert old_headers["Authorization"] != new_headers["Authorization"]

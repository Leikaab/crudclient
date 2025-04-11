import re
from datetime import datetime, timedelta

from freezegun import freeze_time

from crudclient.auth.bearer import BearerAuth
from crudclient.testing.auth.bearer import BearerAuthMock


def test_bearer_auth_mock_init_defaults():
    """Test default initialization."""
    with freeze_time("2023-01-01 12:00:00"):
        mock = BearerAuthMock()
        assert mock.token == "valid_token"
        assert mock.issued_tokens == ["valid_token"]
        assert mock.revoked_tokens == set()
        assert mock.required_scopes == []
        assert mock.jwt_validation is False
        assert isinstance(mock.auth_strategy, BearerAuth)
        assert mock.auth_strategy.token == "valid_token"

        # Check default metadata
        assert "valid_token" in mock.token_metadata
        meta = mock.token_metadata["valid_token"]
        assert meta["issued_at"] == datetime(2023, 1, 1, 12, 0, 0)
        assert meta["expires_at"] == datetime(2023, 1, 1, 13, 0, 0)  # Default 1 hour expiry
        assert meta["scopes"] == ["read", "write"]
        assert meta["user_id"] == "default_user"
        assert meta["client_id"] == "default_client"


def test_bearer_auth_mock_init_custom_token():
    """Test initialization with a custom token."""
    with freeze_time("2023-01-01 12:00:00"):
        mock = BearerAuthMock(token="custom_token_123")
        assert mock.token == "custom_token_123"
        assert mock.issued_tokens == ["custom_token_123"]
        assert "custom_token_123" in mock.token_metadata
        assert mock.auth_strategy.token == "custom_token_123"


def test_with_token():
    """Test setting a new token."""
    with freeze_time("2023-01-01 12:00:00"):
        mock = BearerAuthMock(token="initial_token")
        mock.with_token("new_token_abc")
        assert mock.token == "new_token_abc"
        assert mock.issued_tokens == ["new_token_abc"]  # Overwrites issued tokens
        assert "new_token_abc" in mock.token_metadata
        assert "initial_token" not in mock.token_metadata  # Old metadata removed
        assert mock.auth_strategy.token == "new_token_abc"


def test_with_token_metadata():
    """Test updating token metadata."""
    mock = BearerAuthMock(token="my_token")
    mock.with_token_metadata(user_id="user1", client_id="client_xyz", scopes=["profile", "email"])
    meta = mock.token_metadata["my_token"]
    assert meta["user_id"] == "user1"
    assert meta["client_id"] == "client_xyz"
    assert meta["scopes"] == ["profile", "email"]


def test_with_token_expiration():
    """Test setting token expiration."""
    with freeze_time("2023-01-01 12:00:00") as frozen_time:
        mock = BearerAuthMock(token="expiring_token")
        mock.with_token_expiration(expires_in_seconds=60)  # Expires in 1 minute
        meta = mock.token_metadata["expiring_token"]
        assert meta["expires_at"] == datetime(2023, 1, 1, 12, 1, 0)

        # Test validation before expiry
        assert mock.validate_token("expiring_token") is True

        # Move time forward past expiry
        frozen_time.tick(delta=timedelta(seconds=61))
        assert mock.validate_token("expiring_token") is False


def test_with_token_expiration_for_specific_token():
    """Test setting expiration for a token other than the current one."""
    with freeze_time("2023-01-01 12:00:00") as frozen_time:
        mock = BearerAuthMock(token="current_token")
        # Manually add another token to metadata for testing this feature
        mock.issued_tokens.append("other_token")
        mock.token_metadata["other_token"] = mock.token_metadata["current_token"].copy()

        mock.with_token_expiration(expires_in_seconds=30, token="other_token")

        meta_other = mock.token_metadata["other_token"]
        assert meta_other["expires_at"] == datetime(2023, 1, 1, 12, 0, 30)

        meta_current = mock.token_metadata["current_token"]
        assert meta_current["expires_at"] == datetime(2023, 1, 1, 13, 0, 0)  # Unchanged

        frozen_time.tick(delta=timedelta(seconds=31))
        assert mock.validate_token("other_token") is False
        assert mock.validate_token("current_token") is True


def test_with_token_format_validation():
    """Test token format validation."""
    # Ensure the token being tested is considered issued
    mock = BearerAuthMock().with_token("abcde-123").with_token_format_validation(r"^[a-z]{5}-\d{3}$")
    assert mock.token_format_pattern == re.compile(r"^[a-z]{5}-\d{3}$")
    assert mock.validate_token("abcde-123") is True  # Matches pattern
    assert mock.validate_token("valid_token") is False  # Default token doesn't match
    assert mock.validate_token("invalid-format") is False


def test_with_valid_token_prefix():
    """Test valid token prefix validation."""
    mock = BearerAuthMock().with_valid_token_prefix("prod_").with_valid_token_prefix("test_")
    mock.with_token("prod_abc123")  # Set a token matching a prefix
    mock.issued_tokens.append("test_xyz789")  # Add another valid one
    mock.issued_tokens.append("invalid_token")  # Add an invalid one

    assert mock.validate_token("prod_abc123") is True
    assert mock.validate_token("test_xyz789") is True
    assert mock.validate_token("invalid_token") is False
    assert mock.validate_token("valid_token") is False  # Default token doesn't match prefix


def test_with_required_scopes():
    """Test required scopes validation."""
    mock = BearerAuthMock(token="scoped_token")
    mock.with_token_metadata(scopes=["read", "admin"])
    mock.with_required_scopes(["read"])
    assert mock.validate_token("scoped_token") is True  # Has 'read'

    mock.with_required_scopes(["read", "admin"])
    assert mock.validate_token("scoped_token") is True  # Has both

    mock.with_required_scopes(["read", "write"])
    assert mock.validate_token("scoped_token") is False  # Missing 'write'

    mock.with_required_scopes(["profile"])
    assert mock.validate_token("scoped_token") is False  # Missing 'profile'


def test_with_jwt_validation():
    """Test basic JWT structure validation."""
    mock = BearerAuthMock().with_jwt_validation()
    # Default token is not JWT format
    assert mock.validate_token("valid_token") is False

    # Add a token that looks like a JWT
    jwt_token = "header.payload.signature"
    mock.with_token(jwt_token)
    assert mock.validate_token(jwt_token) is True

    # Add an invalid JWT format token
    invalid_jwt = "header.payload"
    mock.issued_tokens.append(invalid_jwt)
    mock.token_metadata[invalid_jwt] = mock.token_metadata[jwt_token].copy()
    assert mock.validate_token(invalid_jwt) is False


def test_revoke_token():
    """Test revoking a token."""
    mock = BearerAuthMock(token="token_to_revoke")
    assert mock.validate_token("token_to_revoke") is True
    mock.revoke_token("token_to_revoke")
    assert "token_to_revoke" in mock.revoked_tokens
    assert mock.validate_token("token_to_revoke") is False


def test_revoke_non_issued_token():
    """Test revoking a token that was never issued."""
    mock = BearerAuthMock()
    mock.revoke_token("non_existent_token")
    assert "non_existent_token" not in mock.revoked_tokens  # Should not be added


@freeze_time("2023-01-01 12:00:00")
def test_refresh_token_success():
    """Test successful token refresh."""
    mock = BearerAuthMock(token="initial_token")
    mock.with_token_expiration(expires_in_seconds=-1)  # Expired
    mock.with_refresh_token("my_refresh_token")  # Enable refresh

    assert mock.is_token_expired() is True
    assert mock.can_refresh_token() is True

    refreshed = mock.refresh()
    assert refreshed is True
    assert mock.refresh_attempts == 1
    new_token = "initial_token_refreshed_1"
    assert mock.token == new_token
    assert new_token in mock.issued_tokens
    assert new_token in mock.token_metadata
    assert mock.token_metadata[new_token]["issued_at"] == datetime(2023, 1, 1, 12, 0, 0)
    assert mock.token_metadata[new_token]["expires_at"] > datetime(2023, 1, 1, 12, 0, 0)
    assert mock.auth_strategy.token == new_token


@freeze_time("2023-01-01 12:00:00")
def test_refresh_token_not_possible():
    """Test refresh when not enabled."""
    mock = BearerAuthMock(token="initial_token")
    mock.with_token_expiration(expires_in_seconds=-1)  # Expired
    # No with_refresh_token() called

    assert mock.is_token_expired() is True
    assert mock.can_refresh_token() is False
    refreshed = mock.refresh()
    assert refreshed is False
    assert mock.refresh_attempts == 0  # Attempt count doesn't increase
    assert mock.token == "initial_token"  # Token doesn't change


@freeze_time("2023-01-01 12:00:00")
def test_refresh_token_max_attempts():
    """Test refresh hitting max attempts."""
    mock = BearerAuthMock(token="initial_token")
    mock.with_token_expiration(expires_in_seconds=-1)  # Expired
    mock.with_refresh_token("my_refresh_token", max_refresh_attempts=1)  # Enable refresh, max 1 attempt

    # First refresh succeeds
    refreshed1 = mock.refresh()
    assert refreshed1 is True
    assert mock.refresh_attempts == 1
    assert mock.token == "initial_token_refreshed_1"

    # Expire the new token
    mock.with_token_expiration(expires_in_seconds=-1, token=mock.token)
    assert mock.is_token_expired() is True
    assert mock.can_refresh_token() is False  # Max attempts reached

    # Second refresh fails due to max attempts
    refreshed2 = mock.refresh()
    assert refreshed2 is False
    assert mock.refresh_attempts == 1  # Attempt count doesn't increase beyond max
    assert mock.token == "initial_token_refreshed_1"  # Token doesn't change


def test_verify_auth_header_valid():
    """Test verifying a valid Bearer auth header."""
    mock = BearerAuthMock(token="abc")
    assert mock.verify_auth_header("Bearer abc") is True


def test_verify_auth_header_invalid_prefix():
    """Test verifying header with wrong prefix."""
    mock = BearerAuthMock(token="abc")
    assert mock.verify_auth_header("Basic abc") is False


def test_verify_auth_header_missing_space():
    """Test verifying header missing space after Bearer."""
    mock = BearerAuthMock(token="abc")
    assert mock.verify_auth_header("Bearerabc") is False


def test_verify_auth_header_invalid_token():
    """Test verifying header with an invalid token."""
    mock = BearerAuthMock(token="abc")
    assert mock.verify_auth_header("Bearer xyz") is False


def test_verify_token_usage():
    """Test verify_token_usage checks issued and not revoked."""
    mock = BearerAuthMock(token="t1")
    mock.issued_tokens.append("t2")
    mock.revoke_token("t2")

    assert mock.verify_token_usage("t1") is True
    assert mock.verify_token_usage("t2") is False  # Revoked
    assert mock.verify_token_usage("t3") is False  # Not issued


def test_get_token_metadata():
    """Test retrieving token metadata."""
    mock = BearerAuthMock(token="meta_token")
    mock.with_token_metadata(user_id="meta_user")
    meta = mock.get_token_metadata("meta_token")
    assert meta is not None
    assert meta["user_id"] == "meta_user"
    assert mock.get_token_metadata("non_existent") is None


def test_get_auth_headers():
    """Test generating the Authorization header."""
    mock = BearerAuthMock("my_bearer_token")
    assert mock.get_auth_headers() == ("Authorization", "Bearer my_bearer_token")


@freeze_time("2023-01-01 12:00:00")
def test_handle_auth_error_expired_refreshable():
    """Test handle_auth_error attempts refresh for expired token."""
    mock = BearerAuthMock(token="initial")
    mock.with_token_expiration(expires_in_seconds=-1)  # Expired
    mock.with_refresh_token("refresh_key")

    # Pass a dummy response object (not used by this mock's implementation)
    handled = mock.handle_auth_error(None)  # type: ignore

    assert handled is True  # Refresh was attempted and succeeded
    assert mock.token == "initial_refreshed_1"


@freeze_time("2023-01-01 12:00:00")
def test_handle_auth_error_expired_not_refreshable():
    """Test handle_auth_error does not refresh if not configured."""
    mock = BearerAuthMock(token="initial")
    mock.with_token_expiration(expires_in_seconds=-1)  # Expired
    # No with_refresh_token()

    handled = mock.handle_auth_error(None)  # type: ignore
    assert handled is False
    assert mock.token == "initial"


@freeze_time("2023-01-01 12:00:00")
def test_handle_auth_error_not_expired():
    """Test handle_auth_error does not refresh if token not expired."""
    mock = BearerAuthMock(token="initial")
    mock.with_token_expiration(expires_in_seconds=3600)  # Not expired
    mock.with_refresh_token("refresh_key")

    handled = mock.handle_auth_error(None)  # type: ignore
    assert handled is False
    assert mock.token == "initial"


def test_get_auth_strategy():
    """Test getting the underlying auth strategy."""
    mock = BearerAuthMock("strategy_token")
    strategy = mock.get_auth_strategy()
    assert isinstance(strategy, BearerAuth)
    assert strategy.token == "strategy_token"

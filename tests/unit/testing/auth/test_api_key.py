import re
from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from crudclient.auth import ApiKeyAuth
from crudclient.testing.auth.api_key import ApiKeyAuthMock


def test_api_key_auth_mock_init_defaults():
    """Test default initialization (header)."""
    mock = ApiKeyAuthMock()
    assert mock.api_key == "valid_api_key"
    assert mock.header_name == "X-API-Key"
    assert mock.param_name is None
    assert isinstance(mock.auth_strategy, ApiKeyAuth)
    assert mock.auth_strategy.api_key == "valid_api_key"
    assert mock.auth_strategy.header_name == "X-API-Key"
    assert mock.auth_strategy.param_name is None
    assert mock.validator.validate_key("valid_api_key") is True
    assert mock.rate_limiter.rate_limit_enabled is False
    assert mock.usage_tracker.usage_tracking_enabled is False


def test_api_key_auth_mock_init_param():
    """Test initialization with param."""
    mock = ApiKeyAuthMock(api_key="param_key", header_name=None, param_name="key")
    assert mock.api_key == "param_key"
    assert mock.header_name is None
    assert mock.param_name == "key"
    assert isinstance(mock.auth_strategy, ApiKeyAuth)
    assert mock.auth_strategy.api_key == "param_key"
    assert mock.auth_strategy.header_name is None
    assert mock.auth_strategy.param_name == "key"
    assert mock.validator.validate_key("param_key") is True


def test_api_key_auth_mock_init_no_location_raises():
    """Test initialization without header or param raises ValueError."""
    with pytest.raises(ValueError, match="Either header_name or param_name must be provided"):
        ApiKeyAuthMock(header_name=None, param_name=None)


def test_with_api_key():
    """Test setting a new primary API key."""
    mock = ApiKeyAuthMock()
    mock.with_api_key("new_key_123")
    assert mock.api_key == "new_key_123"
    assert mock.validator.validate_key("new_key_123") is True
    assert mock.auth_strategy.api_key == "new_key_123"
    # Check if old key is still technically valid in the validator unless explicitly removed
    assert mock.validator.validate_key("valid_api_key") is True


def test_with_additional_valid_key():
    """Test adding another valid key."""
    mock = ApiKeyAuthMock()
    mock.with_additional_valid_key("key_two")
    assert mock.validator.validate_key("valid_api_key") is True
    assert mock.validator.validate_key("key_two") is True


def test_with_key_metadata():
    """Test setting metadata for a key."""
    mock = ApiKeyAuthMock()
    mock.with_key_metadata(owner="test_owner", permissions=["admin"], tier="premium")
    meta = mock.validator.key_metadata["valid_api_key"]
    assert meta["owner"] == "test_owner"
    assert meta["permissions"] == ["admin"]
    assert meta["tier"] == "premium"


def test_with_key_metadata_for_specific_key():
    """Test setting metadata for a specific key."""
    mock = ApiKeyAuthMock().with_additional_valid_key("other_key")
    mock.with_key_metadata(api_key="other_key", owner="other_owner")

    meta_default = mock.validator.key_metadata["valid_api_key"]
    assert meta_default["owner"] == "default_user"

    meta_other = mock.validator.key_metadata["other_key"]
    assert meta_other["owner"] == "other_owner"


def test_with_key_metadata_expiration():
    """Test setting expiration metadata."""
    with freeze_time("2023-01-01 12:00:00") as frozen_time:
        mock = ApiKeyAuthMock()
        mock.with_key_metadata(expires_in_seconds=60)
        meta = mock.validator.key_metadata["valid_api_key"]
        assert meta["expires_at"] == datetime(2023, 1, 1, 12, 1, 0)

        # Check validation before expiry
        assert mock.validate_key("valid_api_key") is True

        # Move time forward
        frozen_time.tick(delta=timedelta(seconds=61))
        assert mock.validate_key("valid_api_key") is False


def test_with_key_format_validation():
    """Test key format validation."""
    mock = ApiKeyAuthMock().with_key_format_validation(r"^key-[a-z]{3}-\d{3}$")
    assert mock.validator.key_format_pattern == re.compile(r"^key-[a-z]{3}-\d{3}$")

    # Add keys matching/not matching the pattern
    mock.with_additional_valid_key("key-abc-123")
    mock.with_additional_valid_key("invalid-format")

    assert mock.validate_key("key-abc-123") is True
    assert mock.validate_key("invalid-format") is False
    assert mock.validate_key("valid_api_key") is False  # Default key doesn't match


def test_revoke_key():
    """Test revoking a key."""
    mock = ApiKeyAuthMock().with_additional_valid_key("key_to_revoke")
    assert mock.validate_key("key_to_revoke") is True
    mock.revoke_key("key_to_revoke")
    assert mock.validate_key("key_to_revoke") is False
    assert "key_to_revoke" in mock.validator.revoked_keys


def test_revoke_default_key():
    """Test revoking the default/current key."""
    mock = ApiKeyAuthMock()
    assert mock.validate_key("valid_api_key") is True
    mock.revoke_key()  # Revokes self.api_key
    assert mock.validate_key("valid_api_key") is False
    assert "valid_api_key" in mock.validator.revoked_keys


def test_with_rate_limiting():
    """Test enabling and checking rate limiting."""
    with freeze_time("2023-01-01 12:00:00") as frozen_time:
        mock = ApiKeyAuthMock().with_rate_limiting(requests_per_period=2, period_seconds=60)
        assert mock.rate_limiter.rate_limit_enabled is True
        assert mock.rate_limiter.rate_limit_requests == 2
        assert mock.rate_limiter.rate_limit_period == 60

        # Use the key twice - should succeed
        assert mock.validate_key("valid_api_key") is True
        status1 = mock.get_rate_limit_status()
        assert status1["remaining"] == 1
        assert status1["limit"] == 2

        assert mock.validate_key("valid_api_key") is True
        status2 = mock.get_rate_limit_status()
        assert status2["remaining"] == 0
        assert status2["limit"] == 2

        # Third request should fail due to rate limit
        assert mock.validate_key("valid_api_key") is False
        status3 = mock.get_rate_limit_status()
        assert status3["remaining"] == 0  # Still 0

        # Move time forward past the period
        frozen_time.tick(delta=timedelta(seconds=61))

        # Should reset and allow requests again
        assert mock.validate_key("valid_api_key") is True
        status4 = mock.get_rate_limit_status()
        assert status4["remaining"] == 1
        assert status4["limit"] == 2


def test_with_usage_tracking():
    """Test enabling and checking usage tracking."""
    mock = ApiKeyAuthMock().with_usage_tracking()
    assert mock.usage_tracker.usage_tracking_enabled is True

    assert mock.validate_key("valid_api_key") is True
    assert mock.validate_key("valid_api_key") is True
    mock.with_additional_valid_key("key2")
    assert mock.validate_key("key2") is True

    stats = mock.get_usage_stats()
    assert stats["total_requests"] == 3
    assert stats["by_key"]["valid_api_key"] == 2
    assert stats["by_key"]["key2"] == 1  # Check count for key2 using the correct key


def test_as_header():
    """Test switching to header authentication."""
    mock = ApiKeyAuthMock(header_name=None, param_name="key").as_header("X-Custom-API-Key")
    assert mock.header_name == "X-Custom-API-Key"
    assert mock.param_name is None
    assert isinstance(mock.auth_strategy, ApiKeyAuth)
    assert mock.auth_strategy.header_name == "X-Custom-API-Key"
    assert mock.auth_strategy.param_name is None


def test_as_param():
    """Test switching to param authentication."""
    mock = ApiKeyAuthMock(header_name="X-API-Key", param_name=None).as_param("custom_key_param")
    assert mock.header_name is None
    assert mock.param_name == "custom_key_param"
    assert isinstance(mock.auth_strategy, ApiKeyAuth)
    assert mock.auth_strategy.header_name is None
    assert mock.auth_strategy.param_name == "custom_key_param"


def test_validate_key_invalid():
    """Test validate_key returns false for an invalid key."""
    mock = ApiKeyAuthMock()
    assert mock.validate_key("invalid-key") is False


def test_validate_key_revoked():
    """Test validate_key returns false for a revoked key."""
    mock = ApiKeyAuthMock().revoke_key()
    assert mock.validate_key("valid_api_key") is False


@freeze_time("2023-01-01 12:00:00")
def test_validate_key_expired():
    """Test validate_key returns false for an expired key."""
    mock = ApiKeyAuthMock().with_key_metadata(expires_in_seconds=-1)
    assert mock.validate_key("valid_api_key") is False


@freeze_time("2023-01-01 12:00:00")
def test_validate_key_rate_limited():
    """Test validate_key returns false when rate limit exceeded."""
    mock = ApiKeyAuthMock().with_rate_limiting(requests_per_period=1, period_seconds=60)
    assert mock.validate_key("valid_api_key") is True  # First request ok
    assert mock.validate_key("valid_api_key") is False  # Second request fails


def test_verify_auth_header_valid():
    """Test verify_auth_header with a valid key in header."""
    mock = ApiKeyAuthMock(api_key="abc", header_name="X-Test-Key")
    assert mock.verify_auth_header("abc") is True


def test_verify_auth_header_invalid():
    """Test verify_auth_header with an invalid key in header."""
    mock = ApiKeyAuthMock(api_key="abc", header_name="X-Test-Key")
    assert mock.verify_auth_header("xyz") is False


def test_verify_auth_header_when_using_param():
    """Test verify_auth_header returns false when configured for param auth."""
    mock = ApiKeyAuthMock(api_key="abc", header_name=None, param_name="key")
    assert mock.verify_auth_header("abc") is False


def test_verify_token_usage():
    """Test verify_token_usage delegates to validate_key."""
    mock = ApiKeyAuthMock()
    assert mock.verify_token_usage("valid_api_key") is True
    assert mock.verify_token_usage("invalid_key") is False
    mock.revoke_key()
    assert mock.verify_token_usage("valid_api_key") is False


def test_get_auth_headers_for_header_auth():
    """Test get_auth_headers when using header auth."""
    mock = ApiKeyAuthMock(api_key="key123", header_name="X-My-Key")
    assert mock.get_auth_headers() == ("X-My-Key", "key123")


def test_get_auth_headers_for_param_auth():
    """Test get_auth_headers returns None when using param auth."""
    mock = ApiKeyAuthMock(api_key="key123", header_name=None, param_name="api_token")
    assert mock.get_auth_headers() is None


def test_handle_auth_error():
    """Test handle_auth_error always returns False."""
    mock = ApiKeyAuthMock()
    assert mock.handle_auth_error(None) is False  # type: ignore


def test_get_auth_strategy():
    """Test getting the underlying auth strategy."""
    mock = ApiKeyAuthMock(api_key="strat_key", header_name="X-Strat")
    strategy = mock.get_auth_strategy()
    assert isinstance(strategy, ApiKeyAuth)
    assert strategy.api_key == "strat_key"
    assert strategy.header_name == "X-Strat"

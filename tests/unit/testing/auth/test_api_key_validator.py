import re
from datetime import datetime

from freezegun import freeze_time

from crudclient.testing.auth.api_key_validator import ApiKeyValidator


def test_validator_init() -> None:
    """Test initial state of the validator."""
    validator = ApiKeyValidator()
    assert validator.valid_keys == set()
    assert validator.key_format_pattern is None
    assert validator.key_metadata == {}
    assert validator.revoked_keys == set()


def test_add_valid_key() -> None:
    """Test adding valid keys."""
    validator = ApiKeyValidator()
    validator.add_valid_key("key1")
    validator.add_valid_key("key2")
    validator.add_valid_key("key1")  # Adding duplicates is fine
    assert validator.valid_keys == {"key1", "key2"}


def test_set_key_metadata_new_key() -> None:
    """Test setting metadata for a new key."""
    validator = ApiKeyValidator()
    validator.set_key_metadata(api_key="meta_key", owner="owner1", permissions=["read"], tier="basic")
    assert "meta_key" in validator.key_metadata
    meta = validator.key_metadata["meta_key"]
    assert meta["owner"] == "owner1"
    assert meta["permissions"] == ["read"]
    assert meta["tier"] == "basic"
    assert meta["expires_at"] is None
    assert isinstance(meta["issued_at"], datetime)


def test_set_key_metadata_existing_key() -> None:
    """Test updating metadata for an existing key."""
    validator = ApiKeyValidator()
    validator.set_key_metadata(api_key="meta_key", owner="owner1")
    validator.set_key_metadata(api_key="meta_key", owner="owner2", tier="premium")  # Update owner and tier
    meta = validator.key_metadata["meta_key"]
    assert meta["owner"] == "owner2"
    assert meta["tier"] == "premium"
    assert meta["permissions"] == ["read", "write"]  # Default permissions remain


@freeze_time("2023-01-01 12:00:00")
def test_set_key_metadata_with_expiration() -> None:
    """Test setting expiration metadata."""
    validator = ApiKeyValidator()
    validator.set_key_metadata(api_key="exp_key", expires_at=datetime(2023, 1, 1, 13, 0, 0))
    meta = validator.key_metadata["exp_key"]
    assert meta["expires_at"] == datetime(2023, 1, 1, 13, 0, 0)


def test_set_key_format_pattern() -> None:
    """Test setting the key format pattern."""
    validator = ApiKeyValidator()
    pattern = re.compile(r"^[a-z]+$")
    validator.set_key_format_pattern(pattern)
    assert validator.key_format_pattern == pattern


def test_revoke_key() -> None:
    """Test revoking a key."""
    validator = ApiKeyValidator()
    validator.add_valid_key("key_to_revoke")
    validator.add_valid_key("key_to_keep")
    validator.revoke_key("key_to_revoke")
    assert validator.revoked_keys == {"key_to_revoke"}
    assert "key_to_keep" not in validator.revoked_keys


def test_revoke_non_existent_key() -> None:
    """Test revoking a key that wasn't added."""
    validator = ApiKeyValidator()
    validator.revoke_key("non_existent")
    assert validator.revoked_keys == set()  # Should not add non-valid keys


# --- Test validate_key ---


def test_validate_key_valid() -> None:
    """Test validate_key for a simple valid key."""
    validator = ApiKeyValidator()
    validator.add_valid_key("valid1")
    assert validator.validate_key("valid1") is True


def test_validate_key_invalid() -> None:
    """Test validate_key for a key that was never added."""
    validator = ApiKeyValidator()
    assert validator.validate_key("invalid1") is False


def test_validate_key_revoked() -> None:
    """Test validate_key for a revoked key."""
    validator = ApiKeyValidator()
    validator.add_valid_key("revoked_key")
    validator.revoke_key("revoked_key")
    assert validator.validate_key("revoked_key") is False


@freeze_time("2023-01-01 12:00:00")
def test_validate_key_expired() -> None:
    """Test validate_key for an expired key."""
    validator = ApiKeyValidator()
    validator.add_valid_key("expired_key")
    validator.set_key_metadata(api_key="expired_key", expires_at=datetime(2023, 1, 1, 11, 59, 59))
    assert validator.validate_key("expired_key") is False


@freeze_time("2023-01-01 12:00:00")
def test_validate_key_not_expired() -> None:
    """Test validate_key for a non-expired key."""
    validator = ApiKeyValidator()
    validator.add_valid_key("not_expired_key")
    validator.set_key_metadata(api_key="not_expired_key", expires_at=datetime(2023, 1, 1, 12, 0, 1))
    assert validator.validate_key("not_expired_key") is True


def test_validate_key_format_match() -> None:
    """Test validate_key with a matching format pattern."""
    validator = ApiKeyValidator()
    validator.set_key_format_pattern(re.compile(r"^prod_"))
    validator.add_valid_key("prod_key1")
    assert validator.validate_key("prod_key1") is True


def test_validate_key_format_mismatch() -> None:
    """Test validate_key with a non-matching format pattern."""
    validator = ApiKeyValidator()
    validator.set_key_format_pattern(re.compile(r"^prod_"))
    validator.add_valid_key("dev_key1")  # Added, but doesn't match pattern
    assert validator.validate_key("dev_key1") is False


def test_validate_key_format_no_pattern() -> None:
    """Test validate_key works without a format pattern."""
    validator = ApiKeyValidator()
    validator.add_valid_key("any_format_key")
    assert validator.validate_key("any_format_key") is True


def test_validate_key_all_conditions_pass() -> None:
    """Test validate_key when key is valid, not revoked, not expired, matches format."""
    with freeze_time("2023-01-01 12:00:00"):
        validator = ApiKeyValidator()
        validator.set_key_format_pattern(re.compile(r"^final_"))
        validator.add_valid_key("final_key")
        validator.set_key_metadata(api_key="final_key", expires_at=datetime(2023, 1, 1, 13, 0, 0))
        assert validator.validate_key("final_key") is True

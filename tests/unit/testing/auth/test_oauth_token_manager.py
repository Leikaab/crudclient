from datetime import datetime, timedelta

from freezegun import freeze_time

from crudclient.testing.auth.oauth_token_manager import OAuthTokenManager


@freeze_time("2023-01-01 12:00:00")
def test_token_manager_init_and_default_token() -> None:
    """Test initialization and the default token state."""
    manager = OAuthTokenManager()
    manager.initialize_default_token(client_id="default_client", scope="default_scope")

    assert manager.current_access_token == "access_token"
    assert manager.current_refresh_token == "refresh_token"
    assert "access_token" in manager.access_tokens
    assert "refresh_token" in manager.refresh_tokens
    assert manager.refresh_tokens["refresh_token"] == "access_token"

    token_data = manager.access_tokens["access_token"]
    assert token_data["client_id"] == "default_client"
    assert token_data["scope"] == "default_scope"
    assert token_data["expires_at"] == datetime(2023, 1, 1, 13, 0, 0)  # Default 1 hour
    assert token_data["token_type"] == "Bearer"
    assert token_data["grant_type"] == "client_credentials"


@freeze_time("2023-01-01 12:00:00")
def test_create_token() -> None:
    """Test creating a new token."""
    manager = OAuthTokenManager()
    token_info = manager.create_token(client_id="c1", scope="s1", expires_in=60, user="u1")

    new_access_token = token_info["access_token"]
    new_refresh_token = token_info["refresh_token"]

    assert new_access_token.startswith("access_token_")
    assert new_refresh_token.startswith("refresh_token_")
    assert token_info["expires_in"] == 60
    assert token_info["token_type"] == "Bearer"
    assert token_info["scope"] == "s1"

    assert manager.current_access_token == new_access_token
    assert manager.current_refresh_token == new_refresh_token
    assert new_access_token in manager.access_tokens
    assert new_refresh_token in manager.refresh_tokens
    assert manager.refresh_tokens[new_refresh_token] == new_access_token

    token_data = manager.access_tokens[new_access_token]
    assert token_data["client_id"] == "c1"
    assert token_data["scope"] == "s1"
    assert token_data["expires_at"] == datetime(2023, 1, 1, 12, 1, 0)
    assert token_data["grant_type"] == "client_credentials"  # Default grant type
    assert token_data["user"] == "u1"


@freeze_time("2023-01-01 12:00:00")
def test_create_authorization_code() -> None:
    """Test creating an authorization code."""
    manager = OAuthTokenManager()
    code = manager.create_authorization_code(client_id="c1", redirect_uri="uri1", scope="s1", state="state1")

    assert code.startswith("auth_code_")
    assert code in manager.authorization_codes

    code_data = manager.authorization_codes[code]
    assert code_data["client_id"] == "c1"
    assert code_data["redirect_uri"] == "uri1"
    assert code_data["scope"] == "s1"
    assert code_data["state"] == "state1"
    assert code_data["expires_at"] == datetime(2023, 1, 1, 12, 10, 0)  # Default 10 mins


@freeze_time("2023-01-01 12:00:00")
def test_validate_token_valid() -> None:
    """Test validating a valid, non-expired token."""
    manager = OAuthTokenManager()
    token_info = manager.create_token(client_id="c1", expires_in=60)
    assert manager.validate_token(token_info["access_token"]) is True


def test_validate_token_invalid() -> None:
    """Test validating a non-existent token."""
    manager = OAuthTokenManager()
    assert manager.validate_token("non_existent_token") is False


def test_validate_token_expired() -> None:
    """Test validating an expired token."""
    with freeze_time("2023-01-01 12:00:00") as frozen_time:
        manager = OAuthTokenManager()
        token_info = manager.create_token(client_id="c1", expires_in=60)
        access_token = token_info["access_token"]

        # Move time forward
        frozen_time.tick(delta=timedelta(seconds=61))
        assert manager.validate_token(access_token) is False


def test_refresh_token_valid() -> None:
    """Test refreshing a valid token."""
    with freeze_time("2023-01-01 12:00:00") as frozen_time:
        manager = OAuthTokenManager()
        # Create initial token
        initial_token_info = manager.create_token(client_id="c1", scope="s1", user="u1")
        initial_access = initial_token_info["access_token"]
        initial_refresh = initial_token_info["refresh_token"]

        # Move time slightly
        frozen_time.tick(delta=timedelta(seconds=1))

        # Refresh the token
        refreshed_info = manager.refresh_token(initial_refresh)
        assert refreshed_info is not None

        new_access = refreshed_info["access_token"]
        new_refresh = refreshed_info["refresh_token"]

        assert new_access != initial_access
        assert new_refresh != initial_refresh
        assert new_access in manager.access_tokens
        assert new_refresh in manager.refresh_tokens
        assert manager.current_access_token == new_access
        assert manager.current_refresh_token == new_refresh

        # Check new token data inherited properties
        new_token_data = manager.access_tokens[new_access]
        assert new_token_data["client_id"] == "c1"
        assert new_token_data["scope"] == "s1"
        assert new_token_data["user"] == "u1"
        assert new_token_data["grant_type"] == "refresh_token"  # Grant type updated
        assert new_token_data["expires_at"] > datetime(2023, 1, 1, 12, 0, 1)  # New expiry


def test_refresh_token_invalid_refresh_token() -> None:
    """Test refreshing with an invalid refresh token."""
    manager = OAuthTokenManager()
    assert manager.refresh_token("invalid_refresh") is None


def test_refresh_token_access_token_deleted() -> None:
    """Test refreshing when the associated access token was deleted (edge case)."""
    manager = OAuthTokenManager()
    token_info = manager.create_token(client_id="c1")
    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]

    # Manually delete the access token
    del manager.access_tokens[access_token]

    assert manager.refresh_token(refresh_token) is None


@freeze_time("2023-01-01 12:00:00")
def test_revoke_token() -> None:
    """Test revoking an access token."""
    manager = OAuthTokenManager()
    token_info = manager.create_token(client_id="c1")
    access_token = token_info["access_token"]
    refresh_token = token_info["refresh_token"]

    assert access_token in manager.access_tokens
    assert refresh_token in manager.refresh_tokens

    revoked = manager.revoke_token(access_token)
    assert revoked is True
    assert access_token not in manager.access_tokens
    assert refresh_token not in manager.refresh_tokens


def test_revoke_token_invalid() -> None:
    """Test revoking a non-existent token."""
    manager = OAuthTokenManager()
    assert manager.revoke_token("invalid_token") is False


@freeze_time("2023-01-01 12:00:00")
def test_revoke_current_token_updates_current() -> None:
    """Test that revoking the current token updates the current token pointer."""
    manager = OAuthTokenManager()
    token1_info = manager.create_token(client_id="c1")
    token2_info = manager.create_token(client_id="c2")  # This becomes current

    print(f"Token1: {token1_info['access_token']}")
    print(f"Token2: {token2_info['access_token']}")
    print(f"Current token: {manager.current_access_token}")
    print(f"Access tokens: {manager.access_tokens.keys()}")

    assert manager.current_access_token == token2_info["access_token"]

    manager.revoke_token(token2_info["access_token"])

    print(f"After revoke token2, current token: {manager.current_access_token}")
    print(f"Access tokens after revoke: {manager.access_tokens.keys()}")

    # Current should fall back to the other available token
    assert manager.current_access_token == token1_info["access_token"]

    # Revoke the last token
    manager.revoke_token(token1_info["access_token"])
    print(f"After revoke token1, current token: {manager.current_access_token}")
    assert manager.current_access_token == ""  # Becomes empty string


def test_add_user() -> None:
    """Test adding a user for password grant."""
    manager = OAuthTokenManager()
    manager.add_user("testuser", "testpass", ["scope1", "scope2"])
    assert "testuser" in manager.user_credentials  # Check user exists in the correct dictionary
    assert manager.user_credentials["testuser"]["password"] == "testpass"
    assert manager.user_credentials["testuser"]["scopes"] == ["scope1", "scope2"]


def test_validate_user_valid() -> None:
    """Test validating a valid user."""
    manager = OAuthTokenManager()
    manager.add_user("testuser", "testpass", [])
    assert manager.validate_user("testuser", "testpass") is True


def test_validate_user_invalid_password() -> None:
    """Test validating with an invalid password."""
    manager = OAuthTokenManager()
    manager.add_user("testuser", "testpass", [])
    assert manager.validate_user("testuser", "wrongpass") is False


def test_validate_user_invalid_username() -> None:
    """Test validating a non-existent user."""
    manager = OAuthTokenManager()
    assert manager.validate_user("nonexistent", "pass") is False

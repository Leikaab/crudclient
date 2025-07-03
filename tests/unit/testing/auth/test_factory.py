# Assuming AuthTypes exists in crudclient.auth, might need adjustment if not
# from crudclient.auth import AuthTypes
from crudclient.testing.auth.api_key import ApiKeyAuthMock
from crudclient.testing.auth.basic import BasicAuthMock
from crudclient.testing.auth.bearer import BearerAuthMock
from crudclient.testing.auth.custom import CustomAuthMock, OAuthMock
from crudclient.testing.auth.factory import (
    create_api_key_auth_mock,
    create_basic_auth_mock,
    create_bearer_auth_mock,
    create_custom_auth_mock,
    create_oauth_mock,
)


def test_create_basic_auth_mock() -> None:
    """Verify creating a basic auth mock."""
    auth_mock = create_basic_auth_mock()
    assert isinstance(auth_mock, BasicAuthMock)
    assert auth_mock.username == "user"  # Check default value
    assert auth_mock.password == "pass"  # Check default value


def test_create_bearer_auth_mock() -> None:
    """Verify creating a bearer auth mock."""
    auth_mock = create_bearer_auth_mock()
    assert isinstance(auth_mock, BearerAuthMock)
    assert auth_mock.token == "valid_token"  # Check default value


def test_create_api_key_auth_mock() -> None:
    """Verify creating an API key auth mock."""
    auth_mock = create_api_key_auth_mock()
    assert isinstance(auth_mock, ApiKeyAuthMock)
    assert auth_mock.api_key == "valid_api_key"  # Check default value
    assert auth_mock.header_name == "X-API-Key"  # Check default value


def test_create_custom_auth_mock() -> None:
    """Verify creating a custom auth mock."""
    auth_mock = create_custom_auth_mock()
    assert isinstance(auth_mock, CustomAuthMock)
    # Add more specific assertions if needed based on CustomAuthMock implementation


def test_create_oauth_mock() -> None:
    """Verify creating an OAuth mock."""
    auth_mock = create_oauth_mock()
    assert isinstance(auth_mock, OAuthMock)
    assert auth_mock.client_id == "client_id"  # Check default value
    assert auth_mock.client_secret == "client_secret"  # Check default value
    assert auth_mock.token_url == "https://example.com/oauth/token"  # Check default value


# Note: The test for invalid type is removed as each factory function creates a specific type.
# We might add tests later to check the behavior of each factory function with various arguments.

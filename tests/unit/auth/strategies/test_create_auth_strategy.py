"""
Tests for the create_auth_strategy factory function in the crudclient library.
"""

from typing import Dict, Optional, Tuple, Union

import pytest

from crudclient.auth import create_auth_strategy
from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth


class TestCreateAuthStrategy:
    @pytest.mark.parametrize(
        "auth_type, token, expected_class, expected_attrs",
        [
            ("bearer", "test_token", BearerAuth, {"token": "test_token"}),
            ("basic", "user", BasicAuth, {"username": "user", "password": ""}),
            ("basic", ("user", "pass"), BasicAuth, {"username": "user", "password": "pass"}),
            ("none", "any_token", type(None), {}),
            ("bearer", None, type(None), {}),
            ("basic", None, type(None), {}),
            # Assuming default/unknown falls back to None if token is None
            ("unknown", None, type(None), {}),
            # Assuming default/unknown falls back to Bearer if token is provided
            ("custom", "fallback_token", BearerAuth, {"token": "fallback_token"}),
            ("unknown", "fallback_token", BearerAuth, {"token": "fallback_token"}),
        ],
    )
    def test_create_auth_strategy(
        self,
        auth_type: str,
        token: Optional[Union[str, Tuple[str, str]]],
        expected_class: type,
        expected_attrs: Dict[str, str],
    ):
        """
        GIVEN an auth type string and a token/credential
        WHEN create_auth_strategy is called
        THEN the correct auth strategy instance (or None) is created with expected attributes.
        """
        # GIVEN - parameters from pytest.mark.parametrize

        # WHEN
        auth = create_auth_strategy(auth_type, token)  # type: ignore[arg-type]

        # THEN
        if expected_class is type(None):
            assert auth is None
        else:
            assert isinstance(auth, expected_class)
            for attr, value in expected_attrs.items():
                assert getattr(auth, attr) == value

    def test_create_basic_auth_invalid_token_type(self):
        """
        GIVEN the auth type 'basic' and an invalid token type (int)
        WHEN create_auth_strategy is called
        THEN a TypeError is raised.
        """
        # GIVEN / WHEN / THEN
        with pytest.raises(TypeError, match="Basic auth token must be a string or tuple"):
            create_auth_strategy("basic", 123)  # type: ignore

    # Note: ApiKeyAuth and CustomAuth cannot be created via create_auth_strategy
    # as they require more complex configuration (header/param names or callbacks).
    # This is expected behavior. We test that they fall back to BearerAuth if a token is given.

    def test_create_apikey_falls_back_to_bearer(self):
        """
        GIVEN the auth type 'apikey' and a token string
        WHEN create_auth_strategy is called
        THEN it falls back to creating a BearerAuth instance.
        """
        # GIVEN
        auth_type = "apikey"
        token = "some_key"

        # WHEN
        auth = create_auth_strategy(auth_type, token)

        # THEN
        assert isinstance(auth, BearerAuth)
        assert auth.token == token

    def test_create_custom_falls_back_to_bearer(self):
        """
        GIVEN the auth type 'custom' and a token string
        WHEN create_auth_strategy is called
        THEN it falls back to creating a BearerAuth instance.
        """
        # GIVEN
        # This was already tested implicitly by the parametrize test, but making it explicit
        auth_type = "custom"
        token = "some_token"

        # WHEN
        auth = create_auth_strategy(auth_type, token)

        # THEN
        assert isinstance(auth, BearerAuth)
        assert auth.token == token

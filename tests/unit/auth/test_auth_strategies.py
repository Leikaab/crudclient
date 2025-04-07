import base64
from typing import Dict, Optional, Tuple, Union

import pytest

from crudclient.auth import AuthStrategy, create_auth_strategy
from crudclient.auth.base import BaseAuthStrategy
from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import ApiKeyAuth, CustomAuth


class TestBearerAuth:
    def test_prepare_request_headers(self):
        """
        GIVEN a BearerAuth instance with a token
        WHEN prepare_request_headers is called
        THEN the correct Authorization header is returned and params are empty.
        """
        # GIVEN
        auth = BearerAuth(token="test_token")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"Authorization": "Bearer test_token"}
        assert params == {}

    def test_empty_token(self):
        """
        GIVEN a BearerAuth instance with an empty token
        WHEN prepare_request_headers is called
        THEN the Authorization header includes 'Bearer ' and params are empty.
        """
        # GIVEN
        auth = BearerAuth(token="")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"Authorization": "Bearer "}
        assert params == {}

    def test_header_case_insensitivity_provided(self):
        """
        GIVEN a BearerAuth instance
        WHEN prepare_request_headers is called
        THEN the 'Authorization' header key uses standard capitalization.
        """
        # GIVEN
        # Although HTTP headers are case-insensitive, we should store/send exactly as provided
        auth = BearerAuth(token="test_token")

        # WHEN
        headers = auth.prepare_request_headers()

        # THEN
        # We expect the standard "Authorization" capitalization
        assert "Authorization" in headers
        assert "authorization" not in headers  # Check it wasn't lowercased
        assert headers["Authorization"] == "Bearer test_token"


class TestBasicAuth:
    def test_prepare_request_headers(self):
        """
        GIVEN a BasicAuth instance with username and password
        WHEN prepare_request_headers is called
        THEN the correct Basic Authorization header is returned and params are empty.
        """
        # GIVEN
        auth = BasicAuth(username="user", password="pass")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        expected_token = base64.b64encode(b"user:pass").decode("ascii")
        assert headers == {"Authorization": f"Basic {expected_token}"}
        assert params == {}

    def test_empty_credentials(self):
        """
        GIVEN a BasicAuth instance with empty username and password
        WHEN prepare_request_headers is called
        THEN the Basic Authorization header for empty credentials is returned.
        """
        # GIVEN
        auth = BasicAuth(username="", password="")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        expected_token = base64.b64encode(b":").decode("ascii")
        assert headers == {"Authorization": f"Basic {expected_token}"}
        assert params == {}

    def test_only_username(self):
        """
        GIVEN a BasicAuth instance with only a username
        WHEN prepare_request_headers is called
        THEN the Basic Authorization header includes the username and colon.
        """
        # GIVEN
        auth = BasicAuth(username="user", password="")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        expected_token = base64.b64encode(b"user:").decode("ascii")
        assert headers == {"Authorization": f"Basic {expected_token}"}
        assert params == {}

    def test_only_password(self):
        """
        GIVEN a BasicAuth instance with only a password
        WHEN prepare_request_headers is called
        THEN the Basic Authorization header includes the colon and password.
        """
        # GIVEN
        auth = BasicAuth(username="", password="pass")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        expected_token = base64.b64encode(b":pass").decode("ascii")
        assert headers == {"Authorization": f"Basic {expected_token}"}
        assert params == {}


class TestApiKeyAuth:
    def test_header_auth(self):
        """
        GIVEN an ApiKeyAuth instance configured for header authentication
        WHEN prepare_request_headers and prepare_request_params are called
        THEN the correct header is returned, params are empty, and attributes match.
        """
        # GIVEN
        auth = ApiKeyAuth(api_key="test_key", header_name="X-API-Key")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"X-API-Key": "test_key"}
        assert params == {}
        assert auth.api_key == "test_key"
        assert auth.header_name == "X-API-Key"
        assert auth.param_name is None

    def test_param_auth(self):
        """
        GIVEN an ApiKeyAuth instance configured for parameter authentication
        WHEN prepare_request_headers and prepare_request_params are called
        THEN headers are empty, the correct param is returned, and attributes match.
        """
        # GIVEN
        auth = ApiKeyAuth(api_key="test_key", param_name="api_key")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {}
        assert params == {"api_key": "test_key"}
        assert auth.api_key == "test_key"
        assert auth.header_name is None
        assert auth.param_name == "api_key"

    def test_both_header_and_param_auth_raises(self):
        """
        GIVEN ApiKeyAuth initialization arguments for both header and param
        WHEN ApiKeyAuth is instantiated
        THEN a ValueError is raised.
        """
        # GIVEN / WHEN / THEN
        with pytest.raises(ValueError, match="Only one of header_name or param_name"):
            ApiKeyAuth(api_key="test_key", header_name="X-API-Key", param_name="api_key")

    def test_neither_header_nor_param_auth_raises(self):
        """
        GIVEN ApiKeyAuth initialization arguments for neither header nor param
        WHEN ApiKeyAuth is instantiated
        THEN a ValueError is raised.
        """
        # GIVEN / WHEN / THEN
        with pytest.raises(ValueError, match="One of header_name or param_name"):
            ApiKeyAuth(api_key="test_key")

    def test_empty_key_header(self):
        """
        GIVEN an ApiKeyAuth instance for header auth with an empty key
        WHEN prepare_request_headers is called
        THEN the header value is an empty string.
        """
        # GIVEN
        auth = ApiKeyAuth(api_key="", header_name="X-API-Key")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"X-API-Key": ""}
        assert params == {}

    def test_empty_key_param(self):
        """
        GIVEN an ApiKeyAuth instance for param auth with an empty key
        WHEN prepare_request_params is called
        THEN the param value is an empty string.
        """
        # GIVEN
        auth = ApiKeyAuth(api_key="", param_name="api_key")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {}
        assert params == {"api_key": ""}


class TestCustomAuth:
    def test_header_callback(self):
        """
        GIVEN a CustomAuth instance with only a header callback
        WHEN prepare_request_headers and prepare_request_params are called
        THEN the header callback is used, params are empty, and attributes match.
        """
        # GIVEN
        def get_headers() -> Dict[str, str]:
            return {"X-Custom-Auth": "custom_value"}

        auth = CustomAuth(header_callback=get_headers)

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"X-Custom-Auth": "custom_value"}
        assert params == {}
        assert auth.header_callback == get_headers
        assert auth.param_callback is None

    def test_param_callback(self):
        """
        GIVEN a CustomAuth instance with both header and param callbacks
        WHEN prepare_request_headers and prepare_request_params are called
        THEN both callbacks are used correctly and attributes match.
        """
        # GIVEN
        def get_headers() -> Dict[str, str]:
            return {"X-Custom-Auth": "custom_value"}

        def get_params() -> Dict[str, str]:
            return {"custom_param": "param_value"}

        auth = CustomAuth(header_callback=get_headers, param_callback=get_params)

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"X-Custom-Auth": "custom_value"}
        assert params == {"custom_param": "param_value"}
        assert auth.header_callback == get_headers
        assert auth.param_callback == get_params

    def test_only_param_callback(self):
        """
        GIVEN a CustomAuth instance with only a param callback
        WHEN prepare_request_headers and prepare_request_params are called
        THEN headers are empty, the param callback is used, and attributes match.
        """
        # GIVEN
        def get_params() -> Dict[str, str]:
            return {"custom_param": "param_value"}

        auth = CustomAuth(param_callback=get_params)  # type: ignore[call-arg]

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {}
        assert params == {"custom_param": "param_value"}
        assert auth.header_callback is None
        assert auth.param_callback == get_params

    def test_no_callbacks_raises(self):
        """
        GIVEN no callbacks provided to CustomAuth
        WHEN CustomAuth is instantiated
        THEN a ValueError is raised.
        """
        # GIVEN / WHEN / THEN
        with pytest.raises(ValueError, match="At least one callback must be provided"):
            CustomAuth()  # type: ignore[call-arg]

    def test_header_callback_invalid_return_type(self):
        """
        GIVEN a CustomAuth instance with a header callback returning an invalid type
        WHEN prepare_request_headers is called
        THEN a TypeError is raised.
        """
        # GIVEN
        def get_headers_invalid() -> str:
            return "not_a_dict"  # type: ignore

        auth = CustomAuth(header_callback=get_headers_invalid)  # type: ignore[arg-type]

        # WHEN / THEN
        with pytest.raises(TypeError, match="Header callback must return a dictionary"):
            auth.prepare_request_headers()

    def test_param_callback_invalid_return_type(self):
        """
        GIVEN a CustomAuth instance with a param callback returning an invalid type
        WHEN prepare_request_params is called
        THEN a TypeError is raised.
        """
        # GIVEN
        def get_params_invalid() -> list:
            return ["not_a_dict"]  # type: ignore

        auth = CustomAuth(param_callback=get_params_invalid)  # type: ignore[call-arg, arg-type]

        # WHEN / THEN
        with pytest.raises(TypeError, match="Parameter callback must return a dictionary"):
            auth.prepare_request_params()


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


# Test Base Strategy (Optional, but good practice)
class TestBaseAuthStrategy:
    def test_base_methods_not_implemented(self):
        """
        GIVEN a BaseAuthStrategy instance
        WHEN prepare_request_headers or prepare_request_params is called
        THEN a NotImplementedError is raised.
        """
        # GIVEN
        base_auth = BaseAuthStrategy()

        # WHEN / THEN
        with pytest.raises(NotImplementedError):
            base_auth.prepare_request_headers()
        with pytest.raises(NotImplementedError):
            base_auth.prepare_request_params()

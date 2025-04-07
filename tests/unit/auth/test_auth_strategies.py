from typing import Dict

from crudclient.auth import create_auth_strategy
from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import ApiKeyAuth, CustomAuth


class TestBearerAuth:
    def test_prepare_request_headers(self):
        auth = BearerAuth(token="test_token")
        headers = auth.prepare_request_headers()

        assert headers == {"Authorization": "Bearer test_token"}

    def test_prepare_request_params(self):
        auth = BearerAuth(token="test_token")
        params = auth.prepare_request_params()

        assert params == {}


class TestBasicAuth:
    def test_prepare_request_headers(self):
        auth = BasicAuth(username="user", password="pass")
        headers = auth.prepare_request_headers()

        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Basic ")
        # The actual value is base64 encoded, so we don't check the exact value

    def test_prepare_request_params(self):
        auth = BasicAuth(username="user", password="pass")
        params = auth.prepare_request_params()

        assert params == {}


class TestApiKeyAuth:
    def test_header_auth(self):
        auth = ApiKeyAuth(api_key="test_key", header_name="X-API-Key")
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        assert headers == {"X-API-Key": "test_key"}
        assert params == {}

    def test_param_auth(self):
        auth = ApiKeyAuth(api_key="test_key", param_name="api_key")
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        assert headers == {}
        assert params == {"api_key": "test_key"}


class TestCustomAuth:
    def test_header_callback(self):
        def get_headers() -> Dict[str, str]:
            return {"X-Custom-Auth": "custom_value"}

        auth = CustomAuth(header_callback=get_headers)
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        assert headers == {"X-Custom-Auth": "custom_value"}
        assert params == {}

    def test_param_callback(self):
        def get_headers() -> Dict[str, str]:
            return {"X-Custom-Auth": "custom_value"}

        def get_params() -> Dict[str, str]:
            return {"custom_param": "param_value"}

        auth = CustomAuth(header_callback=get_headers, param_callback=get_params)
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        assert headers == {"X-Custom-Auth": "custom_value"}
        assert params == {"custom_param": "param_value"}


class TestCreateAuthStrategy:
    def test_create_bearer_auth(self):
        auth = create_auth_strategy("bearer", "test_token")
        assert isinstance(auth, BearerAuth)
        assert auth.token == "test_token"

    def test_create_basic_auth(self):
        auth = create_auth_strategy("basic", "test_token")
        assert isinstance(auth, BasicAuth)
        assert auth.username == "test_token"
        assert auth.password == ""

    def test_create_none_auth(self):
        auth = create_auth_strategy("none", "test_token")
        assert auth is None

    def test_create_auth_with_none_token(self):
        auth = create_auth_strategy("bearer", None)
        assert auth is None

    def test_create_default_auth(self):
        auth = create_auth_strategy("custom", "test_token")
        assert isinstance(auth, BearerAuth)
        assert auth.token == "test_token"

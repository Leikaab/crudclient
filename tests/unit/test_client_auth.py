import pytest
import requests_mock

from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import CustomAuth
from crudclient.client import Client

from .test_config import MockClientConfig


class MockBearerAuthConfig(MockClientConfig):
    headers = {"X-Custom-Header": "custom-value"}
    api_key = "supersecret"

    def __init__(self):
        super().__init__()
        self.auth_strategy = BearerAuth(token="supersecret")


class MockBasicAuthConfig(MockClientConfig):
    def __init__(self):
        super().__init__()
        self.auth_strategy = BasicAuth(username="user", password="pass")


class MockCustomAuthConfig(MockClientConfig):
    def __init__(self):
        super().__init__()
        self.called = False

        def apply_auth_headers(session):
            session.headers.update({"X-Auth": "yes"})
            self.called = True
            return {}

        self.auth_strategy = CustomAuth(header_callback=lambda: {"X-Auth": "yes"})


class TestClientAuth:
    @pytest.fixture
    def client(self):
        # Create a mock config for the client
        config = MockBearerAuthConfig()
        return Client(config)

    @pytest.fixture
    def mock_request(self):
        with requests_mock.Mocker() as m:
            yield m

    def test_client_accepts_dict_config(self):
        config_dict = {
            "hostname": "https://example.com",
            "version": "v1",
            "headers": {"X-Test": "1"},
        }
        client = Client(config_dict)
        assert client.config.hostname == "https://example.com"
        assert client.config.version == "v1"
        assert client.session.headers["X-Test"] == "1"

    def test_client_basic_auth_sets_session_headers(self):
        config = MockBasicAuthConfig()
        client = Client(config)
        # Just check that the Authorization header exists
        assert "Authorization" in client.session.headers

    def test_client_custom_auth_applies_headers(self):
        config = MockCustomAuthConfig()
        client = Client(config)
        assert client.session.headers["X-Auth"] == "yes"

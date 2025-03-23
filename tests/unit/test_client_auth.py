import pytest
import requests_mock

from crudclient.client import Client

from .test_config import MockClientConfig


class MockBearerAuthConfig(MockClientConfig):
    headers = {"Authorization": "Bearer token"}
    api_key = "supersecret"


class MockTupleAuthConfig(MockClientConfig):
    def auth(self):
        return ("user", "pass")


class MockCallableAuthConfig(MockClientConfig):
    def __init__(self):
        super().__init__()
        self.called = False

    def auth(self):
        def apply_auth(session):
            session.headers.update({"X-Auth": "yes"})
            self.called = True

        return apply_auth


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

    def test_client_tuple_auth_sets_session_auth(self):
        config = MockTupleAuthConfig()
        client = Client(config)
        assert client.session.auth == ("user", "pass")

    def test_client_callable_auth_applies_headers(self):
        config = MockCallableAuthConfig()
        client = Client(config)
        assert client.session.headers["X-Auth"] == "yes"
        assert config.called is True

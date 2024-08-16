import pytest  # noqa F401

from crudclient.config import ClientConfig


class MockClientConfig(ClientConfig):
    hostname = "https://api.example.com"
    version = "v1"
    api_key = "mykey"
    headers = {}
    retries = 3
    timeout = 5


class TestClientConfig:
    @pytest.fixture
    def config(self):
        return MockClientConfig()

    def test_config_initialization(self, config):
        assert config.base_url == "https://api.example.com/v1"
        assert config.api_key == "mykey"
        assert config.headers == {}
        assert config.timeout == 5
        assert config.retries == 3

    def test_config_auth(self, config):
        auth = config.auth()
        assert isinstance(auth, dict)
        assert auth == {"Authorization": f"Bearer {config.api_key}"}

    def test_get_default_headers(self, config):
        config.headers["Accept"] = "application/json"
        assert isinstance(config.headers, dict)
        assert config.headers == {"Accept": "application/json"}

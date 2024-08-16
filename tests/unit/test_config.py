import pytest  # noqa F401

from crudclient.config import ClientConfig


class TestClientConfig:
    @pytest.fixture
    def config(self):
        return ClientConfig(base_url="https://api.example.com", api_key="secret_key")

    def test_config_initialization(self, config):
        assert config.base_url == "https://api.example.com"
        assert config.api_key == "secret_key"
        assert config.headers == {}
        assert config.timeout == 10.0
        assert config.retries == 3

    def test_config_auth(self, config):
        auth = config.auth()
        assert isinstance(auth, dict)
        assert auth == {"Authorization": f"Bearer {config.api_key}"}

    def test_get_default_headers(self, config):
        config.headers["Accept"] = "application/json"
        assert isinstance(config.headers, dict)
        assert config.headers == {"Accept": "application/json"}

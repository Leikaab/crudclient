import pytest  # noqa F401

from crudclient.auth.bearer import BearerAuth
from crudclient.config import ClientConfig


class MockClientConfig(ClientConfig):
    hostname = "https://api.example.com"
    version = "v1"
    api_key = "mykey"
    headers = {}
    retries = 3
    timeout = 5

    def __init__(self):
        super().__init__()
        # Set up a BearerAuth strategy with the API key
        if self.api_key:  # Check if api_key is not None
            self.auth_strategy = BearerAuth(token=self.api_key)


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
        # Use the new get_auth_headers method
        auth = config.get_auth_headers()
        assert isinstance(auth, dict)
        assert auth == {"Authorization": f"Bearer {config.api_key}"}

    def test_get_default_headers(self, config):
        config.headers["Accept"] = "application/json"
        assert isinstance(config.headers, dict)
        assert config.headers == {"Accept": "application/json"}

    def test_no_hostname_get(self):
        config = ClientConfig()
        with pytest.raises(ValueError):
            config.base_url

    def test_should_retry_on_403(self):
        config = ClientConfig()
        assert not config.should_retry_on_403()
        assert config.handle_403_retry(None) is None

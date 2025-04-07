import warnings

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

    def test_merge_method(self):
        """Test the new merge method for combining configurations."""
        base_config = ClientConfig(hostname="https://api.example.com", version="v1")
        custom_config = ClientConfig(timeout=30.0, retries=5)

        # Merge the configurations
        merged = base_config.merge(custom_config)

        # Verify the merged configuration has attributes from both sources
        assert merged.hostname == "https://api.example.com"
        assert merged.version == "v1"
        assert merged.timeout == 30.0
        assert merged.retries == 5

        # Verify the original configs are unchanged
        assert base_config.timeout != 30.0
        assert custom_config.hostname is None

    def test_merge_with_headers(self):
        """Test merging configurations with headers."""
        base_config = ClientConfig(headers={"Accept": "application/json"})
        custom_config = ClientConfig(headers={"Content-Type": "application/json"})

        # Merge the configurations
        merged = base_config.merge(custom_config)

        # Verify headers are merged correctly
        assert merged.headers == {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Test header override
        base_config = ClientConfig(headers={"Accept": "application/xml"})
        custom_config = ClientConfig(headers={"Accept": "application/json"})
        merged = base_config.merge(custom_config)
        assert merged.headers is not None
        assert merged.headers["Accept"] == "application/json"  # custom_config takes precedence

    def test_add_operator_deprecation(self):
        """Test that the __add__ operator is deprecated but still works."""
        base_config = ClientConfig(hostname="https://api.example.com")
        custom_config = ClientConfig(timeout=30.0)

        # Capture the deprecation warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            combined = base_config + custom_config

            # Verify the deprecation warning was issued
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message)

        # Verify the combined config has the expected attributes
        assert combined.hostname == "https://api.example.com"
        assert combined.timeout == 30.0

    def test_static_merge_configs(self):
        """Test the static merge_configs method."""
        base_config = ClientConfig(hostname="https://api.example.com", version="v1")
        custom_config = ClientConfig(timeout=30.0, retries=5)

        # Use the static method to merge configs
        merged = ClientConfig.merge_configs(base_config, custom_config)

        # Verify the merged configuration has attributes from both sources
        assert merged.hostname == "https://api.example.com"
        assert merged.version == "v1"
        assert merged.timeout == 30.0
        assert merged.retries == 5

    def test_static_merge_configs_type_error(self):
        """Test that merge_configs raises TypeError for invalid arguments."""
        base_config = ClientConfig()

        # Test with non-ClientConfig objects
        with pytest.raises(TypeError):
            ClientConfig.merge_configs(base_config, "not a config")  # type: ignore

        with pytest.raises(TypeError):
            ClientConfig.merge_configs("not a config", base_config)  # type: ignore

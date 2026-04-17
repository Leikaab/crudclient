import warnings

import pytest  # noqa F401

from crudclient.auth import BearerAuth
from crudclient.config import ClientConfig


class MockClientConfig(ClientConfig):
    hostname = "https://api.example.com"
    version = "v1"
    api_key = "mykey"
    headers = {}
    retries = 3
    timeout = 5

    def __init__(self) -> None:
        super().__init__()
        # Set up a BearerAuth strategy with the API key
        if self.api_key:  # Check if api_key is not None
            self.auth_strategy = BearerAuth(access_token=self.api_key)


class TestClientConfig:
    @pytest.fixture
    def config(self) -> MockClientConfig:
        return MockClientConfig()

    def test_config_initialization(self, config: MockClientConfig) -> None:
        assert config.base_url == "https://api.example.com/v1"
        assert config.api_key == "mykey"
        assert config.headers == {}
        assert config.timeout == 5
        assert config.retries == 3

    def test_config_auth(self, config: MockClientConfig) -> None:
        # Use the new get_auth_headers method
        auth = config.get_auth_headers()
        assert isinstance(auth, dict)
        assert auth == {"Authorization": f"Bearer {config.api_key}"}

    def test_get_default_headers(self, config: MockClientConfig) -> None:
        if config.headers is None:
            config.headers = {}  # type: ignore[unreachable]
        config.headers["Accept"] = "application/json"
        assert isinstance(config.headers, dict)
        assert config.headers == {"Accept": "application/json"}

    def test_no_hostname_get(self) -> None:
        config = ClientConfig()
        with pytest.raises(ValueError):
            config.base_url

    def test_should_retry_on_403(self) -> None:
        config = ClientConfig()
        assert not config.should_retry_on_403()
        # Test that handle_403_retry can be called without error
        config.handle_403_retry(None)

    def test_merge_method(self) -> None:
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

    def test_merge_with_headers(self) -> None:
        """Test merging configurations with headers."""
        base_config = ClientConfig(headers={"Accept": "application/json"})
        custom_config = ClientConfig(headers={"Content-Type": "application/json"})

        # Make copies to ensure originals are not mutated
        base_original = base_config.headers.copy() if base_config.headers is not None else None
        custom_original = custom_config.headers.copy() if custom_config.headers is not None else None

        # Merge the configurations
        merged = base_config.merge(custom_config)

        # Verify headers are merged correctly
        assert merged.headers == {"Accept": "application/json", "Content-Type": "application/json"}
        # Originals should remain unchanged
        assert base_config.headers == base_original
        assert custom_config.headers == custom_original

        # Test header override
        base_config = ClientConfig(headers={"Accept": "application/xml"})
        custom_config = ClientConfig(headers={"Accept": "application/json"})
        merged = base_config.merge(custom_config)
        assert merged.headers is not None
        assert merged.headers["Accept"] == "application/json"  # custom_config takes precedence

    def test_add_operator_deprecation(self) -> None:
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

    def test_static_merge_configs(self) -> None:
        """Test the static merge_configs method."""
        base_config = ClientConfig(hostname="https://api.example.com", version="v1")
        custom_config = ClientConfig(timeout=30.0, retries=5)

        base_original = base_config.headers.copy() if base_config.headers is not None else None
        custom_original = custom_config.headers.copy() if custom_config.headers is not None else None

        # Use the static method to merge configs
        merged = ClientConfig.merge_configs(base_config, custom_config)

        # Verify the merged configuration has attributes from both sources
        assert merged.hostname == "https://api.example.com"
        assert merged.version == "v1"
        assert merged.timeout == 30.0
        assert merged.retries == 5

        assert base_config.headers == base_original
        assert custom_config.headers == custom_original

    def test_static_merge_configs_type_error(self) -> None:
        """Test that merge_configs raises AttributeError for invalid arguments."""
        base_config = ClientConfig()

        # Test with non-ClientConfig objects - apiconfig raises AttributeError
        # when trying to call .merge() on a string
        with pytest.raises(AttributeError, match="'str' object has no attribute 'merge'"):
            ClientConfig.merge_configs("not a config", base_config)  # type: ignore

        # This one should raise TypeError from the instance merge method
        with pytest.raises(TypeError, match="Cannot merge ClientConfig with object of type"):
            ClientConfig.merge_configs(base_config, "not a config")  # type: ignore

    def test_get_config_errors(self) -> None:
        """Validate get_config_errors reports missing hostname."""
        cfg = ClientConfig()
        assert cfg.get_config_errors() == {"hostname": "hostname is required"}

        cfg = ClientConfig(hostname="https://example.com")
        assert cfg.get_config_errors() == {}

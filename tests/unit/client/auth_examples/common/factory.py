from crudclient.testing.auth import create_api_key_auth_mock, create_basic_auth_mock, create_bearer_auth_mock, create_custom_auth_mock
from crudclient.testing.core.http_client import MockHTTPClient

# Import the backward compatible client from the new location
from .client import BackwardCompatibleMockClient


# Function for backward compatibility
def create_mock_client(**kwargs):
    """Create a mock client with the given configuration."""
    # Create a mock HTTP client
    base_url = kwargs.get('base_url', "https://api.example.com")
    http_client = MockHTTPClient(base_url=base_url)

    # Create a mock client with the mock HTTP client
    enable_spy = kwargs.get('enable_spy', False)
    mock_client = BackwardCompatibleMockClient(
        http_client=http_client,
        enable_spy=enable_spy
    )

    # Configure auth if specified
    if 'auth_type' in kwargs and 'auth_config' in kwargs:
        auth_type = kwargs['auth_type']
        auth_config = kwargs['auth_config']

        # Check if this is a failure scenario
        # Note: Failure scenarios are now primarily handled by configuring
        # 401/403 responses in the test itself using with_response_pattern.
        # The auth mock setup here focuses on creating the strategy.

        # Configure the auth strategy
        if auth_type == "basic":
            basic_auth_mock = create_basic_auth_mock(
                username=auth_config.get('username', ''),
                password=auth_config.get('password', '')
            )
            mock_client.set_auth_strategy(basic_auth_mock.get_auth_strategy())
        elif auth_type == "bearer":
            bearer_auth_mock = create_bearer_auth_mock(
                token=auth_config.get('token', '')
            )
            # Handle bearer-specific failure flags if needed for mock setup
            # (e.g., token_expired - though actual failure is response-driven)
            # bearer_auth_mock.token_expired = auth_config.get('token_expired', False)
            mock_client.set_auth_strategy(bearer_auth_mock.get_auth_strategy())
        elif auth_type == "apikey":
            api_key_auth_mock = create_api_key_auth_mock(
                api_key=auth_config.get('api_key', ''),
                header_name=auth_config.get('header_name'),
                param_name=auth_config.get('param_name')
            )
            mock_client.set_auth_strategy(api_key_auth_mock.get_auth_strategy())
        elif auth_type == "custom":
            custom_auth_mock = create_custom_auth_mock(
                header_callback=auth_config.get('header_callback'),
                param_callback=auth_config.get('param_callback')
            )
            mock_client.set_auth_strategy(custom_auth_mock.get_auth_strategy())
        # Note: MFA logic is handled separately, often involving response configuration

    return mock_client

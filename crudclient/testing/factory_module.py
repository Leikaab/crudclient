
from typing import Any, Optional

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.core.client import MockClient
from crudclient.testing.core.http_client import MockHTTPClient
from crudclient.testing.types import Headers, ResponseData, StatusCode


class MockClientFactory:

    @classmethod
    def create(
        cls,
        base_url: str = "https://api.example.com",
        enable_spy: bool = False,
        **kwargs: Any
    ) -> MockClient:
        # Create a mock HTTP client
        http_client = MockHTTPClient(base_url=base_url)

        # Create a mock client with the mock HTTP client
        mock_client = MockClient(
            http_client=http_client,
            enable_spy=enable_spy,
            **kwargs
        )

        return mock_client

    @classmethod
    def from_client_config(
        cls,
        config: ClientConfig,
        enable_spy: bool = False,
        **kwargs: Any
    ) -> MockClient:
        # Extract the base URL from the config
        base_url = config.hostname or "https://api.example.com"

        # Create a mock client with the base URL
        mock_client = cls.create(
            base_url=base_url,
            enable_spy=enable_spy,
            **kwargs
        )

        # Configure the mock client with the auth strategy from the config
        if config.auth_strategy is not None:
            mock_client.set_auth_strategy(config.auth_strategy)

        return mock_client

    @classmethod
    def from_real_client(
        cls,
        client: Client,
        enable_spy: bool = False,
        **kwargs: Any
    ) -> MockClient:
        # Extract the config from the real client
        config = client.config

        # Create a mock client from the config
        mock_client = cls.from_client_config(
            config=config,
            enable_spy=enable_spy,
            **kwargs
        )

        return mock_client

    @classmethod
    def configure_success_response(
        cls,
        mock_client: MockClient,
        method: str,
        path: str,
        data: Optional[ResponseData] = None,
        status_code: StatusCode = 200,
        headers: Optional[Headers] = None
    ) -> None:
        mock_client.configure_response(
            method=method,
            path=path,
            status_code=status_code,
            data=data,
            headers=headers
        )

    @classmethod
    def configure_error_response(
        cls,
        mock_client: MockClient,
        method: str,
        path: str,
        status_code: StatusCode = 400,
        data: Optional[ResponseData] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None
    ) -> None:
        if error is not None:
            mock_client.configure_response(
                method=method,
                path=path,
                error=error
            )
        else:
            mock_client.configure_response(
                method=method,
                path=path,
                status_code=status_code,
                data=data,
                headers=headers
            )

# crudclient/testing/mock_client_factory.pyi

from typing import Any, Dict, Optional, Union

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.core.client import MockClient
from crudclient.testing.types import Headers, ResponseData, StatusCode

class MockClientFactory:
    @classmethod
    def create(
        cls,
        base_url: str = "https://api.example.com",
        enable_spy: bool = False,
        config: Optional[ClientConfig] = None,
        **kwargs: Any,
    ) -> MockClient: ...
    @classmethod
    def from_client_config(cls, config: ClientConfig, enable_spy: bool = False, **kwargs: Any) -> MockClient: ...
    @classmethod
    def from_real_client(cls, client: Client, enable_spy: bool = False, **kwargs: Any) -> MockClient: ...
    @classmethod
    def configure_success_response(
        cls,
        mock_client: MockClient,
        method: str,
        path: str,
        data: Optional[ResponseData] = None,
        status_code: StatusCode = 200,
        headers: Optional[Headers] = None,
    ) -> None: ...
    @classmethod
    def configure_error_response(
        cls,
        mock_client: MockClient,
        method: str,
        path: str,
        status_code: StatusCode = 400,
        data: Optional[ResponseData] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None,
    ) -> None: ...
    @classmethod
    def create_mock_client(cls, config: Optional[Union[ClientConfig, Dict[str, Any]]] = None, **kwargs: Any) -> MockClient: ...

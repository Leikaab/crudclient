# crudclient/testing/factory_helpers.pyi

from typing import Any, Dict, List, Optional, Union

from crudclient.testing.auth import (
    ApiKeyAuthMock,
    BasicAuthMock,
    BearerAuthMock,
    CustomAuthMock,
    OAuthMock,
)
from crudclient.testing.core.client import MockClient
from crudclient.testing.simple_mock import SimpleMockClient

def _create_api_patterns(api_type: str, **kwargs: Any) -> List[Dict[str, Any]]: ...
def _add_error_responses(client: MockClient, error_configs: Dict[str, Any]) -> None: ...
def _configure_auth_mock(
    auth_mock: Union[BasicAuthMock, BearerAuthMock, ApiKeyAuthMock, CustomAuthMock, OAuthMock], config: Dict[str, Any]
) -> None: ...
def _add_error_responses_to_simple_mock(client: SimpleMockClient, error_configs: Dict[str, Any]) -> None: ...

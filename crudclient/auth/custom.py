from typing import Callable, Dict, Optional

from crudclient.auth.base import AuthStrategy


class CustomAuth(AuthStrategy):

    def __init__(
        self,
        header_callback: Callable[[], Dict[str, str]],
        param_callback: Optional[Callable[[], Dict[str, str]]] = None
    ):
        self.header_callback = header_callback
        self.param_callback = param_callback

    def prepare_request_headers(self) -> Dict[str, str]:
        return self.header_callback()

    def prepare_request_params(self) -> Dict[str, str]:
        if self.param_callback:
            return self.param_callback()
        return {}


class ApiKeyAuth(AuthStrategy):

    def __init__(
        self,
        api_key: str,
        header_name: str = "X-API-Key",
        param_name: Optional[str] = None
    ):
        self.api_key = api_key
        self.header_name = header_name
        self.param_name = param_name

    def prepare_request_headers(self) -> Dict[str, str]:
        if not self.param_name:
            return {self.header_name: self.api_key}
        return {}

    def prepare_request_params(self) -> Dict[str, str]:
        if self.param_name:
            return {self.param_name: self.api_key}
        return {}

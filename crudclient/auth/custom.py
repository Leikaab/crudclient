import logging
from typing import Callable, Dict, Optional

from crudclient.auth.base import AuthStrategy

log = logging.getLogger(__name__)


class CustomAuth(AuthStrategy):

    def __init__(self, header_callback: Optional[Callable[[], Dict[str, str]]] = None, param_callback: Optional[Callable[[], Dict[str, str]]] = None):
        if header_callback is None and param_callback is None:
            raise ValueError("At least one callback must be provided")
        self.header_callback = header_callback
        self.param_callback = param_callback

    def prepare_request_headers(self) -> Dict[str, str]:
        if self.header_callback:
            log.debug("[CustomAuth] Invoking custom header callback to modify request")
            result = self.header_callback()
            if not isinstance(result, dict):
                raise TypeError("Header callback must return a dictionary")
            return result
        return {}

    def prepare_request_params(self) -> Dict[str, str]:
        if self.param_callback:
            log.debug("[CustomAuth] Invoking custom parameter callback to modify request")
            result = self.param_callback()
            if not isinstance(result, dict):
                raise TypeError("Parameter callback must return a dictionary")
            return result
        return {}


class ApiKeyAuth(AuthStrategy):

    def __init__(self, api_key: str, header_name: Optional[str] = None, param_name: Optional[str] = None):
        self.api_key = api_key
        self.header_name = header_name
        self.param_name = param_name

        # Validate that at least one of header_name or param_name is provided
        if header_name is None and param_name is None:
            raise ValueError("One of header_name or param_name must be provided")

        # Validate that only one of header_name or param_name is provided
        if header_name is not None and param_name is not None:
            raise ValueError("Only one of header_name or param_name should be provided")

    def prepare_request_headers(self) -> Dict[str, str]:
        if self.header_name is not None:
            return {self.header_name: self.api_key}
        return {}

    def prepare_request_params(self) -> Dict[str, str]:
        if self.param_name is not None:
            return {self.param_name: self.api_key}
        return {}

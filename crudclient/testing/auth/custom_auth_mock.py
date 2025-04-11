from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple  # Added Tuple, TYPE_CHECKING

from crudclient.auth.base import AuthStrategy
from crudclient.auth.custom import CustomAuth

from .base import AuthMockBase

if TYPE_CHECKING:  # Added TYPE_CHECKING block
    from ..response_builder import MockResponse


class CustomAuthMock(AuthMockBase):
    def __init__(self, header_callback: Optional[Callable[[], Dict[str, str]]] = None, param_callback: Optional[Callable[[], Dict[str, str]]] = None):
        super().__init__()

        # Default callbacks if none provided
        def default_header_callback():
            return {"X-Custom-Auth": "custom_value"}

        if header_callback is None and param_callback is None:
            header_callback = default_header_callback

        self.header_callback = header_callback
        self.param_callback = param_callback
        # Create a safe header callback that handles None
        safe_header_callback = header_callback if header_callback else lambda: {}

        self.auth_strategy = CustomAuth(header_callback=safe_header_callback, param_callback=param_callback)

        # Additional properties for enhanced functionality
        self.expected_headers: Dict[str, str] = {}
        self.expected_params: Dict[str, str] = {}
        self.required_headers: List[str] = []
        self.required_params: List[str] = []
        self.header_validators: Dict[str, Callable[[str], bool]] = {}
        self.param_validators: Dict[str, Callable[[str], bool]] = {}

    def with_header_callback(self, callback: Callable[[], Dict[str, str]]) -> "CustomAuthMock":
        self.header_callback = callback
        self.auth_strategy = CustomAuth(header_callback=callback, param_callback=self.param_callback)
        return self

    def with_param_callback(self, callback: Callable[[], Dict[str, str]]) -> "CustomAuthMock":
        self.param_callback = callback
        # Create a safe header callback that handles None
        safe_header_callback = self.header_callback if self.header_callback else lambda: {}

        self.auth_strategy = CustomAuth(header_callback=safe_header_callback, param_callback=callback)
        return self

    def with_expected_header(self, name: str, value: str) -> "CustomAuthMock":
        self.expected_headers[name] = value
        return self

    def with_expected_param(self, name: str, value: str) -> "CustomAuthMock":
        self.expected_params[name] = value
        return self

    def with_required_header(self, name: str) -> "CustomAuthMock":
        if name not in self.required_headers:
            self.required_headers.append(name)
        return self

    def with_required_param(self, name: str) -> "CustomAuthMock":
        if name not in self.required_params:
            self.required_params.append(name)
        return self

    def with_header_validator(self, name: str, validator: Callable[[str], bool]) -> "CustomAuthMock":
        self.header_validators[name] = validator
        return self

    def with_param_validator(self, name: str, validator: Callable[[str], bool]) -> "CustomAuthMock":
        self.param_validators[name] = validator
        return self

    def verify_headers(self, headers: Dict[str, str]) -> bool:
        # Check required headers
        for name in self.required_headers:
            if name not in headers:
                return False

        # Check expected header values
        for name, expected_value in self.expected_headers.items():
            if name not in headers or headers[name] != expected_value:
                return False

        # Apply custom validators
        for name, validator in self.header_validators.items():
            if name in headers and not validator(headers[name]):
                return False

        return True

    def verify_params(self, params: Dict[str, str]) -> bool:
        # Check required parameters
        for name in self.required_params:
            if name not in params:
                return False

        # Check expected parameter values
        for name, expected_value in self.expected_params.items():
            if name not in params or params[name] != expected_value:
                return False

        # Apply custom validators
        for name, validator in self.param_validators.items():
            if name in params and not validator(params[name]):
                return False

        return True

    def get_auth_strategy(self) -> AuthStrategy:
        return self.auth_strategy

    # --- Added Abstract Method Implementations ---

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        # Headers are applied via the header_callback in the actual strategy.
        # This method signature in the mock base doesn't perfectly align.
        return None

    def handle_auth_error(self, response: "MockResponse") -> bool:
        # No standard refresh mechanism defined for generic custom auth mock
        return False

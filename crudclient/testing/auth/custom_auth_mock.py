from typing import Callable, Dict, List, Optional

from crudclient.auth.base import AuthStrategy
from crudclient.auth.custom import CustomAuth

from .base import AuthMockBase


class CustomAuthMock(AuthMockBase):
    def __init__(
        self,
        header_callback: Optional[Callable[[], Dict[str, str]]] = None,
        param_callback: Optional[Callable[[], Dict[str, str]]] = None
    ):
        super().__init__()

        # Default callbacks if none provided
        def default_header_callback(): return {"X-Custom-Auth": "custom_value"}
        if header_callback is None and param_callback is None:
            header_callback = default_header_callback

        self.header_callback = header_callback
        self.param_callback = param_callback
        # Create a safe header callback that handles None
        safe_header_callback = header_callback if header_callback else lambda: {}

        self.auth_strategy = CustomAuth(
            header_callback=safe_header_callback,
            param_callback=param_callback
        )

        # Additional properties for enhanced functionality
        self.expected_headers: Dict[str, str] = {}
        self.expected_params: Dict[str, str] = {}
        self.required_headers: List[str] = []
        self.required_params: List[str] = []
        self.header_validators: Dict[str, Callable[[str], bool]] = {}
        self.param_validators: Dict[str, Callable[[str], bool]] = {}

    def with_header_callback(self, callback: Callable[[], Dict[str, str]]) -> 'CustomAuthMock':
        """
        Set the header callback for the Custom Auth mock.

        Args:
            callback: Callback function that returns authentication headers

        Returns:
            Self for method chaining
        """
        self.header_callback = callback
        self.auth_strategy = CustomAuth(
            header_callback=callback,
            param_callback=self.param_callback
        )
        return self

    def with_param_callback(self, callback: Callable[[], Dict[str, str]]) -> 'CustomAuthMock':
        """
        Set the parameter callback for the Custom Auth mock.

        Args:
            callback: Callback function that returns authentication parameters

        Returns:
            Self for method chaining
        """
        self.param_callback = callback
        # Create a safe header callback that handles None
        safe_header_callback = self.header_callback if self.header_callback else lambda: {}

        self.auth_strategy = CustomAuth(
            header_callback=safe_header_callback,
            param_callback=callback
        )
        return self

    def with_expected_header(self, name: str, value: str) -> 'CustomAuthMock':
        """
        Set an expected header for validation.

        Args:
            name: Header name
            value: Expected header value

        Returns:
            Self for method chaining
        """
        self.expected_headers[name] = value
        return self

    def with_expected_param(self, name: str, value: str) -> 'CustomAuthMock':
        """
        Set an expected parameter for validation.

        Args:
            name: Parameter name
            value: Expected parameter value

        Returns:
            Self for method chaining
        """
        self.expected_params[name] = value
        return self

    def with_required_header(self, name: str) -> 'CustomAuthMock':
        """
        Add a required header for validation.

        Args:
            name: Required header name

        Returns:
            Self for method chaining
        """
        if name not in self.required_headers:
            self.required_headers.append(name)
        return self

    def with_required_param(self, name: str) -> 'CustomAuthMock':
        """
        Add a required parameter for validation.

        Args:
            name: Required parameter name

        Returns:
            Self for method chaining
        """
        if name not in self.required_params:
            self.required_params.append(name)
        return self

    def with_header_validator(self, name: str, validator: Callable[[str], bool]) -> 'CustomAuthMock':
        """
        Add a custom validator for a header.

        Args:
            name: Header name
            validator: Function that validates the header value

        Returns:
            Self for method chaining
        """
        self.header_validators[name] = validator
        return self

    def with_param_validator(self, name: str, validator: Callable[[str], bool]) -> 'CustomAuthMock':
        """
        Add a custom validator for a parameter.

        Args:
            name: Parameter name
            validator: Function that validates the parameter value

        Returns:
            Self for method chaining
        """
        self.param_validators[name] = validator
        return self

    def verify_headers(self, headers: Dict[str, str]) -> bool:
        """
        Verify that the headers meet all requirements.

        Args:
            headers: The headers to verify

        Returns:
            True if the headers are valid, False otherwise
        """
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
        """
        Verify that the parameters meet all requirements.

        Args:
            params: The parameters to verify

        Returns:
            True if the parameters are valid, False otherwise
        """
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
        """
        Get the configured auth strategy.

        Returns:
            The configured CustomAuth strategy
        """
        return self.auth_strategy

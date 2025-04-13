"""
Custom authentication mock for testing.

This module provides a mock for Custom Authentication strategy with enhanced
validation capabilities for headers and parameters.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple

from crudclient.auth.base import AuthStrategy
from crudclient.auth.custom import CustomAuth

from ..response_builder.response import MockResponse
from ..spy.enhanced import EnhancedSpyBase, FunctionSpy
from .base import AuthMockBase

class CustomAuthMock(EnhancedSpyBase, AuthMockBase):
    """
    Mock for Custom Authentication strategy with enhanced capabilities.

    This class provides a configurable mock implementation of the Custom Authentication
    strategy, with support for header and parameter callbacks, validation, and error simulation.
    """

    _original_header_callback: Optional[Callable[[], Dict[str, str]]]
    _original_param_callback: Optional[Callable[[], Dict[str, str]]]
    header_callback_spy: Optional[FunctionSpy]
    param_callback_spy: Optional[FunctionSpy]
    auth_strategy: CustomAuth
    expected_headers: Dict[str, str]
    expected_params: Dict[str, str]
    required_headers: List[str]
    required_params: List[str]
    header_validators: Dict[str, Callable[[str], bool]]
    param_validators: Dict[str, Callable[[str], bool]]

    def __init__(
        self, header_callback: Optional[Callable[[], Dict[str, str]]] = None, param_callback: Optional[Callable[[], Dict[str, str]]] = None
    ) -> None:
        """
        Initialize a Custom Authentication mock.

        Args:
            header_callback: Callback function that returns authentication headers
            param_callback: Callback function that returns authentication parameters
        """
        ...

    def with_header_callback(self, callback: Callable[[], Dict[str, str]]) -> "CustomAuthMock":
        """
        Set the header callback for the Custom Auth mock.

        Args:
            callback: Callback function that returns authentication headers

        Returns:
            Self for method chaining
        """
        ...

    def with_param_callback(self, callback: Callable[[], Dict[str, str]]) -> "CustomAuthMock":
        """
        Set the parameter callback for the Custom Auth mock.

        Args:
            callback: Callback function that returns authentication parameters

        Returns:
            Self for method chaining
        """
        ...

    def with_expected_header(self, name: str, value: str) -> "CustomAuthMock":
        """
        Set an expected header for validation.

        Args:
            name: Header name
            value: Expected header value

        Returns:
            Self for method chaining
        """
        ...

    def with_expected_param(self, name: str, value: str) -> "CustomAuthMock":
        """
        Set an expected parameter for validation.

        Args:
            name: Parameter name
            value: Expected parameter value

        Returns:
            Self for method chaining
        """
        ...

    def with_required_header(self, name: str) -> "CustomAuthMock":
        """
        Add a required header for validation.

        Args:
            name: Required header name

        Returns:
            Self for method chaining
        """
        ...

    def with_required_param(self, name: str) -> "CustomAuthMock":
        """
        Add a required parameter for validation.

        Args:
            name: Required parameter name

        Returns:
            Self for method chaining
        """
        ...

    def with_header_validator(self, name: str, validator: Callable[[str], bool]) -> "CustomAuthMock":
        """
        Add a custom validator for a header.

        Args:
            name: Header name
            validator: Function that validates the header value

        Returns:
            Self for method chaining
        """
        ...

    def with_param_validator(self, name: str, validator: Callable[[str], bool]) -> "CustomAuthMock":
        """
        Add a custom validator for a parameter.

        Args:
            name: Parameter name
            validator: Function that validates the parameter value

        Returns:
            Self for method chaining
        """
        ...

    def verify_headers(self, headers: Dict[str, str]) -> bool:
        """
        Verify that the headers meet all requirements.

        Args:
            headers: The headers to verify

        Returns:
            True if the headers are valid, False otherwise
        """
        ...

    def verify_params(self, params: Dict[str, str]) -> bool:
        """
        Verify that the parameters meet all requirements.

        Args:
            params: The parameters to verify

        Returns:
            True if the parameters are valid, False otherwise
        """
        ...

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the configured auth strategy.

        Returns:
            The configured CustomAuth strategy
        """
        ...

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        """
        Get the authentication headers for the current token.

        Returns:
            None for CustomAuthMock as headers are applied via callbacks
        """
        ...

    def handle_auth_error(self, response: MockResponse) -> bool:
        """
        Handle authentication errors.

        Args:
            response: The error response that triggered the auth error

        Returns:
            False as no standard refresh mechanism is defined for custom auth
        """
        ...

    def get_calls(self, method_name: Optional[str] = None) -> List[Any]:
        """
        Get all recorded calls or calls for a specific method.

        Args:
            method_name: Optional name of method to filter calls by

        Returns:
            List of call records
        """
        ...

    def get_call_count(self, method_name: Optional[str] = None) -> int:
        """
        Get the number of calls made to all methods or a specific method.

        Args:
            method_name: Optional name of method to count calls for

        Returns:
            Number of calls
        """
        ...

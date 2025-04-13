import time
from typing import TYPE_CHECKING, Callable, Dict, List, Optional, Tuple

from crudclient.auth.base import AuthStrategy
from crudclient.auth.custom import CustomAuth

# Import necessary components from spy and base auth mock
from ..spy.enhanced import EnhancedSpyBase, FunctionSpy
from .base import AuthMockBase

if TYPE_CHECKING:
    from ..response_builder import MockResponse


# Inherit from both EnhancedSpyBase (for spying) and AuthMockBase (for auth mock state/config)
class CustomAuthMock(EnhancedSpyBase, AuthMockBase):
    def __init__(self, header_callback: Optional[Callable[[], Dict[str, str]]] = None, param_callback: Optional[Callable[[], Dict[str, str]]] = None):
        # Initialize both base classes
        EnhancedSpyBase.__init__(self)
        AuthMockBase.__init__(self)

        # --- Callback Handling with Spying ---
        # Store original callbacks separately if needed, wrap provided ones with FunctionSpy
        self._original_header_callback = header_callback
        self._original_param_callback = param_callback

        # Default callbacks if none provided
        def default_header_callback():
            return {"X-Custom-Auth": "custom_value"}

        if header_callback is None and param_callback is None:
            self._original_header_callback = default_header_callback

        # Wrap callbacks with FunctionSpy
        self.header_callback_spy = FunctionSpy(self._original_header_callback, record_only=False) if self._original_header_callback else None
        # FunctionSpy records calls internally, no need to set .spy

        self.param_callback_spy = FunctionSpy(self._original_param_callback, record_only=False) if self._original_param_callback else None
        # FunctionSpy records calls internally, no need to set .spy

        # Use the spied callbacks (or lambdas if None) for the actual auth strategy
        safe_spied_header_callback = self.header_callback_spy if self.header_callback_spy else lambda: {}
        spied_param_callback = self.param_callback_spy if self.param_callback_spy else None

        self.auth_strategy = CustomAuth(header_callback=safe_spied_header_callback, param_callback=spied_param_callback)

        # Additional properties for enhanced functionality
        self.expected_headers: Dict[str, str] = {}
        self.expected_params: Dict[str, str] = {}
        self.required_headers: List[str] = []
        self.required_params: List[str] = []
        self.header_validators: Dict[str, Callable[[str], bool]] = {}
        self.param_validators: Dict[str, Callable[[str], bool]] = {}

    def with_header_callback(self, callback: Callable[[], Dict[str, str]]) -> "CustomAuthMock":
        self._original_header_callback = callback
        self.header_callback_spy = FunctionSpy(callback, record_only=False)
        # FunctionSpy records calls internally, no need to set .spy
        # Use the new spied callback
        spied_param_callback = self.param_callback_spy if self.param_callback_spy else None
        self.auth_strategy = CustomAuth(header_callback=self.header_callback_spy, param_callback=spied_param_callback)
        return self

    def with_param_callback(self, callback: Callable[[], Dict[str, str]]) -> "CustomAuthMock":
        self._original_param_callback = callback
        self.param_callback_spy = FunctionSpy(callback, record_only=False)
        # FunctionSpy records calls internally, no need to set .spy
        # Use the new spied callback
        safe_spied_header_callback = self.header_callback_spy if self.header_callback_spy else lambda: {}
        self.auth_strategy = CustomAuth(header_callback=safe_spied_header_callback, param_callback=self.param_callback_spy)
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
        # Record the call to this verification method
        start_time = time.time()
        result = False
        exception = None
        try:
            result = True  # Assume true initially
            # Check required headers
            for name in self.required_headers:
                if name not in headers:
                    result = False
                    break
            if not result:
                return False  # Early exit

            # Check expected header values
            for name, expected_value in self.expected_headers.items():
                if name not in headers or headers[name] != expected_value:
                    result = False
                    break
            if not result:
                return False  # Early exit

            # Apply custom validators
            for name, validator in self.header_validators.items():
                if name in headers and not validator(headers[name]):
                    result = False
                    break
            if not result:
                return False  # Early exit

            return result  # Return the final result
        except Exception as e:
            exception = e
            raise
        finally:
            duration = time.time() - start_time
            self._record_call(method_name="verify_headers", args=(headers,), kwargs={}, result=result, exception=exception, duration=duration)

    def verify_params(self, params: Dict[str, str]) -> bool:
        start_time = time.time()
        result = True  # Assume success initially
        exception = None
        try:
            # Check required parameters
            for name in self.required_params:
                if name not in params:
                    result = False
                    break  # Exit loop on first failure
            if not result:
                return False  # Return early

            # Check expected parameter values
            for name, expected_value in self.expected_params.items():
                if name not in params or params[name] != expected_value:
                    result = False
                    break  # Exit loop on first failure
            if not result:
                return False  # Return early

            # Apply custom validators
            for name, validator in self.param_validators.items():
                if name in params and not validator(params[name]):
                    result = False
                    break  # Exit loop on first failure
            if not result:
                return False  # Return early

            # If we reach here, all checks passed
            return True

        except Exception as e:
            exception = e
            result = False  # Verification failed due to exception
            raise  # Re-raise the exception after recording
        finally:
            # Record the call regardless of outcome
            duration = time.time() - start_time
            # Result is False if any check failed or an exception occurred
            final_result = result and exception is None
            self._record_call(method_name="verify_params", args=(params,), kwargs={}, result=final_result, exception=exception, duration=duration)
            # If an exception occurred, the raise above will propagate it.
            # If no exception, the return value from the try block (or early return) is used.

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

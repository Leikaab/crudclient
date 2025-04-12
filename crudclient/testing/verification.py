from typing import Any, List, TypeVar, Union, cast

from .exceptions import VerificationError
from .types import SpyTarget  # Keep the import for documentation purposes

# Type variable for target objects
T = TypeVar("T", bound=Union[SpyTarget, object])


class Verifier:
    @staticmethod
    def _check_target_has_calls(target: T) -> SpyTarget:
        if not hasattr(target, "calls"):
            raise VerificationError(f"Target object {target} does not have 'calls' attribute")
        return cast(SpyTarget, target)

    @staticmethod
    def _format_args_string(*args: Any, **kwargs: Any) -> str:
        args_str = ", ".join(str(arg) for arg in args)
        kwargs_str = ", ".join(f"{key}={value}" for key, value in kwargs.items())
        return ", ".join(filter(None, [args_str, kwargs_str]))

    @staticmethod
    def verify_called_with(target: Union[SpyTarget, object], method_name: str, *args: Any, **kwargs: Any) -> bool:
        spy_target = Verifier._check_target_has_calls(target)

        for call in spy_target.calls:
            if call.method_name == method_name:
                # Check positional arguments
                if len(args) > 0 and call.args != args:
                    continue

                # Check keyword arguments
                if kwargs and not all(key in call.kwargs and call.kwargs[key] == value for key, value in kwargs.items()):
                    continue

                return True

        all_args = Verifier._format_args_string(*args, **kwargs)
        raise VerificationError(f"Method {method_name} was not called with arguments ({all_args})")

    @staticmethod
    def verify_called_once_with(target: Union[SpyTarget, object], method_name: str, *args: Any, **kwargs: Any) -> bool:
        spy_target = Verifier._check_target_has_calls(target)

        matching_calls: List[Any] = []

        for call in spy_target.calls:
            if call.method_name == method_name:
                # Check positional arguments
                if len(args) > 0 and call.args != args:
                    continue

                # Check keyword arguments
                if kwargs and not all(key in call.kwargs and call.kwargs[key] == value for key, value in kwargs.items()):
                    continue

                matching_calls.append(call)

        if len(matching_calls) == 1:
            return True

        all_args = Verifier._format_args_string(*args, **kwargs)

        if len(matching_calls) == 0:
            raise VerificationError(f"Method {method_name} was not called with arguments ({all_args})")
        else:
            raise VerificationError(f"Method {method_name} was called {len(matching_calls)} times with arguments ({all_args}), expected exactly once")

    @staticmethod
    def verify_not_called(target: Union[SpyTarget, object], method_name: str) -> bool:
        spy_target = Verifier._check_target_has_calls(target)

        for call in spy_target.calls:
            if call.method_name == method_name:
                raise VerificationError(f"Method {method_name} was called")

        return True

    @staticmethod
    def verify_call_count(target: Union[SpyTarget, object], method_name: str, count: int) -> bool:
        spy_target = Verifier._check_target_has_calls(target)

        actual_count = sum(1 for call in spy_target.calls if call.method_name == method_name)

        if actual_count != count:
            raise VerificationError(f"Method {method_name} was called {actual_count} times, expected {count} times")

        return True

    @staticmethod
    def verify_any_call(target: Union[SpyTarget, object], method_name: str, *args: Any, **kwargs: Any) -> bool:
        spy_target = Verifier._check_target_has_calls(target)

        for call in spy_target.calls:
            if call.method_name == method_name:
                # Check positional arguments
                if len(args) > 0 and call.args != args:
                    continue

                # Check keyword arguments
                if kwargs and not all(key in call.kwargs and call.kwargs[key] == value for key, value in kwargs.items()):
                    continue

                return True

        all_args = Verifier._format_args_string(*args, **kwargs)
        raise VerificationError(f"Method {method_name} was not called with arguments ({all_args})")

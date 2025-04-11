from typing import Any, Dict, List, Optional, Tuple

from .method_call import MethodCall


class SpyBase:

    def __init__(self):
        self.calls: List[MethodCall] = []

    def _record_call(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        return_value: Optional[Any] = None,
        exception: Optional[Exception] = None,
    ) -> None:
        call = MethodCall(method_name, args, kwargs, return_value, exception)
        self.calls.append(call)

    def assert_called(self, method_name: str) -> None:
        for call in self.calls:
            if call.method_name == method_name:
                return

        raise AssertionError(f"Method {method_name} was not called")

    def assert_not_called(self, method_name: str) -> None:
        for call in self.calls:
            if call.method_name == method_name:
                raise AssertionError(f"Method {method_name} was called")

    def assert_called_with(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        for call in self.calls:
            if call.method_name == method_name:
                # Check positional arguments
                if len(args) > 0 and call.args != args:
                    continue

                # Check keyword arguments
                if kwargs and not all(key in call.kwargs and call.kwargs[key] == value for key, value in kwargs.items()):
                    continue

                return

        args_str = ", ".join(str(arg) for arg in args)
        kwargs_str = ", ".join(f"{key}={value}" for key, value in kwargs.items())
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))

        raise AssertionError(f"Method {method_name} was not called with arguments ({all_args})")

    def assert_call_count(self, method_name: str, count: int) -> None:
        actual_count = sum(1 for call in self.calls if call.method_name == method_name)

        if actual_count != count:
            raise AssertionError(f"Method {method_name} was called {actual_count} times, " f"expected {count} times")

    def get_calls(self, method_name: str) -> List[MethodCall]:
        return [call for call in self.calls if call.method_name == method_name]

    def clear_calls(self) -> None:
        self.calls = []

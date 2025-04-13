from typing import Any, Callable, Dict, List

# Type hint for EnhancedSpyBase to avoid circular import
# In a real scenario, consider using typing.TYPE_CHECKING or protocols
EnhancedSpyBase = Any


class SpyAssertionsMixin:

    def assert_called(self: Any, method_name: str) -> None:
        assert self.was_called(method_name), f"Expected method '{method_name}' to have been called, but it was not."

    def assert_not_called(self: Any, method_name: str) -> None:
        assert not self.was_called(method_name), f"Expected method '{method_name}' not to have been called, but it was."

    def assert_called_with(self: Any, method_name: str, *args: Any, **kwargs: Any) -> None:
        assert self.was_called_with(method_name, *args, **kwargs), (
            f"Expected method '{method_name}' to have been called with args={args}, kwargs={kwargs}. " f"Actual calls: {self.get_calls(method_name)}"
        )  # Include actual calls for better debugging

    def assert_called_once(self: Any, method_name: str) -> None:
        call_count = self.get_call_count(method_name)
        assert call_count == 1, f"Expected method '{method_name}' to be called once, but was called {call_count} times."

    def assert_called_times(self: Any, method_name: str, count: int) -> None:
        call_count = self.get_call_count(method_name)
        assert call_count == count, f"Expected method '{method_name}' to be called {count} times, but was called {call_count} times."

    def assert_called_with_params_matching(self: Any, method_name: str, param_matcher: Callable[[Dict[str, Any]], bool]) -> None:
        if not self.was_called(method_name):
            raise AssertionError(f"Method {method_name} was not called")

        # Use get_calls to avoid accessing protected member _method_calls directly
        calls_for_method = self.get_calls(method_name)
        if not calls_for_method:
            # This case should theoretically be caught by was_called, but added for safety
            raise AssertionError(f"Method {method_name} was not called (no records found)")

        for call in calls_for_method:
            # Combine args and kwargs into a single dict
            params: Dict[str, Any] = {}

            # Add positional args with their index as key
            for i, arg in enumerate(call.args):
                params[f"arg{i}"] = arg

            # Add keyword args
            params.update(call.kwargs)

            if param_matcher(params):
                return

        raise AssertionError(f"Method {method_name} was not called with matching parameters")

    def assert_call_order(self: Any, *method_names: str) -> None:
        # Check that all methods were called
        for method_name in method_names:
            if not self.was_called(method_name):
                raise AssertionError(f"Method {method_name} was not called")

        # Check the order using the public get_calls()
        all_calls = self.get_calls()
        indices_found: Dict[str, int] = {}  # Track first occurrence index

        for i, call in enumerate(all_calls):
            if call.method_name in method_names and call.method_name not in indices_found:
                indices_found[call.method_name] = i

        # Now verify the order based on the first occurrence indices
        current_order_index = -1
        for method_name in method_names:
            found_index = indices_found.get(method_name)
            # We already checked all methods were called, so found_index should not be None
            if found_index is None:
                # Should not happen based on initial check, but defensive coding
                raise AssertionError(f"Internal error: Method {method_name} index not found despite being called.")
            if found_index <= current_order_index:
                raise AssertionError(
                    f"Method {method_name} (at index {found_index}) was called out of the expected order "
                    f"(previous method index: {current_order_index})"
                )
            current_order_index = found_index

    def assert_no_errors(self: Any) -> None:
        # Use the public get_calls()
        for call in self.get_calls():
            if call.exception is not None:
                raise AssertionError(f"Method {call.method_name} raised an exception: {call.exception}")

    # --- Assertions moved from verification_helpers ---

    def assert_no_unexpected_calls(self: EnhancedSpyBase, expected_methods: List[str]) -> None:
        unexpected_calls = []
        for call in self.get_calls():
            if call.method_name not in expected_methods:
                unexpected_calls.append(call.method_name)

        if unexpected_calls:
            unique_unexpected = sorted(list(set(unexpected_calls)))
            raise AssertionError(f"Unexpected method calls detected: {', '.join(unique_unexpected)}")

    def assert_call_max_duration(self: EnhancedSpyBase, method_name: str, max_duration: float) -> None:
        self.assert_called(method_name)  # Ensure the method was called at least once

        slow_calls = []
        for call in self.get_calls(method_name):
            # Ensure duration is recorded and check against max_duration
            if call.duration is not None and call.duration > max_duration:
                slow_calls.append(f"{call.method_name} took {call.duration:.6f}s")

        if slow_calls:
            raise AssertionError(f"Method {method_name} exceeded max duration ({max_duration:.6f}s) in the following calls: {'; '.join(slow_calls)}")

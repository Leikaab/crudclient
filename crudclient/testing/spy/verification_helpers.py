from typing import Any, Dict, List

from .enhanced import EnhancedSpyBase

# Helper functions for common verification patterns
# Helper functions for common verification patterns


def verify_call_sequence(spy: EnhancedSpyBase, *method_names: str) -> None:
    spy.assert_call_order(*method_names)


def verify_no_unexpected_calls(spy: EnhancedSpyBase, expected_methods: List[str]) -> None:
    for call in spy.get_calls():
        if call.method_name not in expected_methods:
            raise AssertionError(f"Unexpected method call: {call.method_name}")


def verify_call_timing(spy: EnhancedSpyBase, method_name: str, max_duration: float) -> None:
    spy.assert_called(method_name)

    for call in spy.get_calls(method_name):
        if call.duration is not None and call.duration > max_duration:
            raise AssertionError(f"Method {method_name} took {call.duration:.6f}s, " f"which is longer than the maximum allowed {max_duration:.6f}s")


def verify_call_arguments(spy: EnhancedSpyBase, method_name: str, expected_args: Dict[str, Any]) -> None:
    spy.assert_called(method_name)

    for call in spy.get_calls(method_name):
        # Check if all expected args are present with the correct values
        all_args_match = True

        for arg_name, arg_value in expected_args.items():
            if arg_name in call.kwargs:
                if call.kwargs[arg_name] != arg_value:
                    all_args_match = False
                    break
            else:
                # Check if it's a positional arg
                try:
                    # Attempt to map positional arg name like "arg0", "arg1" to index
                    arg_index = int(arg_name.replace("arg", ""))
                    if arg_index >= len(call.args) or call.args[arg_index] != arg_value:
                        all_args_match = False
                        break
                except (ValueError, IndexError):
                    # If name isn't like "argN" or index is out of bounds
                    all_args_match = False
                    break

        if all_args_match:
            return

    raise AssertionError(f"Method {method_name} was not called with the expected arguments: {expected_args}")

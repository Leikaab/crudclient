from typing import Any, Dict, List

from .enhanced import EnhancedSpyBase

def verify_call_sequence(spy: EnhancedSpyBase, *method_names: str) -> None:
    """
    Verifies that the specified methods were called on the spy in the exact order given.

    Args:
        spy: The EnhancedSpyBase instance to check.
        *method_names: A sequence of method names representing the expected call order.

    Raises:
        AssertionError: If any of the methods were not called or if they were
                      called in a different order.
    """
    ...

def verify_no_unexpected_calls(spy: EnhancedSpyBase, expected_methods: List[str]) -> None:
    """
    Verifies that only the specified methods were called on the spy.

    Args:
        spy: The EnhancedSpyBase instance to check.
        expected_methods: A list of method names that are expected to have been called.

    Raises:
        AssertionError: If any method not in `expected_methods` was called.
    """
    ...

def verify_call_timing(spy: EnhancedSpyBase, method_name: str, max_duration: float) -> None:
    """
    Verifies that a specific method was called and that all its calls completed
    within a maximum duration.

    Args:
        spy: The EnhancedSpyBase instance to check.
        method_name: The name of the method to check.
        max_duration: The maximum allowed duration in seconds for any single call
                      to the method.

    Raises:
        AssertionError: If the method was not called, or if any call exceeded
                      the `max_duration`.
    """
    ...

def verify_call_arguments(spy: EnhancedSpyBase, method_name: str, expected_args: Dict[str, Any]) -> None:
    """
    Verifies that a specific method was called with arguments matching the expected
    dictionary.

    Positional arguments in the actual call are matched against keys like 'arg0',
    'arg1', etc., in the `expected_args` dictionary. Keyword arguments are matched
    by their names.

    Args:
        spy: The EnhancedSpyBase instance to check.
        method_name: The name of the method to check.
        expected_args: A dictionary where keys are argument names (or 'argN' for
                       positional) and values are the expected argument values.

    Raises:
        AssertionError: If the method was not called, or if no call was found
                      that matched all `expected_args`.
    """
    ...

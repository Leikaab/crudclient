"""
Standalone helper functions for verifying interactions with `EnhancedSpyBase` spies.

These functions provide specific verification patterns tailored for spies that
conform to the `EnhancedSpyBase` interface (which includes detailed call recording
like timestamps and potentially results/exceptions). They offer a functional
approach to common assertions beyond the basic call checks provided by the
general `Verifier` class.

These helpers typically raise `AssertionError` upon failure, making them suitable
for direct use in test cases (e.g., with `pytest`).
"""

from typing import Any, Dict, List

from .enhanced import EnhancedSpyBase

def verify_call_sequence(spy: EnhancedSpyBase, *method_names: str) -> None:
    """
    Verifies methods were called in the exact sequence specified.

    Checks the recorded call history of the `spy` to ensure that the methods
    listed in `method_names` were called consecutively in that precise order.
    It does *not* allow other calls between the specified sequence.

    Args:
        spy: The `EnhancedSpyBase` instance to check.
        *method_names: A sequence of method name strings representing the expected call order.

    Raises:
        AssertionError: If the methods were not called, not called in the specified
                        order, or if other methods were called between them.

    Example:
        >>> spy = EnhancedSpyBase() # Assuming appropriate setup/mocking
        >>> spy.method_a()
        >>> spy.method_b()
        >>> spy.method_c()
        >>> verify_call_sequence(spy, "method_a", "method_b") # Checks first two calls
        >>> verify_call_sequence(spy, "method_a", "method_b", "method_c") # Checks all calls
        >>> # This would raise AssertionError: verify_call_sequence(spy, "method_a", "method_c")
        >>> # This would raise AssertionError: spy.other_method(); verify_call_sequence(spy, "method_a", "method_b")
    """
    ...

def verify_no_unexpected_calls(spy: EnhancedSpyBase, expected_methods: List[str]) -> None:
    """
    Verifies that *only* the specified methods were called on the spy, any number of times.

    Checks the entire call history and raises an error if any method *not* present
    in the `expected_methods` list was invoked.

    Args:
        spy: The `EnhancedSpyBase` instance to check.
        expected_methods: A list of method name strings that are allowed to have been called.

    Raises:
        AssertionError: If any method call is found whose name is not in `expected_methods`.

    Example:
        >>> spy = EnhancedSpyBase()
        >>> spy.allowed_method_1()
        >>> spy.allowed_method_2()
        >>> spy.allowed_method_1()
        >>> verify_no_unexpected_calls(spy, ["allowed_method_1", "allowed_method_2"])
        >>> # This would raise AssertionError: spy.unexpected_method(); verify_no_unexpected_calls(spy, ["allowed_method_1", "allowed_method_2"])
    """
    ...

def verify_call_timing(spy: EnhancedSpyBase, method_name: str, max_duration: float) -> None:
    """
    Verifies all calls to a method completed within a maximum duration.

    Checks the recorded start and end times for every call to `method_name` on the `spy`.

    Args:
        spy: The `EnhancedSpyBase` instance (must record call durations).
        method_name: The name of the method whose call durations to check.
        max_duration: The maximum allowed duration in seconds for any single call.

    Raises:
        AssertionError: If the method was never called, or if the duration of *any*
                        call to `method_name` exceeded `max_duration`.

    Example:
        >>> spy = EnhancedSpyBase() # Assumes spy records call timing
        >>> # Simulate calls (implementation detail depends on spy)
        >>> spy.perform_task() # Took 0.1s
        >>> spy.perform_task() # Took 0.2s
        >>> verify_call_timing(spy, "perform_task", 0.25) # All calls <= 0.25s
        >>> # This would raise AssertionError: verify_call_timing(spy, "perform_task", 0.15)
        >>> # This would raise AssertionError: verify_call_timing(spy, "non_existent_method", 1.0)
    """
    ...

def verify_call_arguments(spy: EnhancedSpyBase, method_name: str, expected_args: Dict[str, Any]) -> None:
    """
    Verifies at least one call to `method_name` matches a subset of arguments.

    Checks the call history for `method_name`. For each call, it compares the
    actual arguments against the `expected_args` dictionary. A call matches if
    *all* key-value pairs in `expected_args` are present and equal in the actual call's
    arguments (including positional args mapped to 'argN'). The actual call may
    have *additional* arguments not listed in `expected_args`.

    Args:
        spy: The `EnhancedSpyBase` instance to check.
        method_name: The name of the method to check.
        expected_args: A dictionary representing the subset of arguments to match.
                       Keys are argument names for keyword args, or 'arg0', 'arg1', ...
                       for positional args. Values are the expected values.

    Raises:
        AssertionError: If `method_name` was never called, or if *no call* was found
                        where all items in `expected_args` matched the actual arguments.

    Example:
        >>> spy = EnhancedSpyBase()
        >>> spy.configure(host="localhost", port=8080, timeout=10)
        >>> spy.configure(host="remote", port=9000, retries=3)

        >>> # Check if port 8080 was used in any call
        >>> verify_call_arguments(spy, "configure", {"port": 8080})

        >>> # Check if host "remote" and retries 3 were used together in any call
        >>> verify_call_arguments(spy, "configure", {"host": "remote", "retries": 3})

        >>> # Check positional argument (assuming 'configure' took host as first arg)
        >>> verify_call_arguments(spy, "configure", {"arg0": "localhost"})

        >>> # This would fail (no call had host="localhost" AND retries=3)
        >>> # verify_call_arguments(spy, "configure", {"host": "localhost", "retries": 3})

        >>> # This would fail (no call had port=1234)
        >>> # verify_call_arguments(spy, "configure", {"port": 1234})
    """
    ...

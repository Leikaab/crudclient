"""
Helper functions for unit tests.

This module contains utility functions that are used across multiple test modules.
"""

from unittest.mock import MagicMock

from crudclient.testing.spy.method_call import MethodCall


def translate_mock_calls_for_verifier(mock_target: MagicMock) -> None:
    """
    Translate unittest.mock.MagicMock calls to the format expected by Verifier.

    This helper function reads the mock_calls attribute of a MagicMock instance,
    converts each call to a MethodCall object, and assigns the resulting list
    to the mock's calls attribute, making it compatible with the Verifier class.

    Args:
        mock_target: The MagicMock instance to adapt for use with Verifier
    """
    translated_calls = []

    for call_obj in mock_target.mock_calls:
        # Extract method name, args, and kwargs from the mock call
        method_name = call_obj[0]
        args = call_obj[1]
        kwargs = call_obj[2]

        # Create a MethodCall object and append it to the list
        method_call = MethodCall(
            method_name=method_name,
            args=args,
            kwargs=kwargs
        )
        translated_calls.append(method_call)

    # Assign the translated calls to the mock's calls attribute
    mock_target.calls = translated_calls

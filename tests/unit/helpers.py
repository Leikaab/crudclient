"""
Helper functions for unit tests.

This module contains utility functions that are used across multiple test modules.
"""

from typing import Any, List
from unittest.mock import MagicMock

from crudclient.testing.spy.method_call import MethodCall


class VerifiableMock(MagicMock):
    """
    A MagicMock subclass that provides a `.calls` attribute for use with Verifier.

    This class maintains a `.calls` attribute that can be populated with MethodCall objects
    by calling `translate_mock_calls_for_verifier` before verification.

    Example:
        >>> mock = VerifiableMock()
        >>> mock.some_method(1, 2, key="value")
        >>> mock.another_method()
        >>> mock()  # Direct call to the mock
        >>> translate_mock_calls_for_verifier(mock)  # Populate .calls attribute
        >>> assert len(mock.calls) == 3
        >>> assert mock.calls[0].method_name == "some_method"
        >>> assert mock.calls[0].args == (1, 2)
        >>> assert mock.calls[0].kwargs == {"key": "value"}
        >>> assert mock.calls[1].method_name == "another_method"
        >>> assert mock.calls[2].method_name == ""  # Direct calls use empty string
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the VerifiableMock with an empty calls list.

        Args:
            *args: Arguments to pass to the parent MagicMock constructor
            **kwargs: Keyword arguments to pass to the parent MagicMock constructor
        """
        super().__init__(*args, **kwargs)
        self.calls: List[MethodCall] = []


def translate_mock_calls_for_verifier(mock_target: MagicMock) -> None:
    """
    Translate unittest.mock.MagicMock calls to the format expected by Verifier.

    This helper function reads the mock_calls attribute of a MagicMock instance,
    converts each call to a MethodCall object, and assigns the resulting list
    to the mock's calls attribute, making it compatible with the Verifier class.

    Note:
        Consider using VerifiableMock instead, which automatically maintains the
        calls list in the format expected by Verifier.

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

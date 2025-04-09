"""
Custom exceptions for CRUD mock operations.

This module defines exceptions that can be raised by the CRUD mock classes
during testing to simulate various error conditions.
"""

from crudclient.exceptions import CrudClientError


class ConcurrencyError(CrudClientError):
    """
    Exception raised when a concurrency conflict occurs.

    This exception is used to simulate scenarios where multiple clients attempt
    to update the same resource simultaneously, resulting in a conflict.
    """
    pass


class ValidationFailedError(CrudClientError):
    """
    Exception raised when validation fails.

    This exception is used to simulate scenarios where data validation fails
    during create or update operations, such as when required fields are missing
    or field values don't meet validation criteria.
    """
    pass

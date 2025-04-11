"""
Exception classes for CRUD mock operations.

This module defines custom exceptions that can be raised during CRUD mock operations
to simulate specific error conditions.
"""

from crudclient.exceptions import CrudClientError

class ConcurrencyError(CrudClientError):
    """
    Exception raised when a concurrency conflict is detected.

    This exception is used to simulate scenarios where multiple clients
    attempt to modify the same resource simultaneously, resulting in
    a conflict that prevents the operation from completing.
    """

    ...

class ValidationFailedError(CrudClientError):
    """
    Exception raised when data validation fails.

    This exception is used to simulate scenarios where the data provided
    for a create or update operation fails validation checks, preventing
    the operation from completing.
    """

    ...

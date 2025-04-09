"""
Exceptions for the crudclient testing framework.

This module defines exceptions that can be raised by the testing framework.
"""


class TestingError(Exception):
    """Base class for all testing framework exceptions."""
    pass


class MockConfigurationError(TestingError):
    """Raised when there is an error in the mock configuration."""
    pass


class VerificationError(TestingError):
    """Raised when a verification fails."""
    pass


class RequestNotConfiguredError(MockConfigurationError):
    """Raised when a request is made that has not been configured."""
    pass


class AuthStrategyError(TestingError):
    """Raised when there is an error with an auth strategy."""
    pass


class CRUDOperationError(TestingError):
    """Raised when there is an error with a CRUD operation."""
    pass


class DataStoreError(TestingError):
    """Raised when there is an error with the data store."""
    pass


class ResourceNotFoundError(DataStoreError):
    """Raised when a resource is not found in the data store."""
    pass


class SpyError(TestingError):
    """Raised when there is an error with a spy."""
    pass

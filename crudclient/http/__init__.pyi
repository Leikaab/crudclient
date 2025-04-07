"""
HTTP Module for CrudClient
=========================

This package contains modules for handling HTTP operations in the CrudClient library.
It provides a modular architecture with clear separation of concerns for HTTP operations.

Modules:
    - client: Core HTTP client functionality
    - session: Session management
    - request: Request preparation and formatting
    - response: Response handling and parsing
    - retry: Retry policies and backoff strategies
    - errors: Error handling
"""
from .client import HttpClient
from .session import SessionManager
from .request import RequestFormatter
from .response import ResponseHandler
from .errors import ErrorHandler
from .retry import RetryHandler, RetryStrategy, FixedRetryStrategy, ExponentialBackoffStrategy, RetryCondition, RetryEvent

__all__ = [
    "HttpClient",
    "SessionManager",
    "RequestFormatter",
    "ResponseHandler",
    "ErrorHandler",
    "RetryHandler",
    "RetryStrategy",
    "FixedRetryStrategy",
    "ExponentialBackoffStrategy",
    "RetryCondition",
    "RetryEvent"
]

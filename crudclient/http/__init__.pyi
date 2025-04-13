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
from .errors import ErrorHandler
from .request import RequestFormatter
from .response import ResponseHandler
from .retry import RetryHandler
from .retry_conditions import RetryCondition as RetryCondition, RetryEvent as RetryEvent
from .retry_strategies import (
    RetryStrategy as RetryStrategy,
    FixedRetryStrategy as FixedRetryStrategy,
    ExponentialBackoffStrategy as ExponentialBackoffStrategy,
)
from .session import SessionManager

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
    "RetryEvent",
]

"""
Common utilities for authentication example tests.

This package provides a backward-compatible mock client, a factory function
to create it, and a mock MFA authentication strategy.
"""

from .client import BackwardCompatibleMockClient
from .factory import create_mock_client
from .mfa_auth import MockMFAAuth

__all__ = [
    "BackwardCompatibleMockClient",
    "create_mock_client",
    "MockMFAAuth",
]

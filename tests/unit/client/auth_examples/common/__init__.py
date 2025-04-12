"""
Common utilities for authentication example tests.

This package provides a factory function to create mock clients
and a mock MFA authentication strategy.
"""

from .factory import create_mock_client
from .mfa_auth import MockMFAAuth

__all__ = [
    "create_mock_client",
    "MockMFAAuth",
]

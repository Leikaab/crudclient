"""
Common imports and utilities for authentication examples.

This module now re-exports components from the 'common' subpackage.
"""

# Re-export create_mock_client for backward compatibility
from .common.factory import create_mock_client

# Optionally re-export others if needed elsewhere, but keep it minimal
# from .common.mfa_auth import MockMFAAuth

__all__ = [
    "create_mock_client",
    # "MockMFAAuth",
]

"""
Custom authentication mock for testing.

This module provides mocks for Custom Authentication strategies with support
for OAuth grant types, scopes, and advanced authentication scenarios.
"""

from .oauth_mock import OAuthMock
from .custom_auth_mock import CustomAuthMock

__all__ = ['OAuthMock', 'CustomAuthMock']

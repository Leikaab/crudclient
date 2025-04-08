"""
Enhanced mock Client implementation for testing.

This module provides a sophisticated mock Client implementation with configurable behavior,
support for complex response scenarios, and helpers for verifying client usage patterns.
"""

from .response import MockResponse
from .patterns import ResponsePattern
from .http_client import MockHttpClient
from .network import NetworkCondition
from .pagination import PaginationHelper
from .rate_limit import RateLimitHelper
from .partial_response import PartialResponseHelper
from .client import MockClient
from .factory import create_mock_client, create_simple_mock_client
from .simple_mock import SimpleMockClient
from .api_patterns import APIPatternBuilder
from .response_builder import ResponseBuilder
from .verification import RequestVerifier, ResponseVerifier

__all__ = [
    # Core mock components
    'MockResponse',
    'MockHttpClient',
    'ResponsePattern',
    'NetworkCondition',
    'PaginationHelper',
    'RateLimitHelper',
    'PartialResponseHelper',
    'MockClient',
    'SimpleMockClient',

    # Factory functions
    'create_mock_client',
    'create_simple_mock_client',

    # API pattern builders
    'APIPatternBuilder',

    # Response builders
    'ResponseBuilder',

    # Verification helpers
    'RequestVerifier',
    'ResponseVerifier',
]

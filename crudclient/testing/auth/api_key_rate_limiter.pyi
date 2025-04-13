"""
API Key rate limiting utilities for testing.

This module provides a class for rate limiting API key usage with configurable
limits and periods.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ApiKeyRateLimiter:
    """
    API Key rate limiter with configurable limits and periods.

    This class provides methods for tracking API key usage and enforcing
    rate limits with configurable requests per period.
    """

    rate_limit_enabled: bool
    rate_limit_requests: int
    rate_limit_period: int
    request_history: Dict[str, List[datetime]]

    def __init__(self) -> None:
        """
        Initialize an API Key rate limiter.
        """
        ...

    def enable_rate_limiting(self, requests_per_period: int = 100, period_seconds: int = 3600) -> None:
        """
        Enable rate limiting for API keys.

        Args:
            requests_per_period: Number of requests allowed per period
            period_seconds: Period length in seconds
        """
        ...

    def initialize_key(self, api_key: str) -> None:
        """
        Initialize rate limiting for a specific API key.

        Args:
            api_key: The API key to initialize
        """
        ...

    def track_request(self, api_key: str) -> bool:
        """
        Track a request for rate limiting purposes.

        Args:
            api_key: The API key used for the request

        Returns:
            True if the request is within rate limits, False otherwise
        """
        ...

    def get_rate_limit_status(self, api_key: str) -> Dict:
        """
        Get rate limit status for a specific API key.

        Args:
            api_key: The API key to get status for

        Returns:
            Dictionary with rate limit status
        """
        ...

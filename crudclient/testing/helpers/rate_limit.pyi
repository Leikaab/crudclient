"""
Rate limiting helper for the crudclient testing framework.

This module provides utilities for simulating rate limiting behavior in API responses,
supporting various rate limiting strategies including standard limits, burst limits,
and tiered limits. It generates appropriate rate limit headers and can be configured
to simulate different rate limiting scenarios for testing client behavior under
rate-limited conditions.
"""

import time
from typing import Any, Dict, List, Optional, Tuple

def get_current_time() -> float:
    """
    Get current time in seconds.

    This function provides a consistent way to get the current time,
    making it easier to mock for testing purposes.

    Returns:
        Current time in seconds since the epoch
    """
    ...

class RateLimitHelper:
    """
    Helper for simulating rate limiting behavior in tests.

    This class provides a flexible way to simulate API rate limiting with
    configurable limits, time windows, and header names. It supports standard
    rate limiting, burst limits for short time periods, and tiered rate limiting
    for different API access levels.

    The helper tracks request timestamps and can determine whether a request
    should be allowed or rejected based on configured limits. It also generates
    appropriate rate limit headers that would typically be returned by a
    rate-limited API, allowing tests to verify client behavior when encountering
    rate limits.
    """

    limit: int
    window_seconds: int
    remaining_header: str
    limit_header: str
    reset_header: str
    retry_after_header: str
    burst_limit: Optional[int]
    burst_window_seconds: int
    tiered_limits: Optional[List[Dict[str, Any]]]
    tier_header: Optional[str]
    requests: List[float]
    burst_requests: List[float]
    tiered_requests: Dict[str, List[float]]
    _last_reset: float
    _current_tier: Optional[str]

    def __init__(
        self,
        limit: int = 60,
        window_seconds: int = 60,
        remaining_header: str = "X-RateLimit-Remaining",
        limit_header: str = "X-RateLimit-Limit",
        reset_header: str = "X-RateLimit-Reset",
        retry_after_header: str = "Retry-After",
        burst_limit: Optional[int] = None,
        burst_window_seconds: Optional[int] = None,
        tiered_limits: Optional[List[Dict[str, Any]]] = None,
        tier_header: Optional[str] = None,
    ) -> None:
        """
        Initialize rate limit helper with configuration options.

        This constructor sets up the rate limit helper with configuration for
        standard rate limits, burst limits, and tiered limits. It supports
        customization of header names to match different API implementations.

        Args:
            limit: Maximum number of requests allowed in the standard window
            window_seconds: Time window in seconds for the standard rate limit
            remaining_header: Header name for remaining requests count
            limit_header: Header name for the rate limit value
            reset_header: Header name for the rate limit reset timestamp
            retry_after_header: Header name for retry after seconds value
            burst_limit: Optional burst limit for short time periods
                (useful for simulating APIs that have both long-term and
                short-term rate limits)
            burst_window_seconds: Window for burst limit in seconds
                (defaults to window_seconds / 10 if not provided)
            tiered_limits: Optional list of tier configurations with 'name',
                'limit', and 'window' keys for simulating different rate limits
                for different API access tiers
            tier_header: Header name for tier information in responses
        """
        ...

    def check_rate_limit(self, tier: Optional[str] = None) -> Tuple[bool, Dict[str, str]]:
        """
        Check if the rate limit has been exceeded and generate appropriate headers.

        This method determines whether a request should be allowed based on the
        configured rate limits and the history of previous requests. It also
        generates appropriate rate limit headers that would be returned by a
        rate-limited API, including information about remaining requests,
        limit values, and reset times.

        Args:
            tier: Optional tier name to check against tiered limits
                (if tiered limits are configured)

        Returns:
            Tuple containing:
                - Boolean indicating whether the request is allowed (True) or
                  should be rate limited (False)
                - Dictionary of rate limit headers that would be included in
                  the API response
        """
        ...

    def set_tier(self, tier: str) -> None:
        """
        Set the current tier for rate limiting.

        This method sets the current tier to use for rate limiting checks,
        allowing tests to simulate different API access tiers with different
        rate limits.

        Args:
            tier: Tier name to use for rate limiting
                (must match a tier name in the configured tiered_limits)

        Raises:
            ValueError: If the specified tier is not found in the configured
                tiered limits
        """
        ...

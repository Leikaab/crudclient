"""
Rate limiting helper for the crudclient testing framework.

This module provides utilities for simulating rate limiting behavior in API responses,
supporting various rate limiting strategies including standard limits, burst limits,
and tiered limits. It generates appropriate rate limit headers and can be configured
to simulate different rate limiting scenarios for testing client behavior under
rate-limited conditions.
"""

import time
from typing import Dict, List, Optional, Tuple, Union, Any, cast


def get_current_time() -> float:
    """
    Get current time in seconds.

    This function provides a consistent way to get the current time,
    making it easier to mock for testing purposes.

    Returns:
        Current time in seconds since the epoch
    """
    return time.time()


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
    ):
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
        self.limit = limit
        self.window_seconds = window_seconds
        self.remaining_header = remaining_header
        self.limit_header = limit_header
        self.reset_header = reset_header
        self.retry_after_header = retry_after_header
        self.burst_limit = burst_limit
        self.burst_window_seconds = burst_window_seconds or (window_seconds // 10)
        self.tiered_limits = tiered_limits
        self.tier_header = tier_header

        # Request tracking
        self.requests: List[float] = []
        self.burst_requests: List[float] = []
        self.tiered_requests: Dict[str, List[float]] = {}
        if tiered_limits:
            for tier in tiered_limits:
                tier_name = str(tier['name'])
                self.tiered_requests[tier_name] = []

        self._last_reset = get_current_time()
        self._current_tier: Optional[str] = None

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
        now = get_current_time()

        # Set current tier if provided
        if tier and self.tiered_limits:
            self._current_tier = tier

        # Remove requests outside the current window
        self.requests = [t for t in self.requests if now - t < self.window_seconds]

        # Check burst limit if configured
        burst_limited = False
        if self.burst_limit is not None:
            self.burst_requests = [t for t in self.burst_requests if now - t < self.burst_window_seconds]
            if len(self.burst_requests) >= self.burst_limit:
                burst_limited = True

        # Check tiered limits if configured
        tier_limited = False
        tier_limit = self.limit
        tier_window = self.window_seconds
        tier_name: Optional[str] = None

        if self.tiered_limits and self._current_tier:
            for tier_config in self.tiered_limits:
                if str(tier_config['name']) == self._current_tier:
                    tier_name = str(tier_config['name'])
                    tier_limit = int(tier_config['limit'])
                    tier_window = int(tier_config.get('window', self.window_seconds))

                    # Initialize tier requests list if not exists
                    if tier_name not in self.tiered_requests:
                        self.tiered_requests[tier_name] = []

                    # Remove old requests
                    self.tiered_requests[tier_name] = [
                        t for t in self.tiered_requests[tier_name]
                        if now - t < tier_window
                    ]

                    # Check if tier limit exceeded
                    if len(self.tiered_requests[tier_name]) >= tier_limit:
                        tier_limited = True
                    break

        # Check if we've hit any limit
        is_allowed = (
            len(self.requests) < self.limit
            and not burst_limited
            and not tier_limited
        )

        # If allowed, record this request
        if is_allowed:
            self.requests.append(now)
            if self.burst_limit is not None:
                self.burst_requests.append(now)
            if tier_name and tier_name in self.tiered_requests:
                self.tiered_requests[tier_name].append(now)

        # Calculate reset time
        if self.requests:
            oldest_request = min(self.requests)
            reset_time = int(oldest_request + self.window_seconds)
        else:
            reset_time = int(now + self.window_seconds)

        # Calculate burst reset time if applicable
        burst_reset_time = None
        if burst_limited and self.burst_requests:
            oldest_burst = min(self.burst_requests)
            burst_reset_time = int(oldest_burst + self.burst_window_seconds)

        # Calculate tier reset time if applicable
        tier_reset_time = None
        if tier_limited and tier_name and tier_name in self.tiered_requests and self.tiered_requests[tier_name]:
            oldest_tier = min(self.tiered_requests[tier_name])
            tier_reset_time = int(oldest_tier + tier_window)

        # Use the earliest reset time
        effective_reset_time = reset_time
        if burst_reset_time and burst_reset_time < effective_reset_time:
            effective_reset_time = burst_reset_time
        if tier_reset_time and tier_reset_time < effective_reset_time:
            effective_reset_time = tier_reset_time

        # Generate headers
        headers = {
            self.remaining_header: str(max(0, self.limit - len(self.requests))),
            self.limit_header: str(self.limit),
            self.reset_header: str(effective_reset_time)
        }

        # Add retry-after header if rate limited
        if not is_allowed:
            retry_after = effective_reset_time - int(now)
            headers[self.retry_after_header] = str(max(1, retry_after))

        # Add tier information if applicable
        if self.tier_header and tier_name:
            headers[self.tier_header] = tier_name

        # Add burst limit information if configured
        if self.burst_limit is not None:
            headers["X-Burst-Limit"] = str(self.burst_limit)
            headers["X-Burst-Remaining"] = str(max(0, self.burst_limit - len(self.burst_requests)))
            if burst_reset_time:
                headers["X-Burst-Reset"] = str(burst_reset_time)

        # Add tier limit information if applicable
        if tier_name:
            headers["X-Tier-Limit"] = str(tier_limit)
            remaining = 0
            if tier_name in self.tiered_requests:
                remaining = max(0, tier_limit - len(self.tiered_requests[tier_name]))
            headers["X-Tier-Remaining"] = str(remaining)
            if tier_reset_time:
                headers["X-Tier-Reset"] = str(tier_reset_time)

        return is_allowed, headers

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
        if self.tiered_limits:
            for tier_config in self.tiered_limits:
                if str(tier_config['name']) == tier:
                    self._current_tier = tier
                    return
        raise ValueError(f"Tier '{tier}' not found in configured tiered limits")

"""
Rate limiting helper for mock client.
"""

import time
from typing import Dict, List, Tuple


def get_current_time() -> float:
    """Get current time in seconds."""
    return time.time()


class RateLimitHelper:
    """Helper for simulating rate limiting behavior."""

    def __init__(
        self,
        limit: int = 60,
        window_seconds: int = 60,
        remaining_header: str = "X-RateLimit-Remaining",
        limit_header: str = "X-RateLimit-Limit",
        reset_header: str = "X-RateLimit-Reset",
    ):
        """
        Initialize rate limit helper.

        Args:
            limit: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds
            remaining_header: Header name for remaining requests
            limit_header: Header name for rate limit
            reset_header: Header name for reset time
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.remaining_header = remaining_header
        self.limit_header = limit_header
        self.reset_header = reset_header
        self.requests: List[float] = []
        self._last_reset = get_current_time()

    def check_rate_limit(self) -> Tuple[bool, Dict[str, str]]:
        """
        Check if the rate limit has been exceeded.

        Returns:
            Tuple[bool, Dict[str, str]]: (is_allowed, headers)
        """
        now = get_current_time()

        # Remove requests outside the current window
        self.requests = [t for t in self.requests if now - t < self.window_seconds]

        # Check if we've hit the limit
        is_allowed = len(self.requests) < self.limit

        # If allowed, record this request
        if is_allowed:
            self.requests.append(now)

        # Calculate reset time
        if self.requests:
            oldest_request = min(self.requests)
            reset_time = int(oldest_request + self.window_seconds)
        else:
            reset_time = int(now + self.window_seconds)

        # Generate headers
        headers = {
            self.remaining_header: str(max(0, self.limit - len(self.requests))),
            self.limit_header: str(self.limit),
            self.reset_header: str(reset_time)
        }

        return is_allowed, headers

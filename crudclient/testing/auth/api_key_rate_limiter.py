from datetime import datetime, timedelta
from typing import Dict, List


class ApiKeyRateLimiter:
    def __init__(self):
        self.rate_limit_enabled = False
        self.rate_limit_requests = 100
        self.rate_limit_period = 3600  # seconds (1 hour)
        self.request_history: Dict[str, List[datetime]] = {}

    def enable_rate_limiting(self, requests_per_period: int = 100, period_seconds: int = 3600) -> None:
        self.rate_limit_enabled = True
        self.rate_limit_requests = requests_per_period
        self.rate_limit_period = period_seconds

    def initialize_key(self, api_key: str) -> None:
        if api_key not in self.request_history:
            self.request_history[api_key] = []

    def track_request(self, api_key: str) -> bool:
        # Record request time for rate limiting
        now = datetime.now()
        if api_key not in self.request_history:
            self.request_history[api_key] = []
        self.request_history[api_key].append(now)

        # Check rate limit if enabled
        if self.rate_limit_enabled:
            # Clean up old requests outside the current period
            period_start = now - timedelta(seconds=self.rate_limit_period)
            self.request_history[api_key] = [t for t in self.request_history[api_key] if t >= period_start]

            # Check if rate limit exceeded
            return len(self.request_history[api_key]) <= self.rate_limit_requests

        return True  # No rate limiting or limit not exceeded

    def get_rate_limit_status(self, api_key: str) -> Dict:
        if not self.rate_limit_enabled:
            return {"enabled": False}

        if api_key not in self.request_history:
            return {
                "enabled": True,
                "limit": self.rate_limit_requests,
                "remaining": self.rate_limit_requests,
                "reset": datetime.now() + timedelta(seconds=self.rate_limit_period),
            }

        # Clean up old requests
        now = datetime.now()
        period_start = now - timedelta(seconds=self.rate_limit_period)
        self.request_history[api_key] = [t for t in self.request_history[api_key] if t >= period_start]

        # Calculate remaining requests
        used = len(self.request_history[api_key])
        remaining = max(0, self.rate_limit_requests - used)

        # Calculate reset time (when the oldest request will expire)
        if used > 0:
            oldest = min(self.request_history[api_key])
            reset = oldest + timedelta(seconds=self.rate_limit_period)
        else:
            reset = now + timedelta(seconds=self.rate_limit_period)

        return {"enabled": True, "limit": self.rate_limit_requests, "remaining": remaining, "reset": reset, "used": used}

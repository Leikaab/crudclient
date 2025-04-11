from typing import Dict, Optional


class ApiKeyUsageTracker:
    def __init__(self):
        self.usage_tracking_enabled = False
        self.usage_by_endpoint: Dict[str, int] = {}
        self.usage_by_key: Dict[str, int] = {}

    def enable_usage_tracking(self) -> None:
        self.usage_tracking_enabled = True

    def initialize_key(self, api_key: str) -> None:
        if api_key not in self.usage_by_key:
            self.usage_by_key[api_key] = 0

    def track_request(self, api_key: str, endpoint: Optional[str] = None) -> None:
        if not self.usage_tracking_enabled:
            return

        if api_key not in self.usage_by_key:
            self.usage_by_key[api_key] = 0
        self.usage_by_key[api_key] += 1

        if endpoint:
            if endpoint not in self.usage_by_endpoint:
                self.usage_by_endpoint[endpoint] = 0
            self.usage_by_endpoint[endpoint] += 1

    def get_usage_stats(self) -> Dict:
        return {"by_key": self.usage_by_key, "by_endpoint": self.usage_by_endpoint, "total_requests": sum(self.usage_by_key.values())}

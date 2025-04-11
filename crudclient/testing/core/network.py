import random
import time
from typing import Callable, Optional

import requests


class NetworkCondition:

    def __init__(
        self,
        latency_ms: int = 0,
        packet_loss_percentage: float = 0.0,
        error_rate_percentage: float = 0.0,
        error_factory: Optional[Callable[[], Exception]] = None,
    ):
        self.latency_ms = latency_ms
        self.packet_loss_percentage = min(100.0, max(0.0, packet_loss_percentage))
        self.error_rate_percentage = min(100.0, max(0.0, error_rate_percentage))
        self.error_factory = error_factory or (lambda: requests.ConnectionError("Simulated network error"))

    def should_drop_packet(self) -> bool:
        return random.random() * 100 < self.packet_loss_percentage

    def should_raise_error(self) -> bool:
        return random.random() * 100 < self.error_rate_percentage

    def apply_latency(self) -> None:
        if self.latency_ms > 0:
            time.sleep(self.latency_ms / 1000.0)

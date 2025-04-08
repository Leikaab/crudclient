"""
Network condition simulation for mock client.
"""

import time
import random
from typing import Callable, Optional

import requests


class NetworkCondition:
    """Simulates various network conditions for testing."""

    def __init__(
        self,
        latency_ms: int = 0,
        packet_loss_percentage: float = 0.0,
        error_rate_percentage: float = 0.0,
        error_factory: Optional[Callable[[], Exception]] = None,
    ):
        """
        Initialize network condition simulator.

        Args:
            latency_ms: Simulated latency in milliseconds
            packet_loss_percentage: Percentage of requests that will be dropped (0-100)
            error_rate_percentage: Percentage of requests that will raise errors (0-100)
            error_factory: Function to create network errors
        """
        self.latency_ms = latency_ms
        self.packet_loss_percentage = min(100.0, max(0.0, packet_loss_percentage))
        self.error_rate_percentage = min(100.0, max(0.0, error_rate_percentage))
        self.error_factory = error_factory or (lambda: requests.ConnectionError("Simulated network error"))

    def should_drop_packet(self) -> bool:
        """
        Determine if a packet should be dropped based on the packet loss percentage.

        Returns:
            True if the packet should be dropped, False otherwise
        """
        return random.random() * 100 < self.packet_loss_percentage

    def should_raise_error(self) -> bool:
        """
        Determine if an error should be raised based on the error rate percentage.

        Returns:
            True if an error should be raised, False otherwise
        """
        return random.random() * 100 < self.error_rate_percentage

    def apply_latency(self) -> None:
        """Apply the configured latency by sleeping."""
        if self.latency_ms > 0:
            time.sleep(self.latency_ms / 1000.0)

import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid potential circular imports if strategies need complex types
    pass


class RetryStrategy(ABC):

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        pass


class FixedRetryStrategy(RetryStrategy):

    def __init__(self, delay: float = 1.0) -> None:
        if not isinstance(delay, (int, float)) or delay < 0:
            raise ValueError("delay must be a non-negative number")
        self.delay = delay

    def get_delay(self, attempt: int) -> float:
        if not isinstance(attempt, int):
            raise TypeError(f"attempt must be an integer, got {type(attempt).__name__}")
        if attempt < 1:
            raise ValueError(f"attempt must be a positive integer, got {attempt}")
        return self.delay


class ExponentialBackoffStrategy(RetryStrategy):

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        factor: float = 2.0,
        jitter: bool = True,
    ) -> None:
        if not isinstance(base_delay, (int, float)) or base_delay <= 0:
            raise ValueError("base_delay must be a positive number")
        if not isinstance(max_delay, (int, float)) or max_delay < base_delay:
            raise ValueError("max_delay must be non-negative and >= base_delay")
        if not isinstance(factor, (int, float)) or factor <= 1:
            raise ValueError("factor must be a number greater than 1")
        if not isinstance(jitter, bool):
            raise TypeError("jitter must be a boolean")

        self.base_delay = base_delay
        self.max_delay = max_delay
        self.factor = factor
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        if not isinstance(attempt, int):
            raise TypeError(f"attempt must be an integer, got {type(attempt).__name__}")
        if attempt < 1:
            raise ValueError(f"attempt must be a positive integer, got {attempt}")

        # Calculate exponential backoff
        delay = min(self.base_delay * (self.factor ** (attempt - 1)), self.max_delay)

        # Add jitter if enabled (up to 25% variation around the delay)
        if self.jitter:
            delay = delay * (0.75 + 0.5 * random.random())

        # Ensure delay doesn't exceed max_delay after jitter
        return min(delay, self.max_delay)

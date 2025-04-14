from abc import ABC, abstractmethod

class RetryStrategy(ABC):
    """Abstract base class for retry delay strategies."""

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """Calculate the delay before the next retry attempt.

        Args:
            attempt: The current retry attempt number (starting from 1).

        Returns:
            The calculated delay in seconds.

        Raises:
            TypeError: If attempt is not an integer.
            ValueError: If attempt is less than 1.
        """
        ...

class FixedRetryStrategy(RetryStrategy):
    """A retry strategy with a fixed delay between attempts."""

    delay: float

    def __init__(self, delay: float = 1.0) -> None:
        """Initializes the FixedRetryStrategy.

        Args:
            delay: The fixed delay in seconds between retries. Must be non-negative.

        Raises:
            ValueError: If delay is negative.
        """
        ...

    def get_delay(self, attempt: int) -> float:
        """Returns the fixed delay.

        Args:
            attempt: The current retry attempt number (starting from 1).

        Returns:
            The fixed delay in seconds.

        Raises:
            TypeError: If attempt is not an integer.
            ValueError: If attempt is less than 1.
        """
        ...

class ExponentialBackoffStrategy(RetryStrategy):
    """A retry strategy with exponentially increasing delay, optionally with jitter."""

    base_delay: float
    max_delay: float
    factor: float
    jitter: bool

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        factor: float = 2.0,
        jitter: bool = True,
    ) -> None:
        """Initializes the ExponentialBackoffStrategy.

        Args:
            base_delay: The initial delay in seconds. Must be positive.
            max_delay: The maximum delay in seconds. Must be non-negative and >= base_delay.
            factor: The multiplier for the delay. Must be greater than 1.
            jitter: Whether to add random jitter to the delay.

        Raises:
            ValueError: If base_delay, max_delay, or factor have invalid values.
            TypeError: If jitter is not a boolean.
        """
        ...

    def get_delay(self, attempt: int) -> float:
        """Calculates delay using exponential backoff with optional jitter.

        The delay is calculated as `min(base_delay * (factor ** (attempt - 1)), max_delay)`.
        If jitter is enabled, a random variation is added.

        Args:
            attempt: The current retry attempt number (starting from 1).

        Returns:
            The calculated delay in seconds, capped at max_delay.

        Raises:
            TypeError: If attempt is not an integer.
            ValueError: If attempt is less than 1.
        """
        ...

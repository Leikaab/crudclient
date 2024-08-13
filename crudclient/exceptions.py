from typing import Any


class APIError(Exception):
    """Base class for all API-related errors."""

    pass


class InvalidClientError(APIError):
    """Raised when an invalid client or client configuration is provided."""

    def __init__(self, client: Any, message: str = "client must be an instance of Client or None"):
        self.client = client
        self.message = message
        self.full_message = f"{message}, got {type(client).__name__} instead."
        super().__init__(self.full_message)

    def __str__(self):
        return f"InvalidClientError: {self.full_message}"

    def __repr__(self):
        return f"InvalidClientError(client={self.client!r}, message={self.message!r})"


class ClientInitializationError(APIError):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        original_exception = f"\nCaused by: {self.__cause__}" if self.__cause__ else ""
        return f"{super().__str__()}{original_exception}"

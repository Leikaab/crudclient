class APIError(Exception):
    """Base class for all API-related errors."""

    def __str__(self):
        original_exception = f"\nCaused by: {self.__cause__}" if self.__cause__ else ""
        exception_name = self.__class__.__name__
        return f"{exception_name}: {super().__str__()}{original_exception}"


class InvalidClientError(APIError):
    """Raised when an invalid client or client configuration is provided."""

    def __init__(self, message: str = "Invalid client provided"):
        self.message = message
        super().__init__(message)

    def __repr__(self):
        return f"InvalidClientError(message={self.message!r})"


class ClientInitializationError(APIError):

    pass

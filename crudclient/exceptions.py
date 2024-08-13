class APIError(Exception):
    """Base class for all API-related errors."""

    pass


class InvalidClientError(APIError):
    """Raised when an invalid client is provided."""

    pass


class InvalidClientConfigError(APIError):
    """Raised when an invalid client configuration is provided."""

    pass


class ClientInitializationError(APIError):
    """Raised when the client cannot be initialized."""

    pass

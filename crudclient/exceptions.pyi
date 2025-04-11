from typing import Any, Dict, Optional, Union

import requests

from .types import JSONDict

class APIError(Exception):
    """Base class for all API-related errors."""

    def __str__(self) -> str: ...

class CrudClientError(APIError):
    """
    Base class for all CrudClient-specific errors.

    This class extends APIError and adds a response attribute to store the original
    HTTP response that caused the error.

    Attributes:
        message (str): A descriptive error message.
        response (Optional[requests.Response]): The HTTP response that caused the error, if available.
    """

    message: str
    response: Optional[requests.Response]

    def __init__(self, message: str, response: Optional[requests.Response] = None) -> None: ...
    def __repr__(self) -> str: ...

class AuthenticationError(CrudClientError):
    """
    Raised when authentication fails.

    This error is typically raised when the API returns a 401 Unauthorized response,
    indicating that the provided credentials are invalid or missing.
    """

    pass

class NotFoundError(CrudClientError):
    """
    Raised when a resource is not found.

    This error is typically raised when the API returns a 404 Not Found response,
    indicating that the requested resource does not exist.
    """

    pass

class InvalidResponseError(CrudClientError):
    """
    Raised when the API response is invalid or unexpected.

    This error is raised when the response from the API cannot be parsed or
    does not match the expected format.
    """

    pass

class ModelConversionError(CrudClientError):
    """
    Raised when a model conversion fails.

    This error is raised when the library fails to convert the API response
    to the expected model type, typically due to missing or invalid fields.

    Attributes:
        message (str): A descriptive error message.
        response (Optional[requests.Response]): The HTTP response that caused the error, if available.
        data (Any): The data that failed to convert.
    """

    data: Any

    def __init__(self, message: str, response: Optional[requests.Response] = None, data: Any = None) -> None: ...
    def __repr__(self) -> str: ...

class ValidationError(CrudClientError):
    """
    Raised when data validation fails.

    This error is raised when the input data or response data fails validation,
    typically due to missing required fields, invalid field types, or constraint violations.

    Attributes:
        message (str): A descriptive error message.
        response (Optional[requests.Response]): The HTTP response that caused the error, if available.
        data (Any): The data that failed validation.
        errors (Optional[Dict[str, Any]]): Detailed validation errors, if available.
    """

    data: Any
    errors: Dict[str, Any]

    def __init__(self, message: str, data: Any, response: Optional[requests.Response] = None, errors: Optional[Dict[str, Any]] = None) -> None: ...
    def __repr__(self) -> str: ...

class InvalidClientError(APIError):
    """
    Raised when an invalid client or client configuration is provided.

    This error is raised when the client or client configuration provided
    to the API class is invalid or incompatible.

    Attributes:
        message (str): A descriptive error message.
    """

    message: str

    def __init__(self, message: str = "Invalid client provided") -> None: ...
    def __repr__(self) -> str: ...

class ClientInitializationError(APIError):
    """
    Raised when the client could not be initialized.

    This error is raised when the API class fails to initialize the client,
    typically due to missing or invalid configuration.
    """

    pass

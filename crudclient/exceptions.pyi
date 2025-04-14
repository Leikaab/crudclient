from typing import Any, Optional, Union  # Added Union

import requests
from pydantic import ValidationError as PydanticValidationError
from requests import PreparedRequest
from requests import exceptions as requests_exceptions  # Added PreparedRequest

class CrudClientError(Exception):
    """Base exception for all crudclient errors.

    Attributes:
        message (str): A descriptive error message.
    """

    message: str

    def __init__(self, message: str) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class ConfigurationError(CrudClientError):
    """Error related to client configuration or initialization.

    Raised for issues like invalid base URLs, missing required settings,
    or incompatible configurations.
    """

    pass

class ClientInitializationError(ConfigurationError):
    """Error specifically during the initialization phase of the HTTP client.

    Raised when the client object (e.g., `crudclient.Client`) cannot be
    instantiated, often due to issues passed from the underlying HTTP library
    or configuration problems detected during setup.
    """

    pass

class InvalidClientError(ConfigurationError):
    """Error raised when an operation requires a client but none is available or initialized."""

    pass

class AuthenticationError(CrudClientError):
    """Error related to authentication or authorization.

    Raised for issues like invalid API keys, expired tokens, insufficient
    permissions, or failed authentication attempts.

    Attributes:
        message (str): A descriptive error message.
        response (Optional[requests.Response]): The HTTP response that indicated
            the authentication failure, if available.
    """

    response: Optional[requests.Response]

    def __init__(self, message: str, response: Optional[requests.Response] = None) -> None: ...
    def __repr__(self) -> str: ...

class NetworkError(CrudClientError):
    """Error related to network connectivity during an HTTP request.

    Raised for issues like DNS resolution failures, connection timeouts,
    or other problems preventing communication with the API server.

    Attributes:
        message (str): A descriptive error message, often including request details.
        request (Optional[requests.Request]): The HTTP request that failed due to the network issue, if available.
        original_exception (requests_exceptions.RequestException): The underlying exception
            (e.g., requests.exceptions.Timeout, requests.exceptions.ConnectionError)
            that caused this error.
    """

    request: Optional[requests.Request]  # Changed to Optional
    original_exception: requests_exceptions.RequestException

    def __init__(
        self,
        message: str,
        request: Optional[requests.Request],  # Changed to Optional
        original_exception: requests_exceptions.RequestException,
    ) -> None: ...
    def __repr__(self) -> str: ...

class APIError(CrudClientError):
    """Error related to the API response itself (e.g., HTTP status codes >= 400).

    This is the base class for errors originating from the API server's response,
    indicating a problem with the request or server-side processing. Specific subclasses
    (like BadRequestError, NotFoundError) should be used for specific HTTP status codes.

    Attributes:
        message (str): A descriptive error message, often including status code and request details.
        request (Optional[Union[requests.Request, PreparedRequest]]): The HTTP request that resulted in the error response, if available.
        response (Optional[requests.Response]): The HTTP response received from the API, if available.
    """

    request: Optional[Union[requests.Request, PreparedRequest]]  # Changed type
    response: Optional[requests.Response]  # Changed type

    def __init__(self, message: str, request: Optional[Union[requests.Request, PreparedRequest]], response: Optional[requests.Response]) -> None: ...
    def __repr__(self) -> str: ...

# Specific HTTP Status Code Errors

class BadRequestError(APIError):
    """API error corresponding to HTTP status code 400 (Bad Request)."""

    pass

class ClientAuthenticationError(APIError, AuthenticationError):
    """API error corresponding to HTTP status code 401 (Unauthorized).

    Inherits from both APIError and AuthenticationError.
    """

    pass

class ForbiddenError(APIError):
    """API error corresponding to HTTP status code 403 (Forbidden)."""

    pass

class NotFoundError(APIError):
    """API error corresponding to HTTP status code 404 (Not Found)."""

    pass

class ConflictError(APIError):
    """API error corresponding to HTTP status code 409 (Conflict)."""

    pass

class UnprocessableEntityError(APIError):
    """API error corresponding to HTTP status code 422 (Unprocessable Entity)."""

    pass

class RateLimitError(APIError):
    """API error corresponding to HTTP status code 429 (Too Many Requests)."""

    pass

class InternalServerError(APIError):
    """API error corresponding to HTTP status code 500 (Internal Server Error)."""

    pass

class ServiceUnavailableError(APIError):
    """API error corresponding to HTTP status code 503 (Service Unavailable)."""

    pass

# Other Error Types

class DataValidationError(CrudClientError):
    """Error related to data validation, often wrapping Pydantic errors.

    Raised when incoming data (e.g., API response) or outgoing data (e.g., request payload)
    fails validation against the expected schema or model.

    Attributes:
        message (str): A descriptive error message.
        data (Any): The data that failed validation.
        pydantic_error (Optional[PydanticValidationError]): The underlying Pydantic
            validation error, if the validation was performed using Pydantic.
    """

    data: Any
    pydantic_error: Optional[PydanticValidationError]

    def __init__(
        self,
        message: str,
        data: Any,
        pydantic_error: Optional[PydanticValidationError] = None,
    ) -> None: ...
    def __repr__(self) -> str: ...

class ModelConversionError(CrudClientError):
    """Error during the conversion of response data to a Pydantic model.

    Raised when response data cannot be successfully converted into the target
    Pydantic model, potentially after initial parsing but before or during
    model instantiation. This is distinct from DataValidationError which typically
    wraps Pydantic's own validation exceptions.
    """

    pass

class ResponseParsingError(CrudClientError):
    """Error encountered while parsing or decoding an HTTP response body.

    Raised when the response body cannot be decoded (e.g., invalid JSON) or
    parsed into the expected format.

    Attributes:
        message (str): A descriptive error message, often including response details.
        response (Optional[requests.Response]): The HTTP response whose body could not be parsed, if available.
        original_exception (Exception): The underlying exception (e.g., json.JSONDecodeError)
            that occurred during parsing.
    """

    response: Optional[requests.Response]
    original_exception: Exception

    def __init__(self, message: str, original_exception: Exception, response: Optional[requests.Response] = None) -> None: ...
    def __repr__(self) -> str: ...

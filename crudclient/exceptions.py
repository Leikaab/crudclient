from typing import Any, Optional, Union

import requests
from pydantic import ValidationError as PydanticValidationError
from requests import PreparedRequest
from requests import exceptions as requests_exceptions


class CrudClientError(Exception):
    """Base exception for all crudclient errors.

    Attributes:
        message (str): A descriptive error message.
    """

    message: str

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r})"


class ConfigurationError(CrudClientError):
    """Error related to client configuration or initialization.

    Raised for issues like invalid base URLs, missing required settings,
    or incompatible configurations.
    """


class ClientInitializationError(ConfigurationError):
    """Error specifically during the initialization phase of the HTTP client.

    Raised when the client object (e.g., `crudclient.Client`) cannot be
    instantiated, often due to issues passed from the underlying HTTP library
    or configuration problems detected during setup.
    """


class InvalidClientError(ConfigurationError):
    """Error raised when an operation requires a client but none is available or initialized."""


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

    def __init__(self, message: str, response: Optional[requests.Response] = None) -> None:
        self.response = response
        super().__init__(message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, response={self.response!r})"


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

    request: Optional[requests.Request]
    original_exception: requests_exceptions.RequestException

    def __init__(
        self,
        message: str,
        request: Optional[requests.Request],
        original_exception: requests_exceptions.RequestException,
    ) -> None:
        self.request = request
        self.original_exception = original_exception
        request_info = f"{request.method} {request.url}" if request else "N/A"
        full_message = f"{message} (Request: {request_info})"
        super().__init__(full_message)
        self.__cause__ = original_exception

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, " f"request={self.request!r}, original_exception={self.original_exception!r})"


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

    request: Optional[Union[requests.Request, PreparedRequest]]
    response: Optional[requests.Response]

    def __init__(
        self,
        message: str,
        *,  # Make subsequent arguments keyword-only
        request: Optional[Union[requests.Request, PreparedRequest]] = None,
        response: Optional[requests.Response] = None,
    ) -> None:
        self.request = request
        self.response = response
        status_code = response.status_code if response else "N/A"
        request_info = f"{request.method} {request.url}" if request else "N/A"
        full_message = f"{message} (Status Code: {status_code}, Request: {request_info})"
        super().__init__(full_message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, request={self.request!r}, response={self.response!r})"


# Specific HTTP Status Code Errors


class BadRequestError(APIError):
    """API error corresponding to HTTP status code 400 (Bad Request)."""


class ClientAuthenticationError(APIError, AuthenticationError):
    """API error corresponding to HTTP status code 401 (Unauthorized).

    Inherits from both APIError and AuthenticationError.
    """

    def __init__(
        self,
        message: str,
        response: Optional[requests.Response] = None,
        request: Optional[Union[requests.Request, PreparedRequest]] = None,
    ) -> None:
        """Initialize the ClientAuthenticationError.

        Args:
            message: A descriptive error message.
            response: The HTTP response that indicated the authentication failure.
            request: The HTTP request that resulted in the error response.
        """
        # Call CrudClientError.__init__ to set the basic message
        CrudClientError.__init__(self, message)

        # Explicitly set response and request attributes
        self.response = response
        self.request = request

        # Format the message with status code and request info if available
        status_code = response.status_code if response else "N/A"
        request_info = f"{request.method} {request.url}" if request else "N/A"
        self.message = f"{message} (Status Code: {status_code}, Request: {request_info})"


class ForbiddenError(APIError):
    """API error corresponding to HTTP status code 403 (Forbidden)."""


class NotFoundError(APIError):
    """API error corresponding to HTTP status code 404 (Not Found)."""


class MultipleResourcesFoundError(NotFoundError):
    """Raised when a search expecting one result finds multiple.

    This exception inherits from NotFoundError to maintain compatibility
    with error handling that catches NotFoundError.
    """


class ConflictError(APIError):
    """API error corresponding to HTTP status code 409 (Conflict)."""


class UnprocessableEntityError(APIError):
    """API error corresponding to HTTP status code 422 (Unprocessable Entity)."""


class RateLimitError(APIError):
    """API error corresponding to HTTP status code 429 (Too Many Requests)."""


class InternalServerError(APIError):
    """API error corresponding to HTTP status code 500 (Internal Server Error)."""


class ServiceUnavailableError(APIError):
    """API error corresponding to HTTP status code 503 (Service Unavailable)."""


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
    ) -> None:
        self.data = data
        self.pydantic_error = pydantic_error
        super().__init__(message)
        if pydantic_error:
            self.__cause__ = pydantic_error

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, data={self.data!r}, pydantic_error={self.pydantic_error!r})"


class ModelConversionError(CrudClientError):
    """Error during the conversion of response data to a Pydantic model.

    Raised when response data cannot be successfully converted into the target
    Pydantic model, potentially after initial parsing but before or during
    model instantiation. This is distinct from DataValidationError which typically
    wraps Pydantic's own validation exceptions.
    """


class DeprecatedEndpointError(CrudClientError):
    """Raised when attempting to use a deprecated endpoint.

    This exception should be raised when an endpoint is fully deprecated
    and no longer functional in the API.
    """


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

    def __init__(
        self,
        message: str,
        original_exception: Exception,
        response: Optional[requests.Response] = None,
    ) -> None:
        self.response = response
        self.original_exception = original_exception
        status_code = response.status_code if response else "N/A"
        request_info = f"{response.request.method} {response.request.url}" if response and response.request else "N/A"
        full_message = f"{message} (Status Code: {status_code}, Request: {request_info})"
        super().__init__(full_message)
        self.__cause__ = original_exception

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, response={self.response!r}, original_exception={self.original_exception!r})"

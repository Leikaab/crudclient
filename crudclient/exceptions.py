from typing import Union  # Added Union
from typing import Any, Optional

import requests
from pydantic import ValidationError as PydanticValidationError
from requests import PreparedRequest
from requests import exceptions as requests_exceptions


class CrudClientError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r})"


class ConfigurationError(CrudClientError):
    pass


class ClientInitializationError(ConfigurationError):
    pass


class InvalidClientError(ConfigurationError):
    pass


class AuthenticationError(CrudClientError):
    pass


class NetworkError(CrudClientError):
    def __init__(
        self,
        message: str,
        request: Optional[requests.Request],  # Changed to Optional
        original_exception: requests_exceptions.RequestException,
    ):
        self.request = request
        self.original_exception = original_exception
        request_info = f"{request.method} {request.url}" if request else "N/A"
        full_message = f"{message} (Request: {request_info})"
        super().__init__(full_message)
        self.__cause__ = original_exception

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"request={self.request!r}, original_exception={self.original_exception!r})"  # repr is fine with None
        )


class APIError(CrudClientError):
    def __init__(
        self,
        message: str,
        *,  # Make subsequent arguments keyword-only
        request: Optional[Union[requests.Request, PreparedRequest]] = None,
        response: Optional[requests.Response] = None,
    ):
        self.request = request
        self.response = response
        status_code = response.status_code if response else "N/A"
        request_info = f"{request.method} {request.url}" if request else "N/A"
        full_message = f"{message} (Status Code: {status_code}, Request: {request_info})"
        super().__init__(full_message)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, " f"request={self.request!r}, response={self.response!r})"


# Specific HTTP Status Code Errors


class BadRequestError(APIError):
    pass


class ClientAuthenticationError(APIError, AuthenticationError):
    pass


class ForbiddenError(APIError):
    pass


class NotFoundError(APIError):
    pass


class ConflictError(APIError):
    pass


class UnprocessableEntityError(APIError):
    pass


class RateLimitError(APIError):
    pass


class InternalServerError(APIError):
    pass


class ServiceUnavailableError(APIError):
    pass


# Other Error Types


class DataValidationError(CrudClientError):
    def __init__(
        self,
        message: str,
        data: Any,
        pydantic_error: Optional[PydanticValidationError] = None,
    ):
        self.data = data
        self.pydantic_error = pydantic_error
        super().__init__(message)
        if pydantic_error:
            self.__cause__ = pydantic_error

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, " f"data={self.data!r}, pydantic_error={self.pydantic_error!r})"


class ModelConversionError(CrudClientError):
    pass


class ResponseParsingError(CrudClientError):
    def __init__(
        self,
        message: str,
        original_exception: Exception,
        response: Optional[requests.Response] = None,
    ):
        self.response = response
        self.original_exception = original_exception
        status_code = response.status_code if response else "N/A"
        request_info = f"{response.request.method} {response.request.url}" if response and response.request else "N/A"
        full_message = f"{message} (Status Code: {status_code}, Request: {request_info})"
        super().__init__(full_message)
        self.__cause__ = original_exception

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, " f"response={self.response!r}, original_exception={self.original_exception!r})"

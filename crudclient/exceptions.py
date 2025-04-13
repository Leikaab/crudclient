from typing import Any, Dict, Optional

import requests
from pydantic import ValidationError as PydanticValidationError


class APIError(Exception):
    def __str__(self):
        original_exception = f"\nCaused by: {self.__cause__}" if self.__cause__ else ""
        exception_name = self.__class__.__name__
        return f"{exception_name}: {super().__str__()}{original_exception}"


class CrudClientError(APIError):
    def __init__(self, message: str, response: Optional[requests.Response] = None):
        self.message = message
        self.response = response
        super().__init__(message)

    def __repr__(self):
        return f"{self.__class__.__name__}(message={self.message!r}, response={self.response!r})"


class AuthenticationError(CrudClientError):
    pass


class NotFoundError(CrudClientError):
    pass


class InvalidResponseError(CrudClientError):
    pass


class ModelConversionError(CrudClientError):

    def __init__(self, message: str, response: Optional[requests.Response] = None, data: Any = None):
        self.data = data
        super().__init__(message, response)

    def __repr__(self):
        return f"{self.__class__.__name__}(message={self.message!r}, response={self.response!r}, data={self.data!r})"


class ValidationError(CrudClientError):

    def __init__(
        self,
        message: str,
        data: Any,
        response: Optional[requests.Response] = None,
        errors: Optional[Dict[str, Any]] = None,
        pydantic_error: Optional[PydanticValidationError] = None,  # Added parameter
    ):
        self.data = data
        self.errors = errors or {}
        self.pydantic_error = pydantic_error  # Store the Pydantic error
        super().__init__(message, response)

    def __repr__(self):
        # Include pydantic_error in repr if it exists
        pydantic_repr = f", pydantic_error={self.pydantic_error!r}" if self.pydantic_error else ""
        return (
            f"{self.__class__.__name__}(message={self.message!r}, "
            f"response={self.response!r}, data={self.data!r}, errors={self.errors!r}{pydantic_repr})"
        )


class InvalidClientError(APIError):
    def __init__(self, message: str = "Invalid client provided"):
        self.message = message
        super().__init__(message)

    def __repr__(self):
        return f"InvalidClientError(message={self.message!r})"


class ClientInitializationError(APIError):
    pass

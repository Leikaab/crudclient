import logging
from typing import Dict, Type

import requests

from ..exceptions import (
    AuthenticationError,
    CrudClientError,
    InvalidResponseError,
    NotFoundError,
)

# Set up logging
logger = logging.getLogger(__name__)


class ErrorHandler:

    def __init__(self) -> None:
        # Map status codes to specific error types
        self.status_code_to_exception: Dict[int, Type[CrudClientError]] = {
            400: CrudClientError,
            401: AuthenticationError,
            403: AuthenticationError,
            404: NotFoundError,
            422: InvalidResponseError,
        }

    def handle_error_response(self, response: requests.Response) -> None:
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        try:
            error_data = response.json()
        except ValueError:
            logger.warning("Failed to parse JSON response.")
            error_data = response.text

        status_code = response.status_code
        error_message = f"HTTP error occurred: {status_code}, {error_data}"
        logger.error(error_message)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            # Get the appropriate exception class for the status code
            exception_class = self.status_code_to_exception.get(status_code, CrudClientError)

            # Create a more specific error message based on the exception type
            if exception_class == AuthenticationError:
                specific_message = f"Authentication failed: {error_data}"
            elif exception_class == NotFoundError:
                specific_message = f"Resource not found: {error_data}"
            elif exception_class == InvalidResponseError:
                specific_message = f"Invalid response: {error_data}"
            else:
                specific_message = error_message

            raise exception_class(specific_message, response) from e

        # This should not be reached, but just in case
        raise CrudClientError(f"Request failed with status code {status_code}, {error_data}", response)

    def register_status_code_handler(self, status_code: int, exception_class: Type[CrudClientError]) -> None:
        # Runtime type checks
        if not isinstance(status_code, int):
            raise TypeError(f"status_code must be an integer, got {type(status_code).__name__}")

        if not isinstance(exception_class, type) or not issubclass(exception_class, CrudClientError):
            raise TypeError(f"exception_class must be a subclass of CrudClientError, got {type(exception_class).__name__}")
        self.status_code_to_exception[status_code] = exception_class

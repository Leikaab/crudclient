import logging
from typing import Dict, Type

import requests

# First-party imports grouped and sorted
from ..exceptions import (
    APIError,
    BadRequestError,
    ClientAuthenticationError,
    ConflictError,
    CrudClientError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    UnprocessableEntityError,
)

logger = logging.getLogger(__name__)


class ErrorHandler:

    def __init__(self) -> None:
        self.status_code_to_exception: Dict[int, Type[CrudClientError]] = {
            400: BadRequestError,
            401: ClientAuthenticationError,  # Changed
            403: ForbiddenError,
            404: NotFoundError,
            409: ConflictError,  # Added
            422: UnprocessableEntityError,  # Changed
            429: RateLimitError,  # Added
            500: InternalServerError,
            # 502: APIError, # Removed
            503: ServiceUnavailableError,
        }

    def handle_error_response(self, response: requests.Response) -> None:
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        try:
            error_data = response.json()
        except requests.exceptions.JSONDecodeError as json_err:
            logger.warning(
                "Failed to parse JSON from error response: %s",
                json_err,
                exc_info=True,
            )
            error_data = response.text

        status_code = response.status_code
        logger.error(
            "HTTP error occurred: Status Code: %s, Response Body: %s",
            status_code,
            error_data,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            exception_class = self.status_code_to_exception.get(status_code, APIError)

            error_message = f"HTTP error {status_code}: {error_data}"
            exception_args = {
                "message": error_message,
                "request": response.request,
                "response": response,
            }

            # No specific elif needed for UnprocessableEntityError, handled by issubclass(APIError)
            if issubclass(exception_class, APIError):  # Handles ClientAuthenticationError, UnprocessableEntityError, etc.
                raise exception_class(**exception_args) from e
            else:  # Handle non-APIError custom exceptions if registered
                logger.warning("Status code %s mapped to non-APIError subclass %s.", status_code, exception_class.__name__)
                # Attempt to raise with standard APIError args, might fail if signature differs
                try:
                    # Base CrudClientError only takes message
                    raise exception_class(message=error_message) from e
                except TypeError:
                    logger.error(
                        "Failed to instantiate custom non-APIError %s with standard args. Falling back to APIError.",
                        exception_class.__name__,
                        exc_info=True,
                    )
                    # Fallback to generic APIError
                    raise APIError(**exception_args) from e

        logger.warning("Error handler reached end without raising specific exception for status %s.", status_code)
        raise APIError(
            f"Request failed with status code {status_code}: {error_data}",
            request=response.request,
            response=response,
        )

    def register_status_code_handler(self, status_code: int, exception_class: Type[CrudClientError]) -> None:
        if not isinstance(status_code, int):
            raise TypeError(f"status_code must be an integer, got {type(status_code).__name__}")

        if not isinstance(exception_class, type) or not issubclass(exception_class, CrudClientError):
            raise TypeError("exception_class must be a subclass of CrudClientError, got " f"{type(exception_class).__name__}")
        if not issubclass(exception_class, APIError):
            logger.warning(
                "Registering non-APIError subclass %s for status code %s. " "Ensure its signature matches usage in handle_error_response.",
                exception_class.__name__,
                status_code,
            )

        self.status_code_to_exception[status_code] = exception_class

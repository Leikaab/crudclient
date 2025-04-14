"""
Error Handling Module for CrudClient
===================================

This module provides centralized error handling functionality for the CrudClient library.
It contains classes and functions for processing HTTP error responses and mapping them
to appropriate exceptions.

Classes:
    - ErrorHandler: Centralizes error processing logic for HTTP responses.
"""

from typing import Dict, Optional, Type

import requests

from ..exceptions import CrudClientError

class ErrorHandler:
    """
    Centralizes error processing logic for HTTP responses.

    This class provides methods for handling error responses from API calls,
    extracting error information, and raising appropriate exceptions based on
    status codes.

    Attributes:
        status_code_to_exception (Dict[int, Type[CrudClientError]]): Mapping of HTTP status
            codes to exception types.
    """

    status_code_to_exception: Dict[int, Type[CrudClientError]]

    def __init__(self) -> None:
        """
        Initialize the ErrorHandler with default status code to exception mappings.
        """
        ...

    def handle_error_response(self, response: requests.Response) -> None:
        """
        Handle error responses from the API.

        This method attempts to extract error information from the response and raises
        appropriate exceptions based on the status code.

        Args:
            response: The response object from the API.

        Raises:
            AuthenticationError: If the status code is 401 (Unauthorized) or 403 (Forbidden).
            NotFoundError: If the status code is 404 (Not Found).
            DataValidationError: If the status code is 422 (Unprocessable Entity).
            CrudClientError: For other error status codes.
            TypeError: If response is not a requests.Response object.
        """
        ...

    def register_status_code_handler(self, status_code: int, exception_class: Type[CrudClientError]) -> None:
        """Registers a custom exception handler for a specific HTTP status code.

        This allows users to override or extend the default behavior for handling
        specific HTTP error codes by providing their own CrudClientError subclass.

        Args:
            status_code: The integer HTTP status code (e.g., 409).
            exception_class: The subclass of CrudClientError to be raised when
                this status code is encountered.

        Raises:
            TypeError: If `status_code` is not an integer or if `exception_class`
                is not a type or not a subclass of `CrudClientError`.

        Example:
            >>> class ConflictError(APIError):
            ...     pass
            ...
            >>> error_handler = ErrorHandler()
            >>> error_handler.register_status_code_handler(409, ConflictError)
        """
        ...

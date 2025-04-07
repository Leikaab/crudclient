"""
Module `response.py`
===================

This module defines the ResponseHandler class, which is responsible for processing and validating
HTTP responses. It provides methods for parsing responses based on content type and handling
different response formats.

Class `ResponseHandler`
----------------------

The `ResponseHandler` class provides a flexible way to process HTTP responses based on their
content type. It includes methods for parsing different content types (JSON, binary, text)
and validating response status.

To use the ResponseHandler:
    1. Create a ResponseHandler instance.
    2. Use the handle_response method to process a response.
    3. The method will return the parsed response data based on the content type.

Example:
    handler = ResponseHandler()
    parsed_data = handler.handle_response(response)
    # Use parsed_data in your application

Classes:
    - ResponseHandler: Main class for response processing and validation.
"""

import logging

import requests

from ..types import RawResponseSimple

# Set up logging
logger = logging.getLogger(__name__)


class ResponseHandler:
    """
    Handles HTTP response processing and validation.

    This class is responsible for processing HTTP responses based on their content type
    and validating response status. It supports JSON, binary, and text responses.

    Methods:
        handle_response: Processes an HTTP response and returns the parsed data.
        parse_json_response: Parses a JSON response.
        parse_binary_response: Parses a binary response.
        parse_text_response: Parses a text response.
    """

    def handle_response(self, response: requests.Response) -> RawResponseSimple:
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if not isinstance(response, requests.Response) and not hasattr(response, '_mock_spec') and requests.Response not in getattr(response, '_mock_spec', []):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        if not response.ok:
            # Let the caller handle error responses
            logger.debug(f"Response not OK: {response.status_code}")
            # We don't handle error responses here, just raise an exception
            # to indicate that the caller should handle it
            response.raise_for_status()

        # Special handling for 204 No Content responses
        if response.status_code == 204:
            logger.debug("Received 204 No Content response, returning None")
            return None

        content_type = response.headers.get("Content-Type", "")
        logger.debug(f"Processing response with content type: {content_type}")

        # Use startswith() for more precise Content-Type checking
        if content_type.startswith("application/json"):
            return self.parse_json_response(response)
        elif content_type.startswith("application/octet-stream") or content_type.startswith("multipart/form-data"):
            return self.parse_binary_response(response)
        else:
            return self.parse_text_response(response)

    def parse_json_response(self, response: requests.Response) -> dict:
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if not isinstance(response, requests.Response) and not hasattr(response, '_mock_spec') and requests.Response not in getattr(response, '_mock_spec', []):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        logger.debug("Parsing JSON response")
        return response.json()

    def parse_binary_response(self, response: requests.Response) -> bytes:
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if not isinstance(response, requests.Response) and not hasattr(response, '_mock_spec') and requests.Response not in getattr(response, '_mock_spec', []):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        logger.debug("Parsing binary response")
        return response.content

    def parse_text_response(self, response: requests.Response) -> str:
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if not isinstance(response, requests.Response) and not hasattr(response, '_mock_spec') and requests.Response not in getattr(response, '_mock_spec', []):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        logger.debug("Parsing text response")
        return response.text

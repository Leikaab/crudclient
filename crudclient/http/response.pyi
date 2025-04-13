"""
Stub file for `response.py`
==========================

This file provides type hints and method signatures for the `response.py` module.
It is used to provide better type checking and autocompletion support.
"""

from typing import Any, Dict

import requests

from ..types import RawResponseSimple

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
        """
        Process an HTTP response and return the parsed data.

        This method checks if the response is successful and then parses the response
        based on its content type. It delegates to specific parsing methods based on
        the content type.

        Args:
            response (requests.Response): The HTTP response to process.

        Returns:
            RawResponseSimple: The parsed response data, which could be a JSON dictionary,
                               binary content, or text.

        Raises:
            requests.HTTPError: If the response status code indicates an error.
            TypeError: If response is not a requests.Response object.

        Note:
            This method does not handle error responses. It assumes that error handling
            is done by the caller before this method is called.
        """
        ...

    def parse_json_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Parse a JSON response.

        Args:
            response (requests.Response): The HTTP response with JSON content.

        Returns:
            Dict[str, Any]: The parsed JSON data as a dictionary.

        Raises:
            TypeError: If response is not a requests.Response object.
        """
        ...

    def parse_binary_response(self, response: requests.Response) -> bytes:
        """
        Parse a binary response.

        Args:
            response (requests.Response): The HTTP response with binary content.

        Returns:
            bytes: The binary content of the response.

        Raises:
            TypeError: If response is not a requests.Response object.
        """
        ...

    def parse_text_response(self, response: requests.Response) -> str:
        """
        Parse a text response.

        Args:
            response (requests.Response): The HTTP response with text content.

        Returns:
            str: The text content of the response.

        Raises:
            TypeError: If response is not a requests.Response object.
        """
        ...

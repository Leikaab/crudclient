"""
Module `request.py`
==================

This module defines the RequestFormatter class, which is responsible for handling request
preparation and content-type setting. It provides methods for formatting different types of
requests (JSON, form data, multipart) and setting the appropriate content-type headers.

Class `RequestFormatter`
-----------------------

The `RequestFormatter` class provides a flexible way to prepare request data based on the
content type. It includes methods for different content types (JSON, form data, multipart)
and handles the appropriate content-type header setting.

To use the RequestFormatter:
    1. Create a RequestFormatter instance.
    2. Use the appropriate method to prepare the request data.
    3. Apply the returned headers and data to your request.

Example:
    formatter = RequestFormatter()
    prepared_data, headers = formatter.prepare_json({"name": "example"})
    # Use prepared_data and headers in your request

Classes:
    - RequestFormatter: Main class for request preparation and formatting.
"""

from typing import Any, Dict, Optional, Tuple

class RequestFormatter:
    """
    Handles request preparation and content-type setting.

    This class is responsible for formatting request data based on the content type
    and providing the appropriate content-type headers. It supports JSON, form data,
    and multipart requests.

    Methods:
        prepare_data: Prepares request data based on the provided parameters.
        prepare_json: Prepares JSON request data.
        prepare_form_data: Prepares form data request.
        prepare_multipart: Prepares multipart form data request.
        get_content_type_header: Returns the content-type header for a given content type.
    """

    def prepare_data(
        self, data: Optional[Dict[str, Any]] = None, json: Optional[Any] = None, files: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Prepare request data based on the provided parameters.

        This method determines the appropriate content type based on the provided data
        and returns the prepared data along with the necessary headers.

        Args:
            data (Optional[Dict[str, Any]]): Form data to include in the request.
            json (Optional[Any]): JSON data to include in the request.
            files (Optional[Dict[str, Any]]): Files to include in the request.

        Returns:
            Tuple[Dict[str, Any], Dict[str, str]]: A tuple containing:
                - The prepared request data as a dictionary.
                - The headers dictionary with the appropriate content-type.

        Raises:
            TypeError: If the parameters are of incorrect types.
        """
        ...

    def prepare_json(self, json_data: Any) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Prepare JSON request data.

        Args:
            json_data (Any): The JSON data to include in the request.

        Returns:
            Tuple[Dict[str, Any], Dict[str, str]]: A tuple containing:
                - A dictionary with the 'json' key set to the provided JSON data.
                - The headers dictionary with the content-type set to 'application/json'.
        """
        ...

    def prepare_form_data(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Prepare form data request.

        Args:
            data (Dict[str, Any]): The form data to include in the request.

        Returns:
            Tuple[Dict[str, Any], Dict[str, str]]: A tuple containing:
                - A dictionary with the 'data' key set to the provided form data.
                - The headers dictionary with the content-type set to 'application/x-www-form-urlencoded'.

        Raises:
            TypeError: If data is not a dictionary.
        """
        ...

    def prepare_multipart(self, files: Dict[str, Any], data: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Prepare multipart form data request.

        Args:
            files (Dict[str, Any]): The files to include in the request.
            data (Optional[Dict[str, Any]]): Additional form data to include in the request.

        Returns:
            Tuple[Dict[str, Any], Dict[str, str]]: A tuple containing:
                - A dictionary with 'files' and optionally 'data' keys.
                - The headers dictionary with the content-type set to 'multipart/form-data'.

        Raises:
            TypeError: If files is not a dictionary or data is not a dictionary or None.
        """
        ...

    def get_content_type_header(self, content_type: str) -> Dict[str, str]:
        """
        Get the content-type header for a given content type.

        Args:
            content_type (str): The content type to set in the header.

        Returns:
            Dict[str, str]: A dictionary with the 'Content-Type' key set to the provided content type.

        Raises:
            TypeError: If content_type is not a string.
        """
        ...

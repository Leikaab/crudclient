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

import logging
from typing import Any, Dict, Optional, Tuple

# Set up logging
logger = logging.getLogger(__name__)


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
        self,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        # Runtime type checks for critical parameters
        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")

        if json is not None:
            return self.prepare_json(json)
        elif files is not None:
            return self.prepare_multipart(files, data)
        elif data is not None:
            return self.prepare_form_data(data)
        return {}, {}

    def prepare_json(self, json_data: Any) -> Tuple[Dict[str, Any], Dict[str, str]]:
        headers = self.get_content_type_header("application/json")
        return {"json": json_data}, headers

    def prepare_form_data(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        # Runtime type check
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary, got {type(data).__name__}")
        headers = self.get_content_type_header("application/x-www-form-urlencoded")
        return {"data": data}, headers

    def prepare_multipart(
        self,
        files: Dict[str, Any],
        data: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        # Runtime type checks
        if not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary, got {type(files).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")
        headers = self.get_content_type_header("multipart/form-data")
        result = {"files": files}
        if data is not None:
            result["data"] = data
        return result, headers

    def get_content_type_header(self, content_type: str) -> Dict[str, str]:
        # Runtime type check
        if not isinstance(content_type, str):
            raise TypeError(f"content_type must be a string, got {type(content_type).__name__}")
        return {"Content-Type": content_type}

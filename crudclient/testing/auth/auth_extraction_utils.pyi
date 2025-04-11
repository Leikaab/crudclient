"""
Authentication extraction utilities for testing.

This module provides helper methods for extracting authentication information
from headers and tokens.
"""

import base64
import json
from typing import Any, Dict, Tuple

class AuthExtractionUtils:
    """
    Helper methods for extracting authentication information.

    This class provides static methods for extracting credentials, tokens,
    and JWT payloads from authentication headers and tokens.
    """

    @staticmethod
    def extract_basic_auth_credentials(header_value: str) -> Tuple[str, str]:
        """
        Extract username and password from a Basic Auth header.

        Args:
            header_value: The value of the Authorization header

        Returns:
            A tuple of (username, password)

        Raises:
            ValueError: If the header is not a valid Basic Auth header
        """
        ...

    @staticmethod
    def extract_bearer_token(header_value: str) -> str:
        """
        Extract token from a Bearer Auth header.

        Args:
            header_value: The value of the Authorization header

        Returns:
            The Bearer token

        Raises:
            ValueError: If the header is not a valid Bearer Auth header
        """
        ...

    @staticmethod
    def extract_jwt_payload(token: str) -> Dict[str, Any]:
        """
        Extract and decode the payload from a JWT token.

        Args:
            token: The JWT token

        Returns:
            The decoded JWT payload as a dictionary

        Raises:
            ValueError: If the token is not a valid JWT
            TypeError: If the provided token is not a string
        """
        ...

"""
Authentication header verification utilities for testing.

This module provides helper methods for verifying authentication headers,
including Basic Auth, Bearer Auth, and API Key headers.
"""

from typing import Any, Dict, Optional

from .auth_extraction_utils import AuthExtractionUtils

class AuthHeaderVerification:
    """
    Helper methods for verifying authentication headers.

    This class provides static methods for verifying various types of
    authentication headers, including Basic Auth, Bearer Auth, and API Key headers.
    """

    @staticmethod
    def verify_basic_auth_header(header_value: str) -> bool:
        """
        Verify that a Basic Auth header is correctly formatted.

        Args:
            header_value: The value of the Authorization header

        Returns:
            True if the header is a valid Basic Auth header, False otherwise
        """
        ...

    @staticmethod
    def verify_bearer_auth_header(header_value: str) -> bool:
        """
        Verify that a Bearer Auth header is correctly formatted.

        Args:
            header_value: The value of the Authorization header

        Returns:
            True if the header is a valid Bearer Auth header, False otherwise
        """
        ...

    @staticmethod
    def verify_api_key_header(header_value: str, expected_key: Optional[str] = None) -> bool:
        """
        Verify that an API Key header is correctly formatted and matches the expected key.

        Args:
            header_value: The value of the API Key header
            expected_key: The expected API key value (if None, only format is checked)

        Returns:
            True if the header is a valid API Key header, False otherwise
        """
        ...

    @staticmethod
    def assert_auth_header_format(
        headers: Dict[str, str],
        auth_type: str,
        header_name: str = "Authorization"
    ) -> None:
        """
        Assert that an authentication header has the correct format.

        Args:
            headers: The headers dictionary
            auth_type: The authentication type ("Basic", "Bearer", or "ApiKey")
            header_name: The name of the header (default: "Authorization")

        Raises:
            AssertionError: If the header is missing or has an invalid format
        """
        ...

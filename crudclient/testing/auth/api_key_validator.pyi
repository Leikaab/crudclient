"""
API Key validation utilities for testing.

This module provides a class for validating API keys with support for
key format validation, expiration, and revocation.
"""

from datetime import datetime
from typing import Dict, List, Optional, Pattern, Set

class ApiKeyValidator:
    """
    API Key validator with support for key format validation, expiration, and revocation.

    This class provides methods for validating API keys against various rules,
    including key format, expiration, and revocation.
    """

    valid_keys: Set[str]
    key_format_pattern: Optional[Pattern]
    key_metadata: Dict[str, Dict]
    revoked_keys: Set[str]

    def __init__(self) -> None:
        """
        Initialize an API Key validator.
        """
        ...

    def add_valid_key(self, api_key: str) -> None:
        """
        Add a valid API key.

        Args:
            api_key: The API key to add
        """
        ...

    def set_key_metadata(
        self,
        api_key: str,
        owner: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        tier: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> None:
        """
        Set metadata for a specific API key.

        Args:
            api_key: The API key to set metadata for
            owner: Owner of the API key
            permissions: List of permissions associated with the key
            tier: Service tier associated with the key
            expires_at: Expiration time for the key
        """
        ...

    def set_key_format_pattern(self, pattern: Pattern) -> None:
        """
        Set a regex pattern that valid API keys must match.

        Args:
            pattern: Regular expression pattern for API key validation
        """
        ...

    def revoke_key(self, api_key: str) -> None:
        """
        Revoke a specific API key.

        Args:
            api_key: The API key to revoke
        """
        ...

    def validate_key(self, api_key: str) -> bool:
        """
        Validate an API key against all configured rules.

        Args:
            api_key: The API key to validate

        Returns:
            True if the key is valid, False otherwise
        """
        ...

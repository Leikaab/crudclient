"""
OAuth scope validation utilities for testing.

This module provides a class for validating OAuth scopes against available
and required scopes.
"""

from typing import List, Optional, Set

class OAuthScopeValidator:
    """
    OAuth scope validator for validating requested scopes.

    This class provides methods for validating OAuth scopes against available
    and required scopes, as well as generating default scopes.
    """

    available_scopes: Set[str]
    required_scopes: Set[str]

    def __init__(self) -> None:
        """
        Initialize an OAuth scope validator.
        """
        ...

    def set_available_scopes(self, scopes: List[str]) -> None:
        """
        Set the available scopes for the OAuth server.

        Args:
            scopes: The available scopes
        """
        ...

    def add_available_scope(self, scope: str) -> None:
        """
        Add a scope to the available scopes.

        Args:
            scope: The scope to add
        """
        ...

    def set_required_scopes(self, scopes: List[str]) -> None:
        """
        Set the required scopes for the OAuth server.

        Args:
            scopes: The required scopes
        """
        ...

    def add_required_scope(self, scope: str) -> None:
        """
        Add a scope to the required scopes.

        Args:
            scope: The scope to add
        """
        ...

    def validate_scopes(self, scopes: Optional[str]) -> bool:
        """
        Validate that the provided scopes are valid and include all required scopes.

        Args:
            scopes: Space-separated list of scopes

        Returns:
            True if scopes are valid, False otherwise
        """
        ...

    def get_default_scopes(self) -> str:
        """
        Get the default scopes (required scopes + some common ones).

        Returns:
            Space-separated list of default scopes
        """
        ...

from typing import List, Optional, Set


class OAuthScopeValidator:
    def __init__(self):
        self.available_scopes: Set[str] = {"read", "write", "admin", "user", "profile", "email"}
        self.required_scopes: Set[str] = set()

    def set_available_scopes(self, scopes: List[str]) -> None:
        """Set the available scopes for the OAuth server."""
        self.available_scopes = set(scopes)

    def add_available_scope(self, scope: str) -> None:
        """Add a scope to the available scopes."""
        self.available_scopes.add(scope)

    def set_required_scopes(self, scopes: List[str]) -> None:
        """Set the required scopes for the OAuth server."""
        self.required_scopes = set(scopes)

    def add_required_scope(self, scope: str) -> None:
        """Add a scope to the required scopes."""
        self.required_scopes.add(scope)

    def validate_scopes(self, scopes: Optional[str]) -> bool:
        """
        Validate that the provided scopes are valid and include all required scopes.

        Args:
            scopes: Space-separated list of scopes

        Returns:
            True if scopes are valid, False otherwise
        """
        if not scopes:
            return len(self.required_scopes) == 0

        scope_list = scopes.split()

        # Check that all scopes are valid
        for scope in scope_list:
            if scope not in self.available_scopes:
                return False

        # Check that all required scopes are included
        for required_scope in self.required_scopes:
            if required_scope not in scope_list:
                return False

        return True

    def get_default_scopes(self) -> str:
        """Get the default scopes (required scopes + some common ones)."""
        default_scopes = set(self.required_scopes)

        # Add some common scopes if available
        common_scopes = {"read", "write"}
        for scope in common_scopes:
            if scope in self.available_scopes:
                default_scopes.add(scope)

        return " ".join(sorted(default_scopes))

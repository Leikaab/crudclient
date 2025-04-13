from typing import List, Optional, Set


class OAuthScopeValidator:
    def __init__(self):
        self.available_scopes: Set[str] = {"read", "write", "admin", "user", "profile", "email"}
        self.required_scopes: Set[str] = set()

    def set_available_scopes(self, scopes: List[str]) -> None:
        self.available_scopes = set(scopes)

    def add_available_scope(self, scope: str) -> None:
        self.available_scopes.add(scope)

    def set_required_scopes(self, scopes: List[str]) -> None:
        self.required_scopes = set(scopes)

    def add_required_scope(self, scope: str) -> None:
        self.required_scopes.add(scope)

    def validate_scopes(self, scopes: Optional[str]) -> bool:
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
        default_scopes = set(self.required_scopes)

        # Add some common scopes if available
        common_scopes = {"read", "write"}
        for scope in common_scopes:
            if scope in self.available_scopes:
                default_scopes.add(scope)

        return " ".join(sorted(default_scopes))

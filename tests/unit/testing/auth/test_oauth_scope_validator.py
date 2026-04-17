from typing import List, Optional

import pytest

from crudclient.testing.auth.oauth_scope_validator import OAuthScopeValidator


def test_scope_validator_init() -> None:
    """Test initial state of the scope validator."""
    validator = OAuthScopeValidator()
    # Check default available scopes (might change, so check a few known ones)
    assert "read" in validator.available_scopes
    assert "write" in validator.available_scopes
    assert validator.required_scopes == set()


def test_set_available_scopes() -> None:
    """Test setting available scopes, overwriting defaults."""
    validator = OAuthScopeValidator()
    validator.set_available_scopes(["scope1", "scope2"])
    assert validator.available_scopes == {"scope1", "scope2"}


def test_add_available_scope() -> None:
    """Test adding an available scope."""
    validator = OAuthScopeValidator()
    initial_scopes = validator.available_scopes.copy()
    validator.add_available_scope("new_scope")
    assert validator.available_scopes == initial_scopes.union({"new_scope"})


def test_set_required_scopes() -> None:
    """Test setting required scopes."""
    validator = OAuthScopeValidator()
    validator.set_required_scopes(["req1", "req2"])
    assert validator.required_scopes == {"req1", "req2"}


def test_add_required_scope() -> None:
    """Test adding a required scope."""
    validator = OAuthScopeValidator()
    validator.add_required_scope("req1")
    validator.add_required_scope("req2")
    validator.add_required_scope("req1")  # Duplicates ignored
    assert validator.required_scopes == {"req1", "req2"}


# --- Test validate_scopes ---


@pytest.mark.parametrize(
    "available, required, provided, expected",
    [
        # Basic cases, default available/required
        (None, None, "read write", True),
        (None, None, "read", True),
        (None, None, "profile", True),
        (None, None, "read unknown", False),  # Contains unknown scope
        (None, None, "", True),  # Empty scopes are valid if none required
        (None, None, None, True),  # None scopes are valid if none required
        # With required scopes
        (None, ["admin"], "read write admin", True),
        (None, ["admin"], "read write", False),  # Missing required
        (None, ["admin", "profile"], "profile admin", True),
        (None, ["admin"], "", False),  # Empty scopes invalid if scopes required
        (None, ["admin"], None, False),  # None scopes invalid if scopes required
        # With limited available scopes
        (["read", "profile"], None, "read profile", True),
        (["read", "profile"], None, "read", True),
        (["read", "profile"], None, "read write", False),  # Contains unavailable scope
        (["read", "profile"], ["read"], "read profile", True),
        (["read", "profile"], ["read"], "read", True),
        (["read", "profile"], ["profile"], "read", False),  # Missing required
        (["read", "profile"], ["admin"], "read profile", False),  # Required scope not available
        # Edge cases
        (None, None, " read  write ", True),  # Extra whitespace
        (["scope1"], ["scope1"], "scope1", True),
        ([], [], "", True),  # No scopes available or required, empty is valid
        ([], [], "read", False),  # No scopes available, providing one is invalid
        ([], ["read"], "", False),  # Required scope not available
    ],
)
def test_validate_scopes(
    available: Optional[List[str]],
    required: Optional[List[str]],
    provided: Optional[str],
    expected: bool,
) -> None:
    validator = OAuthScopeValidator()
    if available is not None:
        validator.set_available_scopes(available)
    if required is not None:
        validator.set_required_scopes(required)

    assert validator.validate_scopes(provided) is expected


def test_get_default_scopes_no_required() -> None:
    """Test default scopes when none are required."""
    validator = OAuthScopeValidator()
    validator.set_available_scopes(["read", "profile", "email"])
    # Should include common scopes if available
    assert validator.get_default_scopes() == "read"


def test_get_default_scopes_with_required() -> None:
    """Test default scopes includes required scopes."""
    validator = OAuthScopeValidator()
    validator.set_available_scopes(["read", "admin", "profile"])
    validator.set_required_scopes(["admin", "profile"])
    # Should include required + common available scopes
    assert validator.get_default_scopes() == "admin profile read"


def test_get_default_scopes_required_not_available() -> None:
    """Test default scopes when required scope isn't available (edge case)."""
    validator = OAuthScopeValidator()
    validator.set_available_scopes(["read", "write"])
    validator.set_required_scopes(["admin"])
    # Should still include the required scope, even if not in available
    assert validator.get_default_scopes() == "admin read write"

import base64

from crudclient.auth import BasicAuth
from crudclient.testing.auth.basic import BasicAuthMock


# Helper to create the expected auth header value
def create_basic_auth_header(username, password):
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
    return f"Basic {encoded_credentials}"


def test_basic_auth_mock_init_defaults():
    """Test default initialization."""
    mock = BasicAuthMock()
    assert mock.username == "user"
    assert mock.password == "pass"
    assert mock.case_sensitive is True
    assert mock.max_attempts is None
    assert mock.current_attempts == 0
    assert isinstance(mock.auth_strategy, BasicAuth)
    assert mock.auth_strategy.username == "user"
    assert mock.auth_strategy.password == "pass"
    assert mock.valid_credentials == [("user", "pass")]


def test_basic_auth_mock_init_custom():
    """Test initialization with custom credentials."""
    mock = BasicAuthMock(username="testuser", password="testpassword")
    assert mock.username == "testuser"
    assert mock.password == "testpassword"
    assert mock.auth_strategy.username == "testuser"
    assert mock.auth_strategy.password == "testpassword"
    assert mock.valid_credentials == [("testuser", "testpassword")]


def test_with_credentials():
    """Test updating credentials."""
    mock = BasicAuthMock().with_credentials("newuser", "newpass")
    assert mock.username == "newuser"
    assert mock.password == "newpass"
    assert mock.auth_strategy.username == "newuser"
    assert mock.auth_strategy.password == "newpass"
    assert mock.valid_credentials == [("newuser", "newpass")]


def test_with_additional_valid_credentials():
    """Test adding more valid credentials."""
    mock = BasicAuthMock().with_additional_valid_credentials("admin", "secret")
    assert mock.valid_credentials == [("user", "pass"), ("admin", "secret")]


def test_with_username_pattern():
    """Test setting a username pattern."""
    mock = BasicAuthMock().with_username_pattern(r"^[a-z]+$")
    assert mock.username_pattern is not None
    assert mock.username_pattern.match("validuser")
    assert not mock.username_pattern.match("InvalidUser1")


def test_with_password_requirements():
    """Test setting password requirements."""
    mock = BasicAuthMock().with_password_requirements(min_length=8, complexity=True)
    assert mock.password_min_length == 8
    assert mock.password_complexity is True


def test_with_case_insensitive_username():
    """Test setting case-insensitive username matching."""
    mock = BasicAuthMock().with_case_insensitive_username()
    assert mock.case_sensitive is False


def test_with_max_attempts():
    """Test setting max authentication attempts."""
    mock = BasicAuthMock().with_max_attempts(3)
    assert mock.max_attempts == 3
    assert mock.current_attempts == 0


def test_reset_attempts():
    """Test resetting authentication attempts."""
    mock = BasicAuthMock().with_max_attempts(3)
    mock.current_attempts = 2
    mock.reset_attempts()
    assert mock.current_attempts == 0


def test_get_auth_headers():
    """Test generating the Authorization header."""
    mock = BasicAuthMock("test", "secret")
    expected_header = create_basic_auth_header("test", "secret")
    assert mock.get_auth_headers() == ("Authorization", expected_header)


def test_validate_credentials_valid_default():
    """Test validating default credentials."""
    mock = BasicAuthMock()
    assert mock.validate_credentials("user", "pass") is True


def test_validate_credentials_valid_custom():
    """Test validating custom credentials."""
    mock = BasicAuthMock("custom", "pwd")
    assert mock.validate_credentials("custom", "pwd") is True


def test_validate_credentials_valid_additional():
    """Test validating additional credentials."""
    mock = BasicAuthMock().with_additional_valid_credentials("admin", "secret")
    assert mock.validate_credentials("admin", "secret") is True


def test_validate_credentials_invalid_password():
    """Test validating with incorrect password."""
    mock = BasicAuthMock()
    assert mock.validate_credentials("user", "wrongpass") is False


def test_validate_credentials_invalid_username():
    """Test validating with incorrect username."""
    mock = BasicAuthMock()
    assert mock.validate_credentials("wronguser", "pass") is False


def test_validate_credentials_case_sensitive():
    """Test case-sensitive username validation."""
    mock = BasicAuthMock("User", "Pass")
    assert mock.validate_credentials("User", "Pass") is True
    assert mock.validate_credentials("user", "Pass") is False


def test_validate_credentials_case_insensitive():
    """Test case-insensitive username validation."""
    mock = BasicAuthMock("User", "Pass").with_case_insensitive_username()
    assert mock.validate_credentials("User", "Pass") is True
    assert mock.validate_credentials("user", "Pass") is True
    assert mock.validate_credentials("USER", "Pass") is True
    assert mock.validate_credentials("uSER", "wrongpass") is False


def test_validate_credentials_username_pattern_match():
    """Test validation with matching username pattern."""
    # Add the credentials that match the pattern AND are expected to be valid
    mock = BasicAuthMock().with_username_pattern(r"user\d+").with_additional_valid_credentials("user123", "pass")
    # Now validate against the added credentials which also match the pattern
    assert mock.validate_credentials("user123", "pass") is True


def test_validate_credentials_username_pattern_mismatch():
    """Test validation with non-matching username pattern."""
    mock = BasicAuthMock().with_username_pattern(r"admin\d+")
    assert mock.validate_credentials("user123", "pass") is False


def test_validate_credentials_password_length_met():
    """Test validation with password meeting min length."""
    mock = BasicAuthMock().with_password_requirements(min_length=4)
    assert mock.validate_credentials("user", "pass") is True


def test_validate_credentials_password_length_not_met():
    """Test validation with password not meeting min length."""
    mock = BasicAuthMock().with_password_requirements(min_length=5)
    assert mock.validate_credentials("user", "pass") is False


def test_validate_credentials_password_complexity_met():
    """Test validation with password meeting complexity."""
    mock = BasicAuthMock("user", "Pass1!").with_password_requirements(complexity=True)
    assert mock.validate_credentials("user", "Pass1!") is True


def test_validate_credentials_password_complexity_not_met():
    """Test validation with password not meeting complexity."""
    mock = BasicAuthMock().with_password_requirements(complexity=True)
    assert mock.validate_credentials("user", "pass") is False  # Lacks upper, digit, special
    assert mock.validate_credentials("user", "Password") is False  # Lacks digit, special
    assert mock.validate_credentials("user", "Password123") is False  # Lacks special
    assert mock.validate_credentials("user", "Password!") is False  # Lacks digit


def test_validate_credentials_max_attempts():
    """Test validation respecting max attempts."""
    mock = BasicAuthMock().with_max_attempts(2)
    assert mock.validate_credentials("user", "wrong") is False
    assert mock.current_attempts == 1
    assert mock.validate_credentials("user", "wrong again") is False
    assert mock.current_attempts == 2
    # Third attempt should fail even if correct, because max_attempts is 2
    assert mock.validate_credentials("user", "pass") is False
    assert mock.current_attempts == 3
    # Further attempts also fail
    assert mock.validate_credentials("user", "pass") is False
    assert mock.current_attempts == 4


def test_validate_credentials_max_attempts_reset_on_success():
    """Test that attempts counter doesn't increment on success (implicitly tested elsewhere)."""
    mock = BasicAuthMock().with_max_attempts(2)
    assert mock.validate_credentials("user", "pass") is True
    assert mock.current_attempts == 0  # Should not increment on success


def test_verify_auth_header_valid():
    """Test verifying a valid auth header."""
    mock = BasicAuthMock("test", "secret")
    header = create_basic_auth_header("test", "secret")
    assert mock.verify_auth_header(header) is True


def test_verify_auth_header_invalid_prefix():
    """Test verifying header with wrong prefix."""
    mock = BasicAuthMock()
    header = create_basic_auth_header("user", "pass").replace("Basic", "Bearer")
    assert mock.verify_auth_header(header) is False


def test_verify_auth_header_invalid_encoding():
    """Test verifying header with bad base64 encoding."""
    mock = BasicAuthMock()
    assert mock.verify_auth_header("Basic invalid-base64") is False


def test_verify_auth_header_missing_colon():
    """Test verifying header with decoded value missing colon."""
    mock = BasicAuthMock()
    no_colon = base64.b64encode(b"userpass").decode("utf-8")
    assert mock.verify_auth_header(f"Basic {no_colon}") is False


def test_verify_auth_header_invalid_credentials():
    """Test verifying header with incorrect credentials."""
    mock = BasicAuthMock("test", "secret")
    header = create_basic_auth_header("wrong", "credentials")
    assert mock.verify_auth_header(header) is False


def test_verify_auth_header_case_insensitive():
    """Test verifying header with case-insensitive matching."""
    mock = BasicAuthMock("User", "Pass").with_case_insensitive_username()
    header_lower = create_basic_auth_header("user", "Pass")
    header_upper = create_basic_auth_header("USER", "Pass")
    assert mock.verify_auth_header(header_lower) is True
    assert mock.verify_auth_header(header_upper) is True


def test_handle_auth_error():
    """Test handle_auth_error always returns False."""
    mock = BasicAuthMock()
    # The argument type hint requires a MockResponse, but the method doesn't use it.
    # We can pass None or a dummy object if type checking becomes strict.
    assert mock.handle_auth_error(None) is False  # type: ignore


def test_get_auth_strategy():
    """Test getting the underlying auth strategy."""
    mock = BasicAuthMock("test", "secret")
    strategy = mock.get_auth_strategy()
    assert isinstance(strategy, BasicAuth)
    assert strategy.username == "test"
    assert strategy.password == "secret"

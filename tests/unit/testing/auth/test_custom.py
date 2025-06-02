from crudclient.auth import CustomAuth
from crudclient.testing.auth.custom_auth_mock import CustomAuthMock

# --- Test Initialization ---


def test_custom_auth_mock_init_defaults():
    """Test default initialization (default header callback)."""
    mock = CustomAuthMock()
    assert mock.header_callback_spy is not None
    assert mock.param_callback_spy is None
    assert isinstance(mock.auth_strategy, CustomAuth)

    # Check default callback behavior via the strategy
    headers = mock.auth_strategy.prepare_request_headers()
    assert headers == {"X-Custom-Auth": "custom_value"}
    assert mock.header_callback_spy.get_call_count() == 1
    # Check was_called using the method name stored in the spy
    assert mock.header_callback_spy.was_called(mock.header_callback_spy.method_name) is True

    params = mock.auth_strategy.prepare_request_params()
    assert params == {}  # No param callback by default
    # param_callback_spy should not exist or be called
    assert mock.param_callback_spy is None


def test_custom_auth_mock_init_with_header_callback():
    """Test initialization with a custom header callback."""

    def my_header_cb():
        return {"Authorization": "Bearer test_token"}

    mock = CustomAuthMock(header_callback=my_header_cb)
    assert mock.header_callback_spy is not None
    assert mock.param_callback_spy is None

    headers = mock.auth_strategy.prepare_request_headers()
    assert headers == {"Authorization": "Bearer test_token"}
    assert mock.header_callback_spy.get_call_count() == 1
    assert mock.header_callback_spy.target_function == my_header_cb


def test_custom_auth_mock_init_with_param_callback():
    """Test initialization with a custom param callback."""

    def my_param_cb():
        return {"api_key": "test_key"}

    mock = CustomAuthMock(param_callback=my_param_cb)
    assert mock.header_callback_spy is None  # No default header if param is given
    assert mock.param_callback_spy is not None

    headers = mock.auth_strategy.prepare_request_headers()
    assert headers == {}  # No header callback

    params = mock.auth_strategy.prepare_request_params()
    assert params == {"api_key": "test_key"}
    assert mock.param_callback_spy.get_call_count() == 1
    assert mock.param_callback_spy.target_function == my_param_cb


def test_custom_auth_mock_init_with_both_callbacks():
    """Test initialization with both header and param callbacks."""

    def my_header_cb():
        return {"X-H": "hval"}

    def my_param_cb():
        return {"X-P": "pval"}

    mock = CustomAuthMock(header_callback=my_header_cb, param_callback=my_param_cb)
    assert mock.header_callback_spy is not None
    assert mock.param_callback_spy is not None

    headers = mock.auth_strategy.prepare_request_headers()
    assert headers == {"X-H": "hval"}
    assert mock.header_callback_spy.get_call_count() == 1

    params = mock.auth_strategy.prepare_request_params()
    assert params == {"X-P": "pval"}
    assert mock.param_callback_spy.get_call_count() == 1


# --- Test Configuration Methods ---


def test_with_header_callback():
    """Test updating the header callback."""
    mock = CustomAuthMock()  # Starts with default
    headers1 = mock.auth_strategy.prepare_request_headers()
    assert headers1 == {"X-Custom-Auth": "custom_value"}
    assert mock.header_callback_spy.get_call_count() == 1
    old_spy = mock.header_callback_spy

    def new_header_cb():
        return {"X-New": "new_val"}

    mock.with_header_callback(new_header_cb)
    assert mock.header_callback_spy is not old_spy  # Spy object should be new
    assert mock.header_callback_spy.target_function == new_header_cb

    headers2 = mock.auth_strategy.prepare_request_headers()
    assert headers2 == {"X-New": "new_val"}
    assert mock.header_callback_spy.get_call_count() == 1  # New spy call count


def test_with_param_callback():
    """Test updating the param callback."""
    mock = CustomAuthMock()  # Starts with no param callback
    params1 = mock.auth_strategy.prepare_request_params()
    assert params1 == {}
    assert mock.param_callback_spy is None

    def new_param_cb():
        return {"p_new": "val"}

    mock.with_param_callback(new_param_cb)
    assert mock.param_callback_spy is not None
    assert mock.param_callback_spy.target_function == new_param_cb

    params2 = mock.auth_strategy.prepare_request_params()
    assert params2 == {"p_new": "val"}
    assert mock.param_callback_spy.get_call_count() == 1


def test_with_expected_header():
    mock = CustomAuthMock().with_expected_header("X-Req", "value1")
    assert mock.expected_headers == {"X-Req": "value1"}


def test_with_expected_param():
    mock = CustomAuthMock().with_expected_param("p_req", "value2")
    assert mock.expected_params == {"p_req": "value2"}


def test_with_required_header():
    mock = CustomAuthMock().with_required_header("X-Mandatory")
    assert mock.required_headers == ["X-Mandatory"]
    mock.with_required_header("X-Another").with_required_header("X-Mandatory")  # Duplicates ignored
    assert mock.required_headers == ["X-Mandatory", "X-Another"]


def test_with_required_param():
    mock = CustomAuthMock().with_required_param("p_mandatory")
    assert mock.required_params == ["p_mandatory"]


def test_with_header_validator():
    def is_valid_token(val):
        return val.startswith("Bearer ")

    mock = CustomAuthMock().with_header_validator("Authorization", is_valid_token)
    assert "Authorization" in mock.header_validators
    assert mock.header_validators["Authorization"] == is_valid_token


def test_with_param_validator():
    def is_numeric(val):
        return val.isdigit()

    mock = CustomAuthMock().with_param_validator("user_id", is_numeric)
    assert "user_id" in mock.param_validators
    assert mock.param_validators["user_id"] == is_numeric


# --- Test Verification Methods ---


def test_verify_headers_success_no_rules():
    mock = CustomAuthMock()
    assert mock.verify_headers({"Some-Header": "any_value"}) is True
    assert mock.get_call_count() == 1
    assert mock.get_calls()[0].method_name == "verify_headers"


def test_verify_headers_fail_required_missing():
    mock = CustomAuthMock().with_required_header("X-Mandatory")
    assert mock.verify_headers({"Other-Header": "value"}) is False
    assert mock.get_call_count() == 1
    assert mock.get_calls()[0].result is False


def test_verify_headers_fail_expected_missing():
    mock = CustomAuthMock().with_expected_header("X-Expected", "val1")
    assert mock.verify_headers({"Other-Header": "value"}) is False


def test_verify_headers_fail_expected_wrong_value():
    mock = CustomAuthMock().with_expected_header("X-Expected", "val1")
    assert mock.verify_headers({"X-Expected": "wrong_val"}) is False


def test_verify_headers_fail_validator():
    mock = CustomAuthMock().with_header_validator("Authorization", lambda v: v == "correct")
    assert mock.verify_headers({"Authorization": "incorrect"}) is False


def test_verify_headers_success_all_rules():
    mock = CustomAuthMock()
    mock.with_required_header("X-Mandatory")
    mock.with_expected_header("X-Expected", "val1")
    mock.with_header_validator("X-Validated", lambda v: len(v) > 3)

    headers = {"X-Mandatory": "present", "X-Expected": "val1", "X-Validated": "long_enough", "Other": "ignored"}
    assert mock.verify_headers(headers) is True
    assert mock.get_call_count() == 1
    assert mock.get_calls()[0].result is True


def test_verify_params_success_no_rules():
    mock = CustomAuthMock()
    assert mock.verify_params({"p": "v"}) is True
    assert mock.get_call_count() == 1
    assert mock.get_calls()[0].method_name == "verify_params"


def test_verify_params_fail_required_missing():
    mock = CustomAuthMock().with_required_param("p_mandatory")
    assert mock.verify_params({"other": "v"}) is False


def test_verify_params_fail_expected_missing():
    mock = CustomAuthMock().with_expected_param("p_expected", "v1")
    assert mock.verify_params({"other": "v"}) is False


def test_verify_params_fail_expected_wrong_value():
    mock = CustomAuthMock().with_expected_param("p_expected", "v1")
    assert mock.verify_params({"p_expected": "wrong"}) is False


def test_verify_params_fail_validator():
    mock = CustomAuthMock().with_param_validator("count", lambda v: v.isdigit())
    assert mock.verify_params({"count": "not_a_digit"}) is False


def test_verify_params_success_all_rules():
    mock = CustomAuthMock()
    mock.with_required_param("p_mandatory")
    mock.with_expected_param("p_expected", "v1")
    mock.with_param_validator("p_validated", lambda v: v == "ok")

    params = {"p_mandatory": "present", "p_expected": "v1", "p_validated": "ok", "other": "ignored"}
    assert mock.verify_params(params) is True
    assert mock.get_call_count() == 1
    assert mock.get_calls()[0].result is True


# --- Test Base Class Method Implementations ---


def test_get_auth_headers():
    """CustomAuthMock get_auth_headers should return None."""
    mock = CustomAuthMock()
    assert mock.get_auth_headers() is None


def test_handle_auth_error():
    """CustomAuthMock handle_auth_error should return False."""
    mock = CustomAuthMock()
    assert mock.handle_auth_error(None) is False  # type: ignore


def test_get_auth_strategy():
    """Test getting the underlying auth strategy."""
    mock = CustomAuthMock()
    strategy = mock.get_auth_strategy()
    assert isinstance(strategy, CustomAuth)
    # apiconfig's CustomAuth doesn't expose callbacks as public attributes

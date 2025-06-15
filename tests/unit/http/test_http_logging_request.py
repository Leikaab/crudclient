"""Unit tests for HttpLifecycleLogger request logging."""

import logging  # Add import for logging
from typing import Any, Dict
from unittest.mock import MagicMock, call, patch

import pytest
import requests
from requests.structures import CaseInsensitiveDict

# Removed unused ClientConfig import
from crudclient.http.logging import HttpLifecycleLogger
from crudclient.http.utils import redact_sensitive_headers


@pytest.fixture
def mock_prepared_request() -> MagicMock:
    """Fixture for a mocked requests.PreparedRequest."""
    request = MagicMock(spec=requests.PreparedRequest)
    request.method = "GET"
    request.url = "https://example.com/test"
    request.headers = CaseInsensitiveDict(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer secret-token",
            "X-Custom-Header": "custom-value",
            "Proxy-Authorization": "Basic encoded",
            "Cookie": "secret=cookie",
        }
    )
    # PreparedRequest body is bytes or None
    request.body = b'{"key": "value"}'
    return request


# --- Test log_request_details (Now testing HttpLifecycleLogger.log_request_details) ---


def test_log_request_details_base(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_prepared_request: MagicMock,
):
    """Verify basic request details logging (method, URL, headers)."""
    method = mock_prepared_request.method
    url = mock_prepared_request.url
    kwargs = {  # Simulate kwargs passed to requests.Session.request
        "headers": mock_prepared_request.headers,
        "params": {"q": "test"},
        "json": {"key": "value"},  # Will be ignored if log_request_body=False
    }

    http_logger.log_request_details(method, url, kwargs)

    # Check logger calls
    expected_calls = [
        call.debug("Sending request: %s %s Params: %s", method, url, kwargs["params"]),
        # Headers are logged after redaction - check the redacted string format
        call.debug("Request Headers: %s", redact_sensitive_headers(dict(mock_prepared_request.headers))),  # Use %s format
        call.debug("Request body logging is disabled."),  # Because config.log_request_body is False
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)


def test_log_request_details_no_params(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_prepared_request: MagicMock,
):
    """Verify request details logging when no params are present."""
    method = mock_prepared_request.method
    url = mock_prepared_request.url
    kwargs = {"headers": mock_prepared_request.headers}  # No params

    http_logger.log_request_details(method, url, kwargs)

    # Check logger calls - specifically the first one
    mock_logger.debug.assert_any_call("Sending request: %s %s", method, url)
    # Check others still happen
    mock_logger.debug.assert_any_call("Request Headers: %s", redact_sensitive_headers(dict(mock_prepared_request.headers)))  # Use %s format
    mock_logger.debug.assert_any_call("Request body logging is disabled.")


def test_log_request_details_with_body_enabled(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_client_config: MagicMock,  # Fixture from conftest.py
    mock_prepared_request: MagicMock,
):
    """Verify request body logging when log_request_body is True."""
    mock_client_config.log_request_body = True  # Enable body logging
    method = mock_prepared_request.method
    url = mock_prepared_request.url
    request_body_dict = {"key": "value", "password": "sensitive_data"}
    kwargs = {"headers": mock_prepared_request.headers, "json": request_body_dict}

    # Mock redact_json_body to check it's called
    with patch("crudclient.http.logging.redact_json_body", return_value={"key": "value", "password": "**REDACTED**"}) as mock_redact:
        http_logger.log_request_details(method, url, kwargs)

    mock_redact.assert_called_once_with(request_body_dict)

    # Check logger calls - body should be logged now
    expected_body_log = '{"key": "value", "password": "**REDACTED**"}'  # Result of mocked redact_json_body
    expected_calls = [
        call.debug("Sending request: %s %s", method, url),  # No params in this test
        call.debug("Request Headers: %s", redact_sensitive_headers(dict(mock_prepared_request.headers))),  # Use %s format
        call.debug(f"Request body (application/json (redacted)): {expected_body_log}"),
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)


def test_log_request_details_with_long_body_truncated(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_client_config: MagicMock,  # Fixture from conftest.py
    mock_prepared_request: MagicMock,
):
    """Verify request body truncation."""
    mock_client_config.log_request_body = True
    method = mock_prepared_request.method
    # Define a local constant for test assertion clarity, slightly larger than implementation detail
    EXPECTED_MAX_LOG_LEN = 1024
    url = mock_prepared_request.url
    long_data = "x" * (EXPECTED_MAX_LOG_LEN + 50)  # Use local constant
    request_body_dict = {"data": long_data, "token": "secret"}
    kwargs = {"headers": {"Content-Type": "application/json"}, "json": request_body_dict}  # Need content-type for json path

    # Mock redact_json_body
    with patch("crudclient.http.logging.redact_json_body", return_value={"data": long_data, "token": "**REDACTED**"}) as mock_redact:
        http_logger.log_request_details(method, url, kwargs)

    mock_redact.assert_called_once_with(request_body_dict)

    # Find the body log call
    body_log_call = None
    for call_args in mock_logger.debug.call_args_list:
        if "Request body" in call_args[0][0]:
            body_log_call = call_args
            break

    assert body_log_call is not None, "Body log call not found"
    # Log uses f-string, so the full message is the first arg
    full_log_message = body_log_call[0][0]
    assert "Request body (application/json (redacted)... (truncated)):" in full_log_message

    # Extract the snippet part after the prefix
    prefix = "Request body (application/json (redacted)... (truncated)): "
    logged_body_snippet = full_log_message[len(prefix) :]

    assert isinstance(logged_body_snippet, str)
    assert len(logged_body_snippet) <= EXPECTED_MAX_LOG_LEN  # Check it's truncated
    assert logged_body_snippet.startswith('{"data": "xxx')  # Check start after redaction/serialization
    assert "secret" not in logged_body_snippet  # Ensure original sensitive data isn't there


def test_log_request_details_with_data_kwarg(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_client_config: MagicMock,  # Fixture from conftest.py
    mock_prepared_request: MagicMock,
):
    """Verify logging when 'data' kwarg is used instead of 'json'."""
    mock_client_config.log_request_body = True
    method = mock_prepared_request.method
    url = mock_prepared_request.url
    form_data = "key1=value1&key2=value2"
    # Explicitly type kwargs to help mypy
    kwargs: Dict[str, Any] = {"headers": {"Content-Type": "application/x-www-form-urlencoded"}, "data": form_data}

    http_logger.log_request_details(method, url, kwargs)

    # Check logger calls - body should be logged as string from 'data'
    expected_calls = [
        call.debug("Sending request: %s %s", method, url),
        call.debug("Request Headers: %s", redact_sensitive_headers(kwargs["headers"])),  # Use %s format
        call.debug(f"Request body (application/x-www-form-urlencoded): {form_data}"),
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)


# --- Tests using caplog for more direct assertion ---


def test_log_request_details_header_redaction(
    mock_client_config: MagicMock,  # Use config directly
    caplog: pytest.LogCaptureFixture,
    # mock_prepared_request: MagicMock, # Not needed as we define headers directly
):
    """Verify sensitive headers are redacted in logs using caplog."""
    # Instantiate logger with a real logger for caplog
    test_logger = logging.getLogger("test_header_redaction")
    http_logger_real = HttpLifecycleLogger(config=mock_client_config, logger=test_logger)

    """Verify sensitive headers are redacted in logs using caplog."""
    caplog.set_level("DEBUG")
    method = "POST"
    url = "https://secure.com/api"
    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer super-secret-token",
        "X-API-Key": "another-secret-key",
        "Cookie": "sessionid=private; user=test",
        "Content-Type": "application/json",
        "User-Agent": "TestClient",
        "Proxy-Authorization": "Basic dXNlcjpwYXNz",  # user:pass
    }
    kwargs = {"headers": headers, "json": {"data": "payload"}}

    http_logger_real.log_request_details(method, url, kwargs)  # Use the real logger instance

    header_log_found = False
    for record in caplog.records:
        if record.levelname == "DEBUG" and record.message.startswith("Request Headers:"):
            header_log_found = True
            log_output = record.message
            # Check standard sensitive headers are redacted
            assert "'Authorization': '[REDACTED]'" in log_output
            assert "'X-API-Key': '[REDACTED]'" in log_output
            assert "'Cookie': 'sessionid=private; user=test'" in log_output
            assert "'Proxy-Authorization': '[REDACTED]'" in log_output
            # Check non-sensitive headers are present
            assert "'Accept': 'application/json'" in log_output
            assert "'Content-Type': 'application/json'" in log_output
            assert "'User-Agent': 'TestClient'" in log_output
            # Ensure original secrets are not present
            assert "super-secret-token" not in log_output
            assert "another-secret-key" not in log_output
            assert "dXNlcjpwYXNz" not in log_output
            break
    assert header_log_found, "Header log message not found"


def test_log_request_details_body_redaction_simple(
    # http_logger: HttpLifecycleLogger, # Remove fixture
    caplog: pytest.LogCaptureFixture,
    mock_client_config: MagicMock,  # Fixture from conftest.py
):
    """Verify simple sensitive keys in JSON body are redacted using caplog."""
    # Instantiate logger with a real logger for caplog
    test_logger = logging.getLogger("test_body_redaction_simple")
    http_logger_real = HttpLifecycleLogger(config=mock_client_config, logger=test_logger)

    """Verify simple sensitive keys in JSON body are redacted using caplog."""
    mock_client_config.log_request_body = True  # Enable body logging
    caplog.set_level("DEBUG")
    method = "POST"
    url = "https://secure.com/login"
    headers = {"Content-Type": "application/json"}
    body = {
        "username": "testuser",
        "password": "very_secret_password",
        "token": "auth-token-123",
        "api_key": "key-abc-456",
        "client_secret": "shhh-its-a-secret",
        "access_token": "bearer-xyz-789",
        "normal_field": "visible data",
    }
    kwargs = {"headers": headers, "json": body}

    http_logger_real.log_request_details(method, url, kwargs)  # Use the real logger instance

    body_log_found = False
    for record in caplog.records:
        if record.levelname == "DEBUG" and "Request body (application/json (redacted)):" in record.message:
            body_log_found = True
            log_output = record.message
            # Check sensitive keys are redacted
            assert '"password": "[REDACTED]"' in log_output
            assert '"token": "[REDACTED]"' in log_output
            assert '"api_key": "[REDACTED]"' in log_output
            assert '"client_secret": "[REDACTED]"' in log_output
            assert '"access_token": "[REDACTED]"' in log_output
            # Check non-sensitive keys are present
            assert '"username": "testuser"' in log_output
            assert '"normal_field": "visible data"' in log_output
            # Ensure original secrets are not present
            assert "very_secret_password" not in log_output
            assert "auth-token-123" not in log_output
            assert "key-abc-456" not in log_output
            assert "shhh-its-a-secret" not in log_output
            assert "bearer-xyz-789" not in log_output
            break
    assert body_log_found, "Request body log message not found"


def test_log_request_details_body_redaction_nested(
    # http_logger: HttpLifecycleLogger, # Remove fixture
    caplog: pytest.LogCaptureFixture,
    mock_client_config: MagicMock,  # Fixture from conftest.py
):
    """Verify nested sensitive keys in JSON body are redacted using caplog."""
    # Instantiate logger with a real logger for caplog
    test_logger = logging.getLogger("test_body_redaction_nested")
    http_logger_real = HttpLifecycleLogger(config=mock_client_config, logger=test_logger)

    """Verify nested sensitive keys in JSON body are redacted using caplog."""
    mock_client_config.log_request_body = True  # Enable body logging
    caplog.set_level("DEBUG")
    method = "PUT"
    url = "https://secure.com/config"
    headers = {"Content-Type": "application/json"}
    body = {
        "config_id": 123,
        "settings": {
            "credentials": {"username": "admin", "password": "nested_secret_password", "auth": {"token": "deeply_nested_token"}},
            "feature_flags": ["A", "B"],
            "secrets": [{"name": "db_conn", "value": "conn_string_secret"}, {"name": "api_key", "value": "another_api_key_secret"}],
        },
        "metadata": {"timestamp": "now"},
    }
    kwargs = {"headers": headers, "json": body}

    http_logger_real.log_request_details(method, url, kwargs)  # Use the real logger instance

    body_log_found = False
    for record in caplog.records:
        if record.levelname == "DEBUG" and "Request body (application/json (redacted)):" in record.message:
            body_log_found = True
            log_output = record.message
            # Check nested sensitive keys are redacted
            assert '"password": "[REDACTED]"' in log_output
            assert '"auth": "[REDACTED]"' in log_output
            assert '"secrets": "[REDACTED]"' in log_output

            # Check structure and non-sensitive data remains
            assert '"config_id": 123' in log_output
            assert '"username": "admin"' in log_output
            assert '"feature_flags": ["A", "B"]' in log_output
            assert '"timestamp": "now"' in log_output

            # Ensure original secrets are not present
            assert "nested_secret_password" not in log_output
            assert "deeply_nested_token" not in log_output
            assert "another_api_key_secret" not in log_output
            break
    assert body_log_found, "Request body log message not found"

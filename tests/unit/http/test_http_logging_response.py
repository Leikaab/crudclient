"""Unit tests for HttpLifecycleLogger response logging."""

import json as json_lib
from unittest.mock import MagicMock, call, patch

import pytest
import requests
from requests.structures import CaseInsensitiveDict

# Removed unused ClientConfig import
from crudclient.http.logging import HttpLifecycleLogger
from crudclient.http.utils import redact_sensitive_headers


@pytest.fixture
def mock_prepared_request() -> MagicMock:
    """Fixture for a mocked requests.PreparedRequest (needed by mock_response)."""
    request = MagicMock(spec=requests.PreparedRequest)
    request.method = "GET"
    request.url = "https://example.com/test"
    # Add minimal headers if needed by response tests
    request.headers = CaseInsensitiveDict({"Accept": "application/json"})
    return request


@pytest.fixture
def mock_response(mock_prepared_request: MagicMock) -> MagicMock:
    """Fixture for a mocked requests.Response."""
    response = MagicMock(spec=requests.Response)
    response.request = mock_prepared_request  # Link prepared request
    response.status_code = 200
    response.reason = "OK"
    response.url = mock_prepared_request.url  # Usually same as request url
    response.headers = CaseInsensitiveDict(
        {
            "Content-Type": "application/json",
            "Content-Length": "25",
            "Server": "test-server",
            "Set-Cookie": "sessionid=abc; HttpOnly",
            "X-Sensitive-Info": "very-secret",
        }
    )
    # Use _content for bytes, text property will decode it
    response._content = b'{"result": "success"}'
    response.elapsed = MagicMock()
    response.elapsed.total_seconds.return_value = 0.555  # Example duration

    # Mock text property to return decoded content
    response.text = response._content.decode("utf-8")

    # Mock json() method
    def mock_json():
        return json_lib.loads(response.text)

    response.json = mock_json

    # Mock raise_for_status
    response.raise_for_status = MagicMock()
    response.ok = True  # Based on status_code 200

    return response


# --- Test log_response_details (Now testing HttpLifecycleLogger.log_response_details) ---


def test_log_response_details_base(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_response: MagicMock,
) -> None:
    """Verify basic response details logging (status, headers)."""
    method = mock_response.request.method
    url = mock_response.request.url

    http_logger.log_response_details(method, url, mock_response)

    # Check logger calls
    expected_calls = [
        call.debug("Received response for %s %s: Status %d", method, url, mock_response.status_code),
        call.debug("Response Headers: %s", redact_sensitive_headers(dict(mock_response.headers))),  # Use %s format
        call.debug("Response body logging is disabled."),  # Default config
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)


def test_log_response_details_error_status(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_response: MagicMock,
) -> None:
    """Verify warning/error logging for non-2xx status codes."""
    method = mock_response.request.method
    url = mock_response.request.url

    # Test 4xx
    mock_response.status_code = 403
    mock_response.reason = "Forbidden"
    http_logger.log_response_details(method, url, mock_response)
    mock_logger.warning.assert_any_call("Authentication failed for %s %s: Status %d", method, url, 403)

    mock_logger.reset_mock()  # Reset for next check

    # Test 5xx
    mock_response.status_code = 500
    mock_response.reason = "Server Error"
    http_logger.log_response_details(method, url, mock_response)
    mock_logger.error.assert_any_call("Server error for %s %s: Status %d", method, url, 500)


# Add newline to fix E704
def test_log_response_details_with_body_enabled(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_client_config: MagicMock,  # Fixture from conftest.py
    mock_response: MagicMock,
) -> None:
    """Verify response body logging when log_response_body is True."""
    mock_client_config.log_response_body = True  # Enable body logging
    method = mock_response.request.method
    url = mock_response.request.url
    response_body_dict = {"result": "success", "session_token": "sensitive"}

    # Adjust mock response content and mock json()
    mock_response._content = json_lib.dumps(response_body_dict).encode("utf-8")
    mock_response.text = mock_response._content.decode("utf-8")
    mock_response.headers["Content-Type"] = "application/json"

    def mock_json():
        return response_body_dict  # noqa: E704 (ignore flake8 error for this line)

    mock_response.json = mock_json

    # Mock redact_json_body
    with patch("crudclient.http.logging.redact_json_body", return_value={"result": "success", "session_token": "**REDACTED**"}) as mock_redact:
        http_logger.log_response_details(method, url, mock_response)

    mock_redact.assert_called_once_with(response_body_dict)

    # Check logger calls - body should be logged now
    expected_body_log = '{"result": "success", "session_token": "**REDACTED**"}'
    expected_calls = [
        call.debug("Received response for %s %s: Status %d", method, url, mock_response.status_code),
        call.debug("Response Headers: %s", redact_sensitive_headers(dict(mock_response.headers))),  # Use %s format
        call.debug(f"Response body (application/json (redacted)): {expected_body_log}"),
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)


# Add newline to fix E704
def test_log_response_details_with_long_body_truncated(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_client_config: MagicMock,  # Fixture from conftest.py
    mock_response: MagicMock,
) -> None:
    """Verify response body truncation."""
    mock_client_config.log_response_body = True
    method = mock_response.request.method
    # Define a local constant for test assertion clarity
    EXPECTED_MAX_LOG_LEN = 1024
    url = mock_response.request.url
    long_data = "y" * (EXPECTED_MAX_LOG_LEN + 60)  # Use local constant
    response_body_dict = {"data": long_data, "user_id": 123}

    # Adjust mock response content and mock json()
    mock_response._content = json_lib.dumps(response_body_dict).encode("utf-8")
    mock_response.text = mock_response._content.decode("utf-8")
    mock_response.headers["Content-Type"] = "application/json"

    def mock_json():
        return response_body_dict  # noqa: E704 (ignore flake8 error for this line)

    mock_response.json = mock_json

    # Mock redact_json_body
    with patch("crudclient.http.logging.redact_json_body", return_value={"data": long_data, "user_id": 123}) as mock_redact:
        http_logger.log_response_details(method, url, mock_response)

    mock_redact.assert_called_once_with(response_body_dict)

    # Find the body log call
    body_log_call = None
    for call_args in mock_logger.debug.call_args_list:
        if "Response body" in call_args[0][0]:
            body_log_call = call_args
            break

    assert body_log_call is not None, "Body log call not found"
    # Log uses f-string, so the full message is the first arg
    full_log_message = body_log_call[0][0]
    assert "Response body (application/json (redacted)... (truncated)):" in full_log_message

    # Extract the snippet part after the prefix
    prefix = "Response body (application/json (redacted)... (truncated)): "
    logged_body_snippet = full_log_message[len(prefix) :]

    assert isinstance(logged_body_snippet, str)
    assert len(logged_body_snippet) <= EXPECTED_MAX_LOG_LEN  # Check it's truncated
    assert logged_body_snippet.startswith('{"data": "yyy')


def test_log_response_details_non_json_body(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_client_config: MagicMock,  # Fixture from conftest.py
    mock_response: MagicMock,
) -> None:
    """Verify logging for non-JSON response bodies."""
    mock_client_config.log_response_body = True
    method = mock_response.request.method
    url = mock_response.request.url
    html_content = "<html><body><h1>Hello</h1></body></html>"

    mock_response._content = html_content.encode("utf-8")
    mock_response.text = html_content
    mock_response.headers["Content-Type"] = "text/html; charset=utf-8"
    # Remove json mock as it would fail
    del mock_response.json

    http_logger.log_response_details(method, url, mock_response)

    # Check logger calls - body logged directly as text
    expected_calls = [
        call.debug("Received response for %s %s: Status %d", method, url, mock_response.status_code),
        call.debug("Response Headers: %s", redact_sensitive_headers(dict(mock_response.headers))),  # Use %s format
        call.debug(f"Response body (text/html; charset=utf-8): {html_content}"),
    ]
    mock_logger.assert_has_calls(expected_calls, any_order=False)

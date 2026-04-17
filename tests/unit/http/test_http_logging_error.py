"""Unit tests for HttpLifecycleLogger HTTP error logging."""

import json as json_lib
import logging
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests
from requests.structures import CaseInsensitiveDict

# Assuming ClientConfig is the correct import based on logging.py
from crudclient.http.logging import HttpLifecycleLogger


@pytest.fixture
def mock_prepared_request() -> MagicMock:
    """Fixture for a mocked requests.PreparedRequest."""
    request = MagicMock(spec=requests.PreparedRequest)
    request.method = "GET"
    request.url = "https://example.com/error"
    request.headers = CaseInsensitiveDict({"Accept": "application/json"})
    return request


@pytest.fixture
def mock_response(mock_prepared_request: MagicMock) -> MagicMock:
    """Fixture for a mocked requests.Response."""
    response = MagicMock(spec=requests.Response)
    response.request = mock_prepared_request
    response.status_code = 404  # Default to an error status for these tests
    response.reason = "Not Found"
    response.url = mock_prepared_request.url
    response.headers = CaseInsensitiveDict({"Content-Type": "application/json"})
    response._content = b'{"error": "Resource not found"}'
    response.elapsed = MagicMock()
    response.elapsed.total_seconds.return_value = 0.1
    response.text = response._content.decode("utf-8")

    def mock_json() -> Any:
        return json_lib.loads(response.text)  # noqa: E704

    response.json = mock_json
    # Simulate raise_for_status behavior for HTTPError
    response.raise_for_status = MagicMock(side_effect=requests.exceptions.HTTPError(response=response))
    response.ok = False
    return response


# --- Test log_http_error (Now testing HttpLifecycleLogger.log_http_error) ---


# Ensure newline before def
def test_log_http_error_4xx(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_response: MagicMock,  # Response attached to exception
) -> None:
    """Verify HTTPError logging for 4xx status codes."""
    # Ensure response has the correct attributes for this test
    mock_response.status_code = 404
    mock_response.reason = "Not Found"
    mock_response._content = b'{"error": "Resource not found"}'
    mock_response.text = mock_response._content.decode("utf-8")
    mock_response.request = MagicMock(spec=requests.PreparedRequest, method="GET", url="https://example.com/missing")

    error = requests.exceptions.HTTPError(response=mock_response)

    http_logger.log_http_error(error)

    expected_snippet = '{"error": "Resource not found"}'
    mock_logger.log.assert_called_once_with(
        logging.WARNING,  # Level for 4xx
        "HTTP error encountered for %s %s: Status %d - Response: %s",
        "GET",
        "https://example.com/missing",
        404,
        expected_snippet,
    )


def test_log_http_error_5xx(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_response: MagicMock,
) -> None:
    """Verify HTTPError logging for 5xx status codes."""
    # Ensure response has the correct attributes for this test
    mock_response.status_code = 503
    mock_response.reason = "Service Unavailable"
    mock_response._content = b"Service down for maintenance"
    mock_response.text = mock_response._content.decode("utf-8")
    mock_response.request = MagicMock(spec=requests.PreparedRequest, method="POST", url="https://example.com/api")

    error = requests.exceptions.HTTPError(response=mock_response)

    http_logger.log_http_error(error)

    expected_snippet = "Service down for maintenance"
    mock_logger.log.assert_called_once_with(
        logging.ERROR,  # Level for 5xx
        "HTTP error encountered for %s %s: Status %d - Response: %s",
        "POST",
        "https://example.com/api",
        503,
        expected_snippet,
    )


def test_log_http_error_no_response(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
) -> None:
    """Verify HTTPError logging when the error has no response object."""
    request = MagicMock(spec=requests.PreparedRequest, method="PUT", url="https://example.com/update")
    error = requests.exceptions.HTTPError("Some connection issue", request=request, response=None)

    http_logger.log_http_error(error)

    mock_logger.error.assert_called_once_with(
        "HTTPError occurred without a response object for %s %s: %s", "PUT", "https://example.com/update", error
    )


def test_log_http_error_no_request_or_response(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
) -> None:
    """Verify HTTPError logging when the error has no request or response."""
    error = requests.exceptions.HTTPError("Very early error")
    error.request = None  # Explicitly set to None
    error.response = None

    # Call with explicit method/url fallback
    http_logger.log_http_error(error, method="PATCH", url="https://fallback.com/data")

    mock_logger.error.assert_called_once_with(
        "HTTPError occurred without a response object for %s %s: %s", "PATCH", "https://fallback.com/data", error  # Uses the provided method/url
    )

    mock_logger.reset_mock()

    # Call without explicit method/url fallback
    http_logger.log_http_error(error)

    mock_logger.error.assert_called_once_with(
        "HTTPError occurred without a response object for %s %s: %s", "UNKNOWN_METHOD", "UNKNOWN_URL", error  # Uses the defaults
    )

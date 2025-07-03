"""Unit tests for HttpLifecycleLogger request completion logging."""

import json as json_lib
from typing import Any
from unittest.mock import MagicMock

import pytest
import requests
from requests.structures import CaseInsensitiveDict

# Removed unused ClientConfig import
from crudclient.http.logging import HttpLifecycleLogger


@pytest.fixture
def mock_prepared_request() -> MagicMock:
    """Fixture for a mocked requests.PreparedRequest."""
    request = MagicMock(spec=requests.PreparedRequest)
    request.method = "GET"
    request.url = "https://example.com/completion"
    request.headers = CaseInsensitiveDict({"Accept": "application/json"})
    return request


@pytest.fixture
def mock_response(mock_prepared_request: MagicMock) -> MagicMock:
    """Fixture for a mocked requests.Response."""
    response = MagicMock(spec=requests.Response)
    response.request = mock_prepared_request
    response.status_code = 200
    response.reason = "OK"
    response.url = mock_prepared_request.url
    response.headers = CaseInsensitiveDict({"Content-Type": "application/json"})
    response._content = b'{"status": "done"}'
    response.elapsed = MagicMock()
    response.elapsed.total_seconds.return_value = 0.555
    response.text = response._content.decode("utf-8")

    def mock_json() -> Any:
        return json_lib.loads(response.text)  # noqa: E704

    response.json = mock_json
    response.raise_for_status = MagicMock()
    response.ok = True
    return response


# --- Test log_request_completion (Now testing HttpLifecycleLogger.log_request_completion) ---


# Ensure newline before def
def test_log_request_completion_success(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_response: MagicMock,
    patch_time: MagicMock,  # Explicitly request fixture
) -> None:
    """Verify successful request completion logging."""
    # patch_time provides start_time=100.0, end_time=100.555
    start_time = 100.0  # Matches patch_time.side_effect[0]
    method = mock_response.request.method
    url = mock_response.request.url
    attempt_count = 1
    final_outcome = mock_response  # Successful response

    http_logger.log_request_completion(start_time, method, url, attempt_count, final_outcome)

    duration_ms = 555  # Calculated from patch_time side_effect
    mock_logger.info.assert_called_once_with(
        "Request %s %s completed successfully: %d %s in %dms.", method, url, mock_response.status_code, mock_response.reason, duration_ms
    )


def test_log_request_completion_failure_response(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_response: MagicMock,
    patch_time: MagicMock,  # Explicitly request fixture
) -> None:
    """Verify failed request completion logging (with error response)."""
    # patch_time provides start_time=100.0, end_time=100.555
    start_time = 100.0  # Matches patch_time.side_effect[0]
    method = mock_response.request.method
    url = mock_response.request.url
    attempt_count = 3
    mock_response.status_code = 500
    mock_response.reason = "Server Error"
    mock_response.ok = False  # Update ok status
    final_outcome = mock_response  # Failed response

    http_logger.log_request_completion(start_time, method, url, attempt_count, final_outcome)

    duration_ms = 555
    mock_logger.info.assert_called_once_with(
        "Request %s %s failed after %d attempts: %d %s in %dms.",
        method,
        url,
        attempt_count,
        mock_response.status_code,
        mock_response.reason,
        duration_ms,
    )


def test_log_request_completion_failure_exception(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_prepared_request: MagicMock,  # Need request info for the log
    patch_time: MagicMock,  # Explicitly request fixture
) -> None:
    """Verify failed request completion logging (with exception)."""
    # patch_time provides start_time=100.0, end_time=100.555
    start_time = 100.0  # Matches patch_time.side_effect[0]
    method = mock_prepared_request.method
    url = mock_prepared_request.url
    attempt_count = 2
    final_outcome = requests.exceptions.Timeout("Connection timed out")  # Example exception

    http_logger.log_request_completion(start_time, method, url, attempt_count, final_outcome)

    duration_ms = 555
    mock_logger.info.assert_called_once_with(
        "Request %s %s failed after %d attempts: %s in %dms.", method, url, attempt_count, "Timeout", duration_ms  # Exception type name
    )


def test_log_request_completion_no_outcome(
    http_logger: HttpLifecycleLogger,
    mock_logger: MagicMock,
    mock_prepared_request: MagicMock,
    patch_time: MagicMock,  # Explicitly request fixture
) -> None:
    """Verify request completion logging when outcome is None."""
    # patch_time provides start_time=100.0, end_time=100.555
    start_time = 100.0  # Matches patch_time.side_effect[0]
    method = mock_prepared_request.method
    url = mock_prepared_request.url
    attempt_count = 1
    final_outcome = None  # No outcome

    http_logger.log_request_completion(start_time, method, url, attempt_count, final_outcome)

    duration_ms = 555
    mock_logger.warning.assert_called_once_with("Request %s %s completed with no outcome recorded in %dms.", method, url, duration_ms)

"""Shared fixtures for HTTP logging tests."""

import logging
from typing import Iterator  # Add explicit import for Iterator
from unittest.mock import MagicMock

import pytest

# Assuming ClientConfig is the correct import based on logging.py
# If this fails, we'll need to find the correct location.
from crudclient.http.client import HttpClient
from crudclient.http.errors import ErrorHandler
from crudclient.http.logging import HttpLifecycleLogger
from crudclient.http.request import RequestFormatter
from crudclient.http.response import ResponseHandler
from crudclient.http.retry import RetryHandler


@pytest.fixture
def mock_logger() -> MagicMock:
    """Fixture for a mocked logging.Logger."""
    return MagicMock(spec=logging.Logger)


# mock_client_config fixture moved to tests/unit/conftest.py


@pytest.fixture
def http_logger(mock_client_config: MagicMock, mock_logger: MagicMock) -> HttpLifecycleLogger:  # Updated dependency name
    """Fixture for the HttpLifecycleLogger instance."""
    return HttpLifecycleLogger(config=mock_client_config, logger=mock_logger)


@pytest.fixture()
def patch_time(mocker):
    """Patch time.monotonic to control duration calculations."""
    mock_time = mocker.patch("time.monotonic")
    # Provide the value for the end_time call inside log_request_completion
    mock_time.return_value = 100.555  # end_time (start_time is passed directly in tests)
    return mock_time


# --- Added Fixtures ---


@pytest.fixture
def retry_handler() -> RetryHandler:
    """Fixture for a real RetryHandler instance."""
    return RetryHandler()


# Removed mock_session_manager fixture


@pytest.fixture
def http_client(
    mock_client_config: MagicMock,
    # mock_logger: MagicMock, # Removed, HttpClient creates its own logger instance
    retry_handler: MagicMock,  # Keep mocked retry_handler
) -> Iterator[HttpClient]:
    """Fixture for a real HttpClient with some mocked dependencies."""
    # Instantiate real components with mocks where appropriate
    request_formatter = RequestFormatter(config=mock_client_config)
    response_handler = ResponseHandler()
    error_handler = ErrorHandler()
    # retry_handler is mocked via fixture

    # Let HttpClient create its own SessionManager using the mock_client_config
    client = HttpClient(
        config=mock_client_config,
        # session_manager=None, # Default uses config
        request_formatter=request_formatter,
        response_handler=response_handler,
        error_handler=error_handler,
        retry_handler=retry_handler,
    )
    # Ensure the client is closed after the test to clean up the session
    yield client
    client.close()


@pytest.fixture
def error_handler() -> ErrorHandler:
    """Fixture for a real ErrorHandler instance."""
    return ErrorHandler()

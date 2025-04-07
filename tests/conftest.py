"""
Global fixtures for both unit and integration tests.
"""

import pytest
import os
import time
import json
from unittest.mock import Mock
from contextlib import contextmanager
from pathlib import Path
# Consider adding 'import xml.etree.ElementTree as ET' if XML parsing/mocking is needed


@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for API tests."""
    return "https://api.example.com"


@pytest.fixture
def mock_response_factory():
    """
    Factory fixture to create mock response objects with custom attributes.

    Usage:
        mock_resp = mock_response_factory(status_code=201, json_data={'id': 123})
        mock_resp_text = mock_response_factory(status_code=200, text_data='Success')
        mock_resp_error = mock_response_factory(status_code=404, reason='Not Found')
    """
    def _create_mock_response(
        status_code=200,
        json_data=None,
        text_data=None,  # Default to None
        headers=None,
        reason=None,
        url=None,
        content=None  # Add content for raw bytes
    ):
        mock = Mock()
        mock.status_code = status_code
        mock.reason = reason
        mock.url = url
        mock.headers = headers if headers is not None else {"Content-Type": "application/json"}  # Sensible default

        # Determine content type from headers
        content_type = mock.headers.get("Content-Type", "").lower()

        # Handle JSON data
        if json_data is not None:
            mock.json.return_value = json_data
            # If text_data not explicitly set, derive from json_data
            if text_data is None:
                text_data = json.dumps(json_data)
        else:
            # Make .json() raise an error if no json_data and content type isn't json
            if "application/json" not in content_type:
                mock.json.side_effect = json.JSONDecodeError("No JSON object could be decoded", "", 0)
            else:
                # If content type is JSON but no data, simulate empty body error
                mock.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)

        # Handle text data (set text_data to empty string if None and not derived from JSON)
        mock.text = text_data if text_data is not None else ""

        # Set content (bytes) based on text_data if not provided directly
        mock.content = content if content is not None else mock.text.encode('utf-8')

        # Add raise_for_status mock
        def raise_for_status():
            if 400 <= mock.status_code < 600:
                # Using a generic exception for simplicity, replace with requests.exceptions.HTTPError if needed
                error_msg = f"Mock HTTP Error: {mock.status_code} {mock.reason or 'Error'}"
                if mock.url:
                    error_msg += f" for url: {mock.url}"
                raise Exception(error_msg)
        mock.raise_for_status = Mock(side_effect=raise_for_status)

        return mock

    return _create_mock_response


@pytest.fixture(params=["json", "xml", "text"])
def api_response_type(request):
    """Parametrized fixture for different API response content types."""
    return request.param


@pytest.fixture
def temp_file(tmp_path):
    """
    Provides a pathlib.Path object for a temporary file within the test's temp directory.
    The file is created empty. Cleanup is handled automatically by pytest.

    Usage:
        def test_something(temp_file):
            temp_file.write_text("Hello")
            assert temp_file.read_text() == "Hello"
    """
    file_path = tmp_path / "test_temp_file.dat"
    file_path.touch()  # Create the file
    return file_path


@pytest.fixture
def manage_env_vars(monkeypatch):
    """
    Fixture providing functions to safely set/unset environment variables
    during a test, automatically restoring the original state afterwards.

    Usage:
        def test_with_env(manage_env_vars):
            set_var, del_var = manage_env_vars
            set_var('MY_API_KEY', '12345')
            # ... test logic ...
            del_var('MY_API_KEY') # Optional: explicitly delete if needed before test end
    """
    def _set_var(key, value):
        monkeypatch.setenv(key, str(value))  # Ensure value is string

    def _del_var(key, raising=False):
        # raising=False: don't error if var doesn't exist
        monkeypatch.delenv(key, raising=raising)

    return _set_var, _del_var


class ExecutionTimer:
    """Helper class for the timer fixture."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = None

    @contextmanager
    def measure(self):
        """Context manager to measure execution time."""
        self.start_time = time.perf_counter()
        yield
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        # You could add logging here if desired
        # print(f"\n[Timer] Duration: {self.duration:.4f}s")


@pytest.fixture
def timer():
    """
    Fixture providing a context manager to measure execution time.

    Usage:
        def test_performance(timer):
            with timer.measure():
                # code to time
            assert timer.duration < 1.0 # Example assertion
            print(f"Measured time: {timer.duration:.4f}s")
    """
    return ExecutionTimer()


# Keep existing xdist scheduler configuration
def pytest_xdist_make_scheduler(config, log):
    """Custom scheduler for pytest-xdist to handle 'no_parallel' marker."""
    # Ensure xdist is installed or handle ImportError
    try:
        from xdist.scheduler import LoadScheduling
    except ImportError:
        # If xdist is not installed, don't attempt to customize scheduling
        return None  # Or potentially raise a warning/error if xdist is expected

    class CustomScheduling(LoadScheduling):
        def _split_scope(self, nodeid):
            # This logic might need refinement based on how markers are accessed
            # during scheduling in your specific pytest/xdist version.
            # A common way is to access markers via the collected items.
            # This simplified check looks for the marker name in the node ID string.
            if "[no_parallel]" in nodeid or "::no_parallel" in nodeid:  # Adjust marker check as needed
                # Group tests marked with no_parallel to run sequentially on one worker
                return "no_parallel_group"

            # Fallback to default scheduling logic
            # Explicitly specify the class and instance for super() to help type checkers
            return super(CustomScheduling, self)._split_scope(nodeid)  # type: ignore[attr-defined]

        # Note: The original code had a complex way to access markers via config.hook.
        # Accessing markers directly from nodeid or collected items is usually preferred.
        # If the simple string check above doesn't work, you might need to investigate
        # how to access item markers reliably within the scheduler context.

    return CustomScheduling(config, log)

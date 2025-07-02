"""
Global fixtures for both unit and integration tests.
"""

import json
import time
from contextlib import contextmanager

# Removed incorrect imports for internal types: LogCaptureHandler, Config
from typing import (  # Ensure List and Type are imported
    Any,
    Callable,
    List,
    Optional,
)
from unittest.mock import Mock

import pytest
from pytest import Item  # Added import
from xdist.scheduler import LoadScheduling  # Moved import to top level

# Consider adding 'import xml.etree.ElementTree as ET' if XML parsing/mocking is needed

pytest_plugins = ["tests.unit.fixtures.mock_clients"]


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for API tests."""
    return "https://api.example.com"


@pytest.fixture
def mock_response_factory() -> Callable[..., Mock]:
    """
    Factory fixture to create mock response objects with custom attributes.

    Usage:
        mock_resp = mock_response_factory(status_code=201, json_data={'id': 123})
        mock_resp_text = mock_response_factory(status_code=200, text_data='Success')
        mock_resp_error = mock_response_factory(status_code=404, reason='Not Found')
    """

    def _create_mock_response(
        status_code: int = 200,
        json_data: Any = None,
        text_data: Optional[str] = None,  # Default to None
        headers: Optional[dict] = None,
        reason: Optional[str] = None,
        url: Optional[str] = None,
        content: Optional[bytes] = None,  # Add content for raw bytes
    ) -> Mock:
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
        mock.content = content if content is not None else mock.text.encode("utf-8")

        # Add raise_for_status mock
        def raise_for_status() -> None:
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
def api_response_type(request: Any) -> Any:
    """Parametrized fixture for different API response content types."""
    return request.param


@pytest.fixture
def temp_file(tmp_path: Any) -> Any:
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
def manage_env_vars(monkeypatch: Any) -> tuple[Callable[[str, Any], None], Callable[[str, bool], None]]:
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

    def _set_var(key: str, value: Any) -> None:
        monkeypatch.setenv(key, str(value))  # Ensure value is string

    def _del_var(key: str, raising: bool = False) -> None:
        # raising=False: don't error if var doesn't exist
        monkeypatch.delenv(key, raising=raising)

    return _set_var, _del_var


class ExecutionTimer:
    """Helper class for the timer fixture."""

    def __init__(self) -> None:
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None

    @contextmanager
    def measure(self) -> Any:
        """Context manager to measure execution time."""
        self.start_time = time.perf_counter()
        yield
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        # You could add logging here if desired
        # print(f"\n[Timer] Duration: {self.duration:.4f}s")


@pytest.fixture
def timer() -> ExecutionTimer:
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


# TYPE_CHECKING block is no longer strictly necessary for LoadScheduling,
# but keep Mark for type hints if used elsewhere or for clarity.
# Keep existing xdist scheduler configuration
# --- Custom xdist Scheduler ---

# Use Any for config and log types for robustness against internal API changes
# Cache items by nodeid during collection
# Use Any for config and items types for robustness against internal API changes


def pytest_collection_modifyitems(session: Any, config: Any, items: List[Item]) -> None:
    """
    Hook to modify the list of collected items.
    We use it to cache items by their nodeid on the config object.
    """
    config._nodeid_to_item = {item.nodeid: item for item in items}
    # Optional: Log the number of items cached
    # log = logging.getLogger(__name__)
    # log.debug(f"Cached {len(config._nodeid_to_item)} items by nodeid.")


# Define the custom scheduler class at the module level
class CustomScheduling(LoadScheduling):
    """
    Custom xdist scheduler that groups tests marked with '@pytest.mark.no_parallel'
    onto a single worker node for sequential execution, while distributing
    other tests normally using file-based scoping.
    """

    # Store config for later access in _split_scope
    # Use Any for config and log types for robustness against internal API changes
    def __init__(self, config: Any, log: Any):
        super().__init__(config, log)
        self.config = config  # Store config instance
        # Removed collection processing from __init__ as collection is not ready yet

    def _split_scope(self, nodeid: str) -> str:
        """Determine scheduling scope based on 'no_parallel' marker."""
        # Retrieve the item from the cache created by pytest_collection_modifyitems
        # Ensure the cache exists before trying to access it
        item = getattr(self.config, "_nodeid_to_item", {}).get(nodeid)

        # Check if the item exists and has the 'no_parallel' marker
        if item and item.get_closest_marker("no_parallel"):
            # Assign to a dedicated scope for sequential execution
            return "no_parallel_group"

        # Fallback to default file-based scheduling logic if no 'no_parallel' marker.
        # Replicating default LoadScheduling behavior (scoping by file)
        # by extracting the file path from the nodeid.
        # This avoids the super() call that Pylance struggles with.
        return nodeid.split("::")[0]


# Scheduler factory function
# Use Any for config and log types for robustness against internal API changes


def pytest_xdist_make_scheduler(config: Any, log: Any) -> Optional[LoadScheduling]:
    """Custom scheduler for pytest-xdist to handle 'no_parallel' marker."""
    # Ensure xdist is installed or handle ImportError
    # Check if LoadScheduling was successfully imported (i.e., xdist is installed)
    # The import is now at the top level, but we still need to handle missing xdist.
    # We can check if the name 'LoadScheduling' exists in globals.
    if "LoadScheduling" not in globals():
        # If xdist is not installed, don't attempt to customize scheduling
        # log object type and methods are not guaranteed, removed logging call
        return None

    # Instantiate and return the custom scheduler (now defined at top level)
    return CustomScheduling(config, log)

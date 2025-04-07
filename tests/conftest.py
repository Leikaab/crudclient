"""
Global fixtures for both unit and integration tests.
"""

import pytest
from unittest.mock import Mock


@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for API tests."""
    return "https://api.example.com"


@pytest.fixture
def mock_response():
    """Create a mock response object with common attributes."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"status": "success"}
    return mock


# Add this to the end of tests/conftest.py
def pytest_xdist_make_scheduler(config, log):
    from xdist.scheduler import LoadScheduling

    class CustomScheduling(LoadScheduling):
        def _split_scope(self, nodeid):
            # Check if the marker is directly in the nodeid string
            # This might need adjustment based on how markers are represented in nodeids
            if "no_parallel" in nodeid:
                # Group tests marked with no_parallel to run sequentially on one worker
                return "no_parallel_group"
            # Check node markers more reliably
            node = config.hook.pytest_collection_finish(session=config.session)  # This is illustrative, need actual node access
            if node and node.get_closest_marker("no_parallel"):
                return "no_parallel_group"

            return super()._split_scope(nodeid)

    return CustomScheduling(config, log)

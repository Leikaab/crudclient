"""
Simplified integration test for rate limiting in HttpClient.
"""

import os
import tempfile
import time
from unittest.mock import Mock, patch

import pytest
import requests

from crudclient.config import ClientConfig
from crudclient.http.client import HttpClient
from crudclient.ratelimit import get_rate_limiter


class TestHttpClientRateLimitingSimple:
    """Test that HttpClient properly integrates with the rate limiter."""

    def test_rate_limiter_called_before_request(self) -> None:
        """Test that the rate limiter check_and_wait is called before making requests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with rate limiting enabled
            config = ClientConfig(hostname="https://api.example.com")
            config.enable_rate_limiter(state_path=temp_dir)

            # Create a rate limiter instance
            rate_limiter = get_rate_limiter(config)
            assert rate_limiter is not None

            # Mock the rate limiter methods
            with (
                patch.object(rate_limiter, "check_and_wait") as mock_check_and_wait,
                patch.object(rate_limiter, "update_from_headers") as mock_update,
            ):

                # Create HttpClient with mocked session
                with patch("crudclient.http.client.SessionManager") as MockSessionManager:
                    mock_session_manager = Mock()
                    mock_session = Mock()
                    mock_session_manager.session = mock_session
                    mock_session_manager.timeout = 30
                    MockSessionManager.return_value = mock_session_manager

                    # Mock response
                    mock_response = Mock(spec=requests.Response)
                    mock_response.status_code = 200
                    mock_response.headers = {"X-Rate-Limit-Remaining": "42", "X-Rate-Limit-Reset": "3600"}
                    mock_response.json.return_value = {"result": "success"}
                    mock_session.request.return_value = mock_response

                    # Patch get_rate_limiter to return our mocked rate limiter
                    with patch("crudclient.http.client.get_rate_limiter", return_value=rate_limiter):
                        client = HttpClient(config)

                        # Make a request
                        client.get("/test")

                        # Verify rate limiter was called
                        mock_check_and_wait.assert_called_once()
                        mock_update.assert_called_once_with(mock_response.headers)

    def test_rate_limiting_blocks_requests(self) -> None:
        """Test that rate limiting actually blocks requests when limit is reached."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set worker count to avoid pytest-xdist interference
            os.environ["CRUDCLIENT_WORKERS"] = "1"

            # Create config with rate limiting enabled
            config = ClientConfig(hostname="https://api.example.com")
            config.enable_rate_limiter(state_path=temp_dir, buffer=1, buffer_time=0.1)

            # Initialize state file with low remaining count
            # Create rate limiter to get the correct state file path
            rate_limiter = get_rate_limiter(config)
            assert rate_limiter is not None

            # Set initial state to force blocking - use shorter reset time
            # With 1 worker + 1 buffer = threshold of 2
            # So setting remaining=3 means first request succeeds, second succeeds, third blocks
            with rate_limiter.backend:
                rate_limiter.backend.write({"remaining": 3, "reset_ts": time.time() + 0.1})  # Further reduced to 0.1s

            # Create HttpClient with mocked session
            with patch("crudclient.http.client.SessionManager") as MockSessionManager:
                mock_session_manager = Mock()
                mock_session = Mock()
                mock_session_manager.session = mock_session
                mock_session_manager.timeout = 30
                MockSessionManager.return_value = mock_session_manager

                # Mock response
                mock_response = Mock(spec=requests.Response)
                mock_response.status_code = 200
                mock_response.headers = {"X-Rate-Limit-Remaining": "1", "X-Rate-Limit-Reset": "1"}  # Reduced from 3s
                mock_response.json.return_value = {"result": "success"}
                mock_session.request.return_value = mock_response

                # Don't patch get_rate_limiter, let it use the real one
                client = HttpClient(config)

                # First request should succeed immediately
                start_time = time.time()
                client.get("/test1")
                elapsed = time.time() - start_time
                assert elapsed < 0.5, f"First request took too long: {elapsed}s"

                # Update headers to show we're at the limit
                mock_response.headers = {"X-Rate-Limit-Remaining": "0", "X-Rate-Limit-Reset": "1"}  # Reduced from 3s

                # Second request should also succeed (remaining=1)
                client.get("/test2")

                # Third request should be blocked (threshold = 1 + 1 buffer = 2)
                start_time = time.time()
                client.get("/test3")
                elapsed = time.time() - start_time
                assert elapsed >= 0.05, f"Third request should have waited ~0.1s, but only waited {elapsed}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

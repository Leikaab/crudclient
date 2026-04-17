"""
Simple unit tests for rate limiter to verify basic functionality.
"""

import tempfile
import time
import warnings

import pytest

from crudclient.config import ClientConfig
from crudclient.ratelimit import get_rate_limiter


class TestRateLimiterSimple:
    """Simple tests for rate limiter functionality."""

    def test_basic_rate_limiting(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that rate limiter blocks when limit is reached."""
        # Override worker detection to get predictable behavior
        monkeypatch.setenv("CRUDCLIENT_WORKERS", "1")

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with rate limiting
            config = ClientConfig(hostname="test.api")
            config.enable_rate_limiter(state_path=temp_dir, buffer=2)
            limiter = get_rate_limiter(config)
            assert limiter is not None, "Rate limiter should be created"

            # Set initial rate limit state
            limiter.update_from_headers({"X-Rate-Limit-Remaining": "5", "X-Rate-Limit-Reset": "10"})  # 10 seconds from now

            # Make requests until we hit the threshold
            # With buffer=2 and 1 worker, threshold = 1 + 2 = 3
            # So we should be able to make 2 requests (5 remaining > 3 threshold)
            # Then wait when remaining = 3

            # Track calls to time.sleep to ensure no waiting occurs
            sleep_calls = []
            original_sleep = time.sleep

            def tracking_sleep(seconds: float) -> None:
                sleep_calls.append(seconds)
                original_sleep(seconds)

            monkeypatch.setattr(time, "sleep", tracking_sleep)

            # First request should succeed immediately without sleeping
            start = time.time()
            limiter.check_and_wait()
            elapsed = time.time() - start
            assert not sleep_calls, "Rate limiter unexpectedly slept on first request"
            assert elapsed < 0.5, f"First request should be immediate, took {elapsed}s"

            # Check state after first request
            with limiter.backend:
                state = limiter.backend.read()
                assert state["remaining"] == 4, f"Expected remaining=4, got {state['remaining']}"

            # Second request should also succeed immediately without sleeping
            start = time.time()
            limiter.check_and_wait()
            elapsed = time.time() - start
            assert not sleep_calls, "Rate limiter unexpectedly slept on second request"
            assert elapsed < 0.5, f"Second request should be immediate, took {elapsed}s"

            # Check state after second request
            with limiter.backend:
                state = limiter.backend.read()
                assert state["remaining"] == 3, f"Expected remaining=3, got {state['remaining']}"

            # Third request should wait because remaining (3) <= threshold (3)
            # Update the reset time to be shorter for testing
            limiter.update_from_headers({"X-Rate-Limit-Remaining": "3", "X-Rate-Limit-Reset": "1"})  # Reset in 1 second

            start = time.time()
            limiter.check_and_wait()
            elapsed = time.time() - start
            # Should have slept approximately 1 second + buffer and recorded the sleep call
            assert sleep_calls, "Rate limiter did not sleep when expected"
            assert 1.5 < elapsed < 2.5, f"Expected to wait ~2s, but waited {elapsed}s"

    def test_unknown_state_proceeds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that unknown state allows requests to proceed."""
        # Override worker detection to get predictable behavior
        monkeypatch.setenv("CRUDCLIENT_WORKERS", "1")

        with tempfile.TemporaryDirectory() as temp_dir:
            config = ClientConfig(hostname="test.api")
            config.enable_rate_limiter(state_path=temp_dir, buffer=2)
            limiter = get_rate_limiter(config)
            assert limiter is not None, "Rate limiter should be created"

            # Initially state should be unknown
            with limiter.backend:
                state = limiter.backend.read()
                assert state["remaining"] == -1, "Initial state should be unknown"

            # Request should proceed immediately when unknown
            start = time.time()
            limiter.check_and_wait()
            elapsed = time.time() - start
            assert elapsed < 0.1, f"Request with unknown state should be immediate, took {elapsed}s"

            # State should still be unknown after request
            with limiter.backend:
                state = limiter.backend.read()
                assert state["remaining"] == -1, "State should remain unknown"

    def test_rate_limit_window_reset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that rate limit resets after window expires."""
        # Override worker detection to get predictable behavior
        monkeypatch.setenv("CRUDCLIENT_WORKERS", "1")

        with tempfile.TemporaryDirectory() as temp_dir:
            config = ClientConfig(hostname="test.api")
            config.enable_rate_limiter(state_path=temp_dir, buffer=2)
            limiter = get_rate_limiter(config)
            assert limiter is not None, "Rate limiter should be created"

            # Set rate limit that will expire soon
            limiter.update_from_headers({"X-Rate-Limit-Remaining": "0", "X-Rate-Limit-Reset": "0.5"})  # Reset in 0.5 seconds

            # First request should wait for reset
            start = time.time()
            limiter.check_and_wait()
            elapsed = time.time() - start
            # Should wait 0.5s + 1s buffer = 1.5s
            assert 1.0 < elapsed < 2.0, f"Expected to wait ~1.5s for reset, waited {elapsed}s"

            # After reset, state should be unknown and requests proceed
            with limiter.backend:
                state = limiter.backend.read()
                assert state["remaining"] == -1, "State should be unknown after reset"

    def test_delay_history_tracking(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Ensure delay history is recorded when track_delays is enabled."""
        monkeypatch.setenv("CRUDCLIENT_WORKERS", "1")

        with tempfile.TemporaryDirectory() as temp_dir:
            config = ClientConfig(hostname="test.api")
            config.enable_rate_limiter(state_path=temp_dir, buffer=1, track_delays=True)
            limiter = get_rate_limiter(config)
            assert limiter is not None, "Rate limiter should be created"

            limiter.update_from_headers({"X-Rate-Limit-Remaining": "0", "X-Rate-Limit-Reset": "0.1"})
            # Delay should be approximately the reset interval + buffer (0.1 + 1 = 1.1 seconds)

            start = time.time()
            limiter.check_and_wait()
            elapsed = time.time() - start

            delays = limiter.get_delay_history()
            assert len(delays) == 1, "Expected a single recorded delay"

            # The tracked delay should be the intended wait time (reset_time + buffer)
            expected_delay = 0.1 + 1  # reset_time + buffer
            assert delays[0] == pytest.approx(expected_delay, rel=0.3, abs=0.2), f"Expected delay ~{expected_delay}s, got {delays[0]}s"

            # The elapsed time should be close to the tracked delay, but allow for more variance
            # in CI environments due to system scheduling and load
            assert elapsed == pytest.approx(delays[0], rel=0.5, abs=0.3), f"Elapsed time {elapsed}s should be close to tracked delay {delays[0]}s"

            limiter.clear_delay_history()
            assert limiter.get_delay_history() == []

    def test_get_rate_limiter_disabled(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_rate_limiter returns None when rate limiting is disabled."""
        monkeypatch.setenv("CRUDCLIENT_WORKERS", "1")
        config = ClientConfig(hostname="test.api")

        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            limiter = get_rate_limiter(config)

        assert limiter is None
        assert captured == []

    def test_get_rate_limiter_enabled_warning(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """get_rate_limiter emits FutureWarning when enabled."""
        monkeypatch.setenv("CRUDCLIENT_WORKERS", "1")

        with tempfile.TemporaryDirectory() as temp_dir:
            config = ClientConfig(hostname="test.api")
            config.enable_rate_limiter(state_path=temp_dir)

            with warnings.catch_warnings(record=True) as captured:
                warnings.simplefilter("always")
                limiter = get_rate_limiter(config)

            assert limiter is not None
            assert len(captured) == 1
            assert issubclass(captured[0].category, FutureWarning)

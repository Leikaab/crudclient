from datetime import datetime, timedelta

from freezegun import freeze_time

from crudclient.testing.auth.api_key_rate_limiter import ApiKeyRateLimiter


def test_rate_limiter_init() -> None:
    """Test initial state of the rate limiter."""
    limiter = ApiKeyRateLimiter()
    assert limiter.rate_limit_enabled is False
    assert limiter.rate_limit_requests == 100  # Default value
    assert limiter.rate_limit_period == 3600  # Default value
    assert limiter.request_history == {}


def test_enable_rate_limiting() -> None:
    """Test enabling rate limiting with custom values."""
    limiter = ApiKeyRateLimiter()
    limiter.enable_rate_limiting(requests_per_period=5, period_seconds=60)
    assert limiter.rate_limit_enabled is True
    assert limiter.rate_limit_requests == 5
    assert limiter.rate_limit_period == 60


def test_initialize_key() -> None:
    """Test initializing a key adds it to history."""
    limiter = ApiKeyRateLimiter()
    limiter.initialize_key("key1")
    assert "key1" in limiter.request_history
    assert limiter.request_history["key1"] == []


def test_track_request_disabled() -> None:
    """Test track_request when rate limiting is disabled."""
    limiter = ApiKeyRateLimiter()
    limiter.initialize_key("key1")
    assert limiter.rate_limit_enabled is False
    assert limiter.track_request("key1") is True
    assert limiter.track_request("key1") is True
    assert len(limiter.request_history["key1"]) == 2  # History is still recorded


@freeze_time("2023-01-01 12:00:00")
def test_track_request_enabled_within_limit() -> None:
    """Test track_request when enabled and within limit."""
    limiter = ApiKeyRateLimiter()
    limiter.enable_rate_limiting(requests_per_period=2, period_seconds=60)
    limiter.initialize_key("key1")

    assert limiter.track_request("key1") is True
    assert len(limiter.request_history["key1"]) == 1
    assert limiter.track_request("key1") is True
    assert len(limiter.request_history["key1"]) == 2


@freeze_time("2023-01-01 12:00:00")
def test_track_request_enabled_exceed_limit() -> None:
    """Test track_request when enabled and limit is exceeded."""
    limiter = ApiKeyRateLimiter()
    limiter.enable_rate_limiting(requests_per_period=1, period_seconds=60)
    limiter.initialize_key("key1")

    assert limiter.track_request("key1") is True  # First request OK
    assert len(limiter.request_history["key1"]) == 1
    assert limiter.track_request("key1") is False  # Second request fails
    assert len(limiter.request_history["key1"]) == 2  # Still recorded


@freeze_time("2023-01-01 12:00:00")
def test_track_request_history_cleanup() -> None:
    """Test that old requests are cleaned up."""
    limiter = ApiKeyRateLimiter()
    limiter.enable_rate_limiting(requests_per_period=5, period_seconds=60)
    limiter.initialize_key("key1")

    # Add a request from 2 minutes ago
    limiter.request_history["key1"].append(datetime(2023, 1, 1, 11, 58, 0))
    # Add a request from 59 seconds ago
    limiter.request_history["key1"].append(datetime(2023, 1, 1, 11, 59, 1))
    # Add a request now
    limiter.request_history["key1"].append(datetime(2023, 1, 1, 12, 0, 0))

    assert len(limiter.request_history["key1"]) == 3

    # Track a new request, which should trigger cleanup
    assert limiter.track_request("key1") is True

    # The oldest request ( > 60s ago) should be removed
    assert len(limiter.request_history["key1"]) == 3  # Now 3 requests within the window
    assert datetime(2023, 1, 1, 11, 58, 0) not in limiter.request_history["key1"]
    assert datetime(2023, 1, 1, 11, 59, 1) in limiter.request_history["key1"]
    assert datetime(2023, 1, 1, 12, 0, 0) in limiter.request_history["key1"]


def test_track_request_limit_reset() -> None:
    """Test that the limit resets after the period passes."""
    with freeze_time("2023-01-01 12:00:00") as frozen_time:
        limiter = ApiKeyRateLimiter()
        limiter.enable_rate_limiting(requests_per_period=1, period_seconds=60)
        limiter.initialize_key("key1")

        assert limiter.track_request("key1") is True  # Use the limit
        assert limiter.track_request("key1") is False  # Exceed limit

        # Move time forward past the period
        frozen_time.tick(delta=timedelta(seconds=61))

        # Limit should be reset
        assert limiter.track_request("key1") is True
        assert len(limiter.request_history["key1"]) == 1  # Only the latest request remains


def test_get_rate_limit_status_disabled() -> None:
    """Test get_rate_limit_status when disabled."""
    limiter = ApiKeyRateLimiter()
    assert limiter.get_rate_limit_status("key1") == {"enabled": False}


@freeze_time("2023-01-01 12:00:00")
def test_get_rate_limit_status_enabled_new_key() -> None:
    """Test get_rate_limit_status for a new key when enabled."""
    limiter = ApiKeyRateLimiter()
    limiter.enable_rate_limiting(requests_per_period=10, period_seconds=300)
    # Key not initialized yet

    status = limiter.get_rate_limit_status("new_key")
    assert status["enabled"] is True
    assert status["limit"] == 10
    assert status["remaining"] == 10
    assert status["reset"] == datetime(2023, 1, 1, 12, 5, 0)  # Now + period
    assert "used" not in status  # 'used' only added if history exists


@freeze_time("2023-01-01 12:00:00")
def test_get_rate_limit_status_enabled_with_usage() -> None:
    """Test get_rate_limit_status with existing usage."""
    limiter = ApiKeyRateLimiter()
    limiter.enable_rate_limiting(requests_per_period=5, period_seconds=60)
    limiter.initialize_key("key1")

    # Simulate past requests
    limiter.request_history["key1"].append(datetime(2023, 1, 1, 11, 59, 30))  # Oldest
    limiter.request_history["key1"].append(datetime(2023, 1, 1, 11, 59, 45))
    limiter.request_history["key1"].append(datetime(2023, 1, 1, 12, 0, 0))  # Newest (now)

    status = limiter.get_rate_limit_status("key1")
    assert status["enabled"] is True
    assert status["limit"] == 5
    assert status["remaining"] == 2  # 5 - 3 used
    assert status["used"] == 3
    # Reset time is when the oldest request expires
    assert status["reset"] == datetime(2023, 1, 1, 12, 0, 30)  # 11:59:30 + 60s


@freeze_time("2023-01-01 12:00:00")
def test_get_rate_limit_status_after_reset() -> None:
    """Test get_rate_limit_status after the period has passed."""
    limiter = ApiKeyRateLimiter()
    limiter.enable_rate_limiting(requests_per_period=5, period_seconds=60)
    limiter.initialize_key("key1")

    # Simulate a request from 70 seconds ago
    limiter.request_history["key1"].append(datetime(2023, 1, 1, 11, 58, 50))

    status = limiter.get_rate_limit_status("key1")
    # The old request should be cleaned up during status check
    assert status["enabled"] is True
    assert status["limit"] == 5
    assert status["remaining"] == 5  # Back to full limit
    assert status["used"] == 0
    # Reset time is now + period, as there are no recent requests
    assert status["reset"] == datetime(2023, 1, 1, 12, 1, 0)

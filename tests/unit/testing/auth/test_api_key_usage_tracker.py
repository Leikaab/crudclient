from crudclient.testing.auth.api_key_usage_tracker import ApiKeyUsageTracker


def test_usage_tracker_init() -> None:
    """Test initial state of the usage tracker."""
    tracker = ApiKeyUsageTracker()
    assert tracker.usage_tracking_enabled is False
    assert tracker.usage_by_endpoint == {}
    assert tracker.usage_by_key == {}


def test_enable_usage_tracking() -> None:
    """Test enabling usage tracking."""
    tracker = ApiKeyUsageTracker()
    tracker.enable_usage_tracking()
    assert tracker.usage_tracking_enabled is True


def test_initialize_key() -> None:
    """Test initializing a key adds it to usage_by_key with zero count."""
    tracker = ApiKeyUsageTracker()
    tracker.initialize_key("key1")
    assert "key1" in tracker.usage_by_key
    assert tracker.usage_by_key["key1"] == 0


def test_track_request_disabled() -> None:
    """Test track_request does nothing when tracking is disabled."""
    tracker = ApiKeyUsageTracker()
    assert tracker.usage_tracking_enabled is False
    tracker.track_request("key1", "/users")
    assert tracker.usage_by_key == {}
    assert tracker.usage_by_endpoint == {}


def test_track_request_enabled_key_only() -> None:
    """Test track_request increments key count when enabled."""
    tracker = ApiKeyUsageTracker()
    tracker.enable_usage_tracking()
    tracker.initialize_key("key1")

    tracker.track_request("key1")
    assert tracker.usage_by_key["key1"] == 1
    assert tracker.usage_by_endpoint == {}  # No endpoint provided

    tracker.track_request("key1")
    assert tracker.usage_by_key["key1"] == 2

    tracker.track_request("key2")  # New key
    assert tracker.usage_by_key["key2"] == 1


def test_track_request_enabled_with_endpoint() -> None:
    """Test track_request increments key and endpoint counts when enabled."""
    tracker = ApiKeyUsageTracker()
    tracker.enable_usage_tracking()
    tracker.initialize_key("key1")

    tracker.track_request("key1", "/users")
    assert tracker.usage_by_key["key1"] == 1
    assert tracker.usage_by_endpoint["/users"] == 1

    tracker.track_request("key1", "/users")
    assert tracker.usage_by_key["key1"] == 2
    assert tracker.usage_by_endpoint["/users"] == 2

    tracker.track_request("key1", "/posts")  # Different endpoint
    assert tracker.usage_by_key["key1"] == 3
    assert tracker.usage_by_endpoint["/users"] == 2
    assert tracker.usage_by_endpoint["/posts"] == 1

    tracker.track_request("key2", "/users")  # Different key, same endpoint
    assert tracker.usage_by_key["key1"] == 3
    assert tracker.usage_by_key["key2"] == 1
    assert tracker.usage_by_endpoint["/users"] == 3
    assert tracker.usage_by_endpoint["/posts"] == 1


def test_get_usage_stats_empty() -> None:
    """Test get_usage_stats when no requests tracked."""
    tracker = ApiKeyUsageTracker()
    stats = tracker.get_usage_stats()
    assert stats == {"by_key": {}, "by_endpoint": {}, "total_requests": 0}


def test_get_usage_stats_with_data() -> None:
    """Test get_usage_stats returns correct aggregated data."""
    tracker = ApiKeyUsageTracker()
    tracker.enable_usage_tracking()
    tracker.track_request("key1", "/users")
    tracker.track_request("key1", "/users")
    tracker.track_request("key2", "/posts")
    tracker.track_request("key1")  # No endpoint

    stats = tracker.get_usage_stats()
    expected_stats = {"by_key": {"key1": 3, "key2": 1}, "by_endpoint": {"/users": 2, "/posts": 1}, "total_requests": 4}
    assert stats == expected_stats

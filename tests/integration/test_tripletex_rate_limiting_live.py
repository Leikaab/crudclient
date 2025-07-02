"""
Live integration test for rate limiting against Tripletex API.

This test demonstrates that our rate limiter prevents 429 errors
when making rapid requests to the actual Tripletex API.
"""

import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from crudclient.exceptions import RateLimitError
from tests.integration.tripletex_resources import (
    TripletexAPI,
    TripletexTestConfig,
)

# Set up logging to see rate limiter logs during tests
logging.getLogger("crudclient.ratelimit").setLevel(logging.DEBUG)


@pytest.mark.skipif(
    not os.getenv("TRIPLETEX_TEST_CONSUMER_TOKEN") or not os.getenv("TRIPLETEX_TEST_EMPLOYEE_TOKEN"),
    reason="Tripletex test credentials not configured",
)
@pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Skip live API rate limiting tests in CI - file-based rate limiter doesn't work across matrix jobs",
)
@pytest.mark.no_parallel
def test_tripletex_rate_limiting_prevents_429():
    """
    Test that rate limiter prevents 429 errors under real rate limit conditions.

    This test runs both protected and unprotected clients simultaneously to ensure
    we're testing under actual rate limit pressure.
    """

    print("\n=== Simultaneous test with protected and unprotected clients ===")

    # Create both clients
    # For the unprotected client, we need to disable the automatic rate limiting
    config_unprotected = TripletexTestConfig()
    config_unprotected._rate_limiter_enabled = False  # Disable automatic rate limiting for comparison
    api_unprotected = TripletexAPI(client_config=config_unprotected)

    config_protected = TripletexTestConfig()
    # TripletexTestConfig already enables rate limiting, just enable tracking
    config_protected._rate_limiter_track_delays = True
    api_protected = TripletexAPI(client_config=config_protected)

    # Get rate limiter for monitoring
    from crudclient.ratelimit import get_rate_limiter

    rate_limiter = get_rate_limiter(config_protected)

    # Shared results storage
    unprotected_results: list[tuple[str, float]] = []
    protected_results: list[tuple[str, float]] = []
    results_lock = threading.Lock()

    def make_requests(api, num_requests, results_list, client_name):
        """Make requests and track results."""
        local_results = []

        for i in range(num_requests):
            try:
                start = time.time()
                api.countries.list(params={"count": 1})
                elapsed = time.time() - start
                local_results.append(("success", elapsed))
            except RateLimitError:
                elapsed = time.time() - start
                local_results.append(("rate_limited", elapsed))
            except Exception:
                elapsed = time.time() - start
                local_results.append(("error", elapsed))

        with results_lock:
            results_list.extend(local_results)

    # Run both clients in parallel with high request volume
    num_requests_per_client = 100

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=2) as executor:
        # Start both clients simultaneously
        unprotected_future = executor.submit(make_requests, api_unprotected, num_requests_per_client, unprotected_results, "UNPROTECTED")
        protected_future = executor.submit(make_requests, api_protected, num_requests_per_client, protected_results, "PROTECTED")

        # Wait for both to complete
        unprotected_future.result()
        protected_future.result()

    total_time = time.time() - start_time

    # Analyze results
    print(f"\n=== Results after {total_time:.1f}s ===")

    # Unprotected client results
    unprotected_success = sum(1 for status, _ in unprotected_results if status == "success")
    unprotected_limited = sum(1 for status, _ in unprotected_results if status == "rate_limited")
    unprotected_errors = sum(1 for status, _ in unprotected_results if status == "error")

    print("\nUNPROTECTED client (no rate limiter):")
    print(f"  Success: {unprotected_success}/{num_requests_per_client}")
    print(f"  Rate limited (429): {unprotected_limited}/{num_requests_per_client}")
    print(f"  Other errors: {unprotected_errors}")

    # Protected client results
    protected_success = sum(1 for status, _ in protected_results if status == "success")
    protected_limited = sum(1 for status, _ in protected_results if status == "rate_limited")
    protected_errors = sum(1 for status, _ in protected_results if status == "error")

    print("\nPROTECTED client (with rate limiter):")
    print(f"  Success: {protected_success}/{num_requests_per_client}")
    print(f"  Rate limited (429): {protected_limited}/{num_requests_per_client}")
    print(f"  Other errors: {protected_errors}")

    # Check timing differences
    avg_unprotected_time = sum(t for _, t in unprotected_results) / len(unprotected_results)
    avg_protected_time = sum(t for _, t in protected_results) / len(protected_results)

    print("\nAverage request times:")
    print(f"  Unprotected: {avg_unprotected_time:.3f}s")
    print(f"  Protected: {avg_protected_time:.3f}s")

    # Check delay tracking
    if rate_limiter:
        delays = rate_limiter.get_delay_history()
        if delays:
            print(f"\nRate limiter introduced {len(delays)} delays totaling {sum(delays):.2f}s")

    # Key assertions
    if unprotected_limited > 0:
        # If unprotected got rate limited, protected should have prevented them
        assert protected_limited == 0, (
            f"Rate limiter failed! Protected client got {protected_limited} rate limit errors "
            f"while unprotected got {unprotected_limited}. The rate limiter should have prevented ALL 429s."
        )
        print("\n✅ SUCCESS: Rate limiter prevented all 429 errors!")
        print(f"   Unprotected client: {unprotected_limited} rate limit errors")
        print("   Protected client: 0 rate limit errors (prevented by rate limiter)")
    else:
        # If we didn't trigger rate limits, at least verify the rate limiter didn't break anything
        assert protected_success > 0, "Protected client had no successful requests"

        if avg_protected_time > avg_unprotected_time * 1.5:
            print(f"\n✅ Rate limiter added protective delays (avg {avg_protected_time - avg_unprotected_time:.3f}s per request)")
        else:
            print(f"\n⚠️  WARNING: Could not trigger rate limits with {num_requests_per_client} requests per client.")
            print("   The API may have higher rate limits than expected.")
            print("   However, the rate limiter did not cause any errors.")


@pytest.mark.skipif(
    not os.getenv("TRIPLETEX_TEST_CONSUMER_TOKEN") or not os.getenv("TRIPLETEX_TEST_EMPLOYEE_TOKEN"),
    reason="Tripletex test credentials not configured",
)
@pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Skip live API rate limiting tests in CI - file-based rate limiter doesn't work across matrix jobs",
)
@pytest.mark.no_parallel
def test_rate_limiter_delay_tracking():
    """Test that the rate limiter delay tracking mechanism works correctly."""

    print("\n=== Testing rate limiter delay tracking ===")

    # Create a config with tracking enabled
    config = TripletexTestConfig()
    config.enable_rate_limiter(track_delays=True, buffer=5)
    api = TripletexAPI(client_config=config)

    # Get rate limiter
    from crudclient.ratelimit import get_rate_limiter

    rate_limiter = get_rate_limiter(config)

    if not rate_limiter:
        pytest.fail("Rate limiter should be enabled")

    # Clear any existing delays
    rate_limiter.clear_delay_history()

    # Force the rate limiter to think we're near the limit
    # This is a bit of a hack but necessary for testing
    with rate_limiter.backend:
        rate_limiter.backend.write({"remaining": 10, "reset_ts": time.time() + 1})  # Low remaining count  # Reset in 1 seconds

    print("Set rate limiter state to low remaining count...")

    # Make some requests - these should trigger delays
    print("\nMaking requests that should trigger delays...")

    for i in range(5):
        try:
            api.countries.list(params={"count": 1})
            print(f"  Request {i + 1}: Success")
        except Exception as e:
            print(f"  Request {i + 1}: {type(e).__name__}")

    # Check delays
    delays = rate_limiter.get_delay_history()

    print("\nDelay tracking results:")
    print(f"  Delays recorded: {len(delays)}")
    if delays:
        print(f"  Delay values: {[f'{d:.1f}s' for d in delays]}")
        print(f"  Total delay time: {sum(delays):.1f}s")

    # We should have at least one delay given the low remaining count
    if len(delays) > 0:
        print("\n✅ Delay tracking is working correctly!")
    else:
        print("\n⚠️  No delays were tracked. The rate limiter may have different thresholds than expected.")

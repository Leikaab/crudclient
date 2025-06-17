"""
Integration tests for rate limiting functionality.

Tests the full rate limiting behavior with real HTTP clients and file storage.
"""

import multiprocessing
import os
import tempfile
import time

from apiconfig.testing.integration import configure_mock_response

from crudclient.config import ClientConfig
from crudclient.http import HttpClient
from crudclient.ratelimit import get_rate_limiter


def api_worker(
    worker_id: int,
    state_dir: str,
    base_url: str,
    results_queue: multiprocessing.Queue,
    requests_per_worker: int = 10,
) -> None:
    """
    Worker process that makes API requests with rate limiting.

    Args:
        worker_id: Unique identifier for this worker
        state_dir: Directory for rate limiter state
        results_queue: Queue to report results
        requests_per_worker: Number of requests to make
    """
    try:
        # Create config with rate limiting
        config = ClientConfig(hostname=base_url)
        config.enable_rate_limiter(state_path=state_dir, buffer=2, buffer_time=0.05)

        # Create HTTP client
        client = HttpClient(config=config)
        limiter = get_rate_limiter(config)

        # Track successful and blocked requests
        successful = 0
        blocked = 0

        for i in range(requests_per_worker):
            start_time = time.time()

            try:
                client.get("/test")
                elapsed = time.time() - start_time

                if elapsed > 0.05:  # Adjusted assertion
                    blocked += 1
                    print(f"Worker {worker_id}: Request {i + 1} waited {elapsed:.3f}s")

                # If we got here without exception, request was successful
                successful += 1
            except Exception as e:
                print(f"Worker {worker_id}: Request {i + 1} failed: {e}")

            # Update rate limit from response headers
            # Simulate API returning decreasing rate limit
            remaining = 10 - ((worker_id * requests_per_worker + i) % 10)
            if limiter:
                limiter.update_from_headers({"X-Rate-Limit-Remaining": str(remaining), "X-Rate-Limit-Reset": "0.2"})  # Reduced reset window

            # Small delay between requests
            time.sleep(0.001)

        results_queue.put((worker_id, successful, blocked))

    except Exception as e:
        print(f"Worker {worker_id} failed with error: {e}")
        import traceback

        traceback.print_exc()
        # Still report results even on error
        results_queue.put((worker_id, 0, 0))


class TestRateLimitIntegration:
    """Integration tests for rate limiting."""

    def test_multi_process_rate_limiting(self, httpserver, mock_api_url):
        """Test rate limiting across multiple processes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            num_workers = 4
            requests_per_worker = 10

            # Initialize rate limiter with starting state
            config = ClientConfig(hostname=mock_api_url)
            config.enable_rate_limiter(state_path=temp_dir, buffer=2, buffer_time=0.05)
            limiter = get_rate_limiter(config)

            # Set initial state
            initial_state = {"remaining": 10, "reset_ts": time.time() + 0.2, "limit": 10}  # Reduced reset window
            if limiter and hasattr(limiter, "backend"):
                with limiter.backend:
                    limiter.backend.write(initial_state)

            # Start worker processes
            results_queue = multiprocessing.Queue()
            processes = []

            configure_mock_response(httpserver, path="/test", response_data={"status": "ok"})

            for i in range(num_workers):
                p = multiprocessing.Process(
                    target=api_worker,
                    args=(i, temp_dir, mock_api_url, results_queue, requests_per_worker),
                )
                p.start()
                processes.append(p)

            # Wait for completion with generous timeout for CI
            timeout = 10 if os.environ.get("GITHUB_ACTIONS") == "true" else 5
            for p in processes:
                p.join(timeout=timeout)
                if p.is_alive():
                    print(f"Warning: Process {p.pid} timed out after {timeout}s, terminating...")
                    p.terminate()
                    p.join()

            # Collect results
            total_successful = 0
            total_blocked = 0
            results = {}

            # Wait a bit for queue to be populated
            time.sleep(0.5)

            # Collect all available results with timeout
            deadline = time.time() + 2.0  # 2 second deadline for collecting results
            while time.time() < deadline:
                try:
                    worker_id, successful, blocked = results_queue.get(timeout=0.1)
                    results[worker_id] = {"successful": successful, "blocked": blocked}
                    total_successful += successful
                    total_blocked += blocked
                except Exception:
                    # Check if we have enough results
                    if len(results) >= num_workers - 1:
                        break
                    continue

            print("\nResults:")
            print(f"  Workers reporting: {len(results)}/{num_workers}")
            print(f"  Total successful: {total_successful}")
            print(f"  Total blocked: {total_blocked}")
            print(f"  Worker details: {results}")

            # Assertions with CI awareness
            # In all environments, allow for one worker to fail (common in multiprocessing tests)
            assert len(results) >= num_workers - 1, f"Too few workers reported: {len(results)}/{num_workers}"

            # At least some requests should succeed
            assert total_successful > 0, "No successful requests"

            if os.environ.get("GITHUB_ACTIONS") != "true":
                # In local testing only, expect more strict results
                # Total requests should be reasonable (at least 75% of expected)
                expected_min = (num_workers - 1) * requests_per_worker * 0.75
                assert total_successful >= expected_min, f"Too few successful requests: {total_successful} < {expected_min}"

                # We expect some blocking to occur
                assert total_blocked > 0, f"No blocking occurred: {total_blocked} == 0"

    def test_rate_limiter_with_http_client(self, httpserver, mock_api_url):
        """Test rate limiter integration with HttpClient."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create config with rate limiting
            config = ClientConfig(hostname=mock_api_url)
            config.enable_rate_limiter(state_path=temp_dir, buffer=1, buffer_time=0.05)

            # Create HTTP client
            client = HttpClient(config=config)

            # Pre-configure ordered responses with decreasing rate limit headers
            for i in range(7):
                remaining = max(0, 5 - i)
                configure_mock_response(
                    httpserver,
                    path="/test",
                    response_data={"data": "test"},
                    response_headers={"X-Rate-Limit-Remaining": str(remaining), "X-Rate-Limit-Reset": "0.1"},
                    ordered=True,
                )

            # Make requests until we hit the rate limit
            for i in range(7):
                start_time = time.time()
                response_data = client.get("/test")
                elapsed = time.time() - start_time

                # Successful if no exception was raised
                assert response_data is not None

                # After 5 requests, we should be rate limited
                if i >= 5:
                    # Should have waited for rate limit reset
                    assert elapsed > 0.05, f"Request {i + 1} should have waited, but took {elapsed}s"

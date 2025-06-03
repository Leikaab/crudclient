"""
Atomic parallel unit tests for rate limiter.

Tests that the rate limiter works correctly across multiple processes.
"""

import multiprocessing
import os
import tempfile
import time
from pathlib import Path


def worker_process(
    worker_id: int, state_dir: str, results_queue: multiprocessing.Queue, limit: int = 10, requests_per_worker: int = 5, num_workers: int = 8
) -> None:
    """
    Worker process that attempts to make requests with rate limiting.

    Args:
        worker_id: Unique identifier for this worker
        state_dir: Directory containing rate limiter state files
        results_queue: Queue to report successful calls
        limit: Total rate limit for all workers
        requests_per_worker: Number of requests each worker should try
    """
    import time

    from crudclient.config import ClientConfig

    # Import inside worker to test clean initialization
    from crudclient.ratelimit import get_rate_limiter

    # Set worker count explicitly for the process
    os.environ["CRUDCLIENT_WORKERS"] = str(num_workers)

    # Create a simple config with rate limiting enabled
    config = ClientConfig(hostname="test.api")
    config.enable_rate_limiter(state_path=state_dir, buffer=2, buffer_time=0.01)  # Small buffer and buffer_time for testing

    limiter = get_rate_limiter(config)

    # Simulate making requests
    successful_calls = 0
    blocked_calls = 0
    for i in range(requests_per_worker):
        try:
            # Track timing to detect blocks
            start_time = time.time()

            # This may wait if rate limited
            if limiter:
                limiter.check_and_wait()

            elapsed = time.time() - start_time

            if elapsed > 0.05:  # If it took more than 50ms, we were blocked
                blocked_calls += 1
                print(f"Worker {worker_id}: Request {i + 1} blocked for {elapsed:.3f}s")

            successful_calls += 1

            # Small delay to simulate API call
            time.sleep(0.001)  # 1ms instead of 10ms

        except Exception as e:
            # If we get an exception, count it as error
            print(f"Worker {worker_id} error on request {i + 1}: {e}")

    results_queue.put((worker_id, successful_calls, blocked_calls))


class TestRateLimiterParallel:
    """Test rate limiter with parallel processes."""

    def test_parallel_rate_limiting(self):
        """Test that multiple processes respect the rate limit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            num_workers = 4  # Reduce workers for easier debugging
            limit = 10  # Smaller limit
            requests_per_worker = 5
            results_queue: multiprocessing.Queue = multiprocessing.Queue()

            # Initialize rate limit state
            from crudclient.config import ClientConfig
            from crudclient.ratelimit import get_rate_limiter

            # Set worker count for main process
            os.environ["CRUDCLIENT_WORKERS"] = str(num_workers)

            config = ClientConfig(hostname="test.api")
            config.enable_rate_limiter(state_path=temp_dir, buffer=2, buffer_time=0.01)  # 10ms buffer for fast tests
            limiter = get_rate_limiter(config)

            # Set initial rate limit
            if limiter:
                limiter.update_from_headers({"X-Rate-Limit-Remaining": str(limit), "X-Rate-Limit-Reset": "0.3"})  # 300ms window instead of 30 seconds

            # Verify initial state was written
            if limiter:
                with limiter.backend:
                    state = limiter.backend.read()
                print(f"Initial state: {state}")
                assert state["remaining"] == limit, f"Initial state not set correctly: {state}"

            # Start worker processes
            processes = []
            for i in range(num_workers):
                p = multiprocessing.Process(target=worker_process, args=(i, temp_dir, results_queue, limit, requests_per_worker, num_workers))
                p.start()
                processes.append(p)

            # Wait for all processes to complete with timeout
            # Need to account for rate limit window (300ms) + buffer
            for p in processes:
                p.join(timeout=2)  # 2 seconds should be plenty for 300ms window
                if p.is_alive():
                    print(f"Process {p.pid} timed out after 2s")
                    p.terminate()
                    p.join()

            # Collect results
            total_calls = 0
            total_blocked = 0
            worker_results = {}
            while not results_queue.empty():
                result = results_queue.get()
                if len(result) == 2:
                    # Old format, for compatibility
                    worker_id, calls = result
                    blocked = 0
                else:
                    # New format with blocked count
                    worker_id, calls, blocked = result
                worker_results[worker_id] = {"successful": calls, "blocked": blocked}
                total_calls += calls
                total_blocked += blocked

            # Assertions
            print(f"Results: {worker_results}")
            print(f"Total successful: {total_calls}, Total blocked: {total_blocked}")

            # All workers should report
            assert len(worker_results) == num_workers, f"Not all workers reported: {worker_results}"

            # Since the rate limit window resets after 300ms, and workers wait when blocked,
            # all requests should eventually succeed (20 total for 4 workers × 5 requests each)
            assert total_calls == num_workers * requests_per_worker, f"Not all calls completed: {total_calls} != {num_workers * requests_per_worker}"

            # The important thing is that blocking occurred
            assert total_blocked > 0, f"No blocking occurred: {total_blocked} == 0"

            # In fact, all workers should have been blocked at some point
            blocked_workers = sum(1 for w in worker_results.values() if w["blocked"] > 0)
            assert blocked_workers == num_workers, f"Not all workers were blocked: {blocked_workers}/{num_workers}"

            # Check that state file was created
            state_files = list(Path(temp_dir).glob("*.json"))
            assert len(state_files) > 0, "No state files created"

    def test_rate_limit_reset_after_window(self):
        """Test that rate limit resets after the time window expires."""
        with tempfile.TemporaryDirectory() as temp_dir:
            from crudclient.config import ClientConfig
            from crudclient.ratelimit import get_rate_limiter

            config = ClientConfig(hostname="test.api")
            config.enable_rate_limiter(state_path=temp_dir, buffer_time=0.01)  # 10ms buffer for fast tests
            limiter = get_rate_limiter(config)

            # First, exhaust the rate limit
            for i in range(5):
                if limiter:
                    limiter.check_and_wait()
                    limiter.update_from_headers(
                        {"X-Rate-Limit-Remaining": str(4 - i), "X-Rate-Limit-Reset": "0.1"}  # Reset in 100ms instead of 2 seconds
                    )

            # Now we should be at the limit (remaining = 0)
            # This call should wait
            start_time = time.time()
            if limiter:
                limiter.check_and_wait()
            wait_time = time.time() - start_time

            # Should have waited approximately 100ms + 10ms buffer = 0.11 seconds
            assert 0.10 < wait_time < 0.15, f"Expected to wait ~0.11s (0.1s + 0.01s buffer), but waited {wait_time}s"

            # After reset, should be able to proceed immediately
            start_time = time.time()
            if limiter:
                limiter.check_and_wait()
            wait_time = time.time() - start_time
            assert wait_time < 0.1, f"Should not wait after reset, but waited {wait_time}s"

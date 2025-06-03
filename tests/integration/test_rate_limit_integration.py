"""
Integration test for rate limiting with simulated API responses.
"""

import multiprocessing
import os
import tempfile
import time

from crudclient.config import ClientConfig
from crudclient.ratelimit import get_rate_limiter


def api_worker(worker_id: int, state_dir: str, results_queue: multiprocessing.Queue, requests_per_worker: int = 10) -> None:
    """
    Worker that simulates making API requests with proper rate limit header updates.
    """
    # Set worker count for this process
    os.environ["CRUDCLIENT_WORKERS"] = "4"

    # Create rate limiter with minimal buffer_time for testing
    config = ClientConfig(hostname="test.api")
    config.enable_rate_limiter(state_path=state_dir, buffer=2, buffer_time=0.05)  # Reduced buffer_time
    limiter = get_rate_limiter(config)

    if not limiter:
        results_queue.put((worker_id, 0, 0))
        return

    successful = 0
    blocked = 0

    for i in range(requests_per_worker):
        try:
            # Track timing to detect blocks
            start_time = time.time()

            # Check rate limit before request
            limiter.check_and_wait()

            elapsed = time.time() - start_time

            if elapsed > 0.05:  # If it took more than 0.05s, we were blocked
                blocked += 1
            else:
                # Simulate successful API call
                successful += 1

                # Simulate API response updating rate limit headers
                # This helps test multiple rate limit windows
                with limiter.backend:
                    state = limiter.backend.read()
                    if state["reset_ts"] < time.time():
                        # Window expired, simulate new window
                        limiter.backend.write({"remaining": 10, "reset_ts": time.time() + 0.2})  # Reduced reset window

            # Very small delay to simulate API latency
            time.sleep(0.005)  # Reduced from 0.01s

        except Exception as e:
            blocked += 1
            print(f"Worker {worker_id} error: {e}")
            break

    results_queue.put((worker_id, successful, blocked))


class TestRateLimitIntegration:
    """Test rate limiting with realistic API simulation."""

    def test_multi_process_rate_limiting(self):
        """Test that multiple processes properly respect rate limits."""
        with tempfile.TemporaryDirectory() as temp_dir:
            num_workers = 4
            requests_per_worker = 10

            # Initialize rate limit state file
            # Since each worker will look for state in temp_dir, we need to create the state file
            # that the rate limiter will use
            initial_state = {
                "remaining": 10,  # Low limit to force blocking
                "reset_ts": time.time() + 0.2,  # Reduced reset window for faster testing
                "limit": 10,
            }

            # We need to use the same logic as RateLimiter to determine the state file path
            # For simplicity, let's create a config and limiter to get the correct path
            config = ClientConfig(hostname="test.api")
            config.enable_rate_limiter(state_path=temp_dir, buffer=2, buffer_time=0.05)  # Reduced buffer_time
            os.environ["CRUDCLIENT_WORKERS"] = str(num_workers)

            # Get a limiter instance to determine the state file path and initialize it
            limiter = get_rate_limiter(config)
            if limiter:
                # Write initial state
                with limiter.backend:
                    limiter.backend.write({"remaining": initial_state["remaining"], "reset_ts": initial_state["reset_ts"]})

            # Start worker processes
            results_queue = multiprocessing.Queue()
            processes = []

            for i in range(num_workers):
                p = multiprocessing.Process(target=api_worker, args=(i, temp_dir, results_queue, requests_per_worker))
                p.start()
                processes.append(p)

            # Wait for completion
            for p in processes:
                p.join(timeout=2)  # Further reduced timeout
                if p.is_alive():
                    print(f"Warning: Process {p.pid} timed out, terminating...")
                    p.terminate()
                    p.join()

            # Collect results
            total_successful = 0
            total_blocked = 0
            results = {}

            while not results_queue.empty():
                worker_id, successful, blocked = results_queue.get()
                results[worker_id] = {"successful": successful, "blocked": blocked}
                total_successful += successful
                total_blocked += blocked

            print("\nResults:")
            print(f"  Workers reporting: {len(results)}/{num_workers}")
            print(f"  Total successful: {total_successful}")
            print(f"  Total blocked: {total_blocked}")
            print(f"  Worker details: {results}")

            # Assertions
            assert len(results) == num_workers, "Not all workers reported"

            # Total requests should match expected
            assert (
                total_successful + total_blocked == num_workers * requests_per_worker
            ), f"Total mismatch: {total_successful} + {total_blocked} != {num_workers * requests_per_worker}"

            # We expect some blocking to occur (rate limiter is working)
            assert total_blocked > 0, f"No blocking occurred: {total_blocked} == 0"

            # At least some requests should have been successful
            assert total_successful > 0, "No successful requests"

            # The successful count should be less than total possible (rate limiting occurred)
            assert total_successful < num_workers * requests_per_worker, f"No rate limiting occurred: all {total_successful} requests succeeded"

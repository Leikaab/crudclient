from unittest.mock import MagicMock, patch

import pytest
import requests

from crudclient.exceptions import CrudClientError
from crudclient.http.retry import ExponentialBackoffStrategy, FixedRetryStrategy, RetryCondition, RetryEvent, RetryHandler


class TestRetryStrategies:
    """Tests for the retry strategies."""

    def test_fixed_retry_strategy(self):
        """Test that the fixed retry strategy returns the same delay for each attempt."""
        strategy = FixedRetryStrategy(delay=2.0)
        assert strategy.get_delay(1) == 2.0
        assert strategy.get_delay(2) == 2.0
        assert strategy.get_delay(3) == 2.0

    def test_exponential_backoff_strategy(self):
        """Test that the exponential backoff strategy increases the delay exponentially."""
        # Disable jitter for deterministic testing
        strategy = ExponentialBackoffStrategy(base_delay=1.0, max_delay=10.0, factor=2.0, jitter=False)
        assert strategy.get_delay(1) == 1.0
        assert strategy.get_delay(2) == 2.0
        assert strategy.get_delay(3) == 4.0
        assert strategy.get_delay(4) == 8.0
        # Should be capped at max_delay
        assert strategy.get_delay(5) == 10.0

    def test_exponential_backoff_with_jitter(self):
        """Test that the exponential backoff strategy adds jitter when enabled."""
        strategy = ExponentialBackoffStrategy(base_delay=1.0, max_delay=10.0, factor=2.0, jitter=True)
        # With jitter, the delay should be different but within a certain range
        delay1 = strategy.get_delay(3)  # Base would be 4.0
        delay2 = strategy.get_delay(3)  # Base would be 4.0
        assert delay1 != delay2  # Jitter should make these different
        assert 3.0 <= delay1 <= 6.0  # Should be within 75-125% of base
        assert 3.0 <= delay2 <= 6.0  # Should be within 75-125% of base


class TestRetryCondition:
    """Tests for the retry condition class."""

    def test_retry_on_status_code(self):
        """Test that the retry condition correctly identifies status codes to retry on."""
        condition = RetryCondition(status_codes=[500, 502, 503])

        # Create mock responses with different status codes
        response_500 = MagicMock(spec=requests.Response)
        response_500.status_code = 500

        response_404 = MagicMock(spec=requests.Response)
        response_404.status_code = 404

        # Should retry on 500
        assert condition.should_retry(response_500) is True
        # Should not retry on 404
        assert condition.should_retry(response_404) is False

    def test_retry_on_exception(self):
        """Test that the retry condition correctly identifies exceptions to retry on."""
        condition = RetryCondition(exceptions=[requests.Timeout, requests.ConnectionError])

        # Should retry on Timeout
        assert condition.should_retry(exception=requests.Timeout()) is True
        # Should retry on ConnectionError
        assert condition.should_retry(exception=requests.ConnectionError()) is True
        # Should not retry on other exceptions
        assert condition.should_retry(exception=ValueError()) is False

    def test_retry_on_event(self):
        """Test that the retry condition correctly handles RetryEvent enums."""
        condition = RetryCondition(events=[RetryEvent.SERVER_ERROR, RetryEvent.TIMEOUT])

        # Create mock response with 500 status code
        response_500 = MagicMock(spec=requests.Response)
        response_500.status_code = 500

        # Should retry on 500 (SERVER_ERROR)
        assert condition.should_retry(response_500) is True
        # Should retry on Timeout (TIMEOUT)
        assert condition.should_retry(exception=requests.Timeout()) is True

    def test_custom_retry_condition(self):
        """Test that custom retry conditions work correctly."""
        # Custom condition that retries if the response contains a specific header
        def custom_condition(response, exception):
            if response and response.headers.get("Retry-After"):
                return True
            return False

        condition = RetryCondition(custom_condition=custom_condition)

        # Create mock responses with and without the Retry-After header
        response_with_header = MagicMock(spec=requests.Response)
        response_with_header.headers = {"Retry-After": "30"}
        response_with_header.status_code = 200  # Add status_code attribute

        response_without_header = MagicMock(spec=requests.Response)
        response_without_header.headers = {}
        response_without_header.status_code = 200  # Add status_code attribute

        # Should retry when header is present
        assert condition.should_retry(response_with_header) is True
        # Should not retry when header is absent
        assert condition.should_retry(response_without_header) is False


class TestRetryHandler:
    """Tests for the retry handler class."""

    @pytest.fixture
    def retry_handler(self):
        """Create a retry handler with a fixed retry strategy for testing."""
        return RetryHandler(
            max_retries=3,
            retry_strategy=FixedRetryStrategy(delay=0.01),  # Small delay for faster tests
            retry_conditions=[
                RetryCondition(
                    status_codes=[500, 502, 503, 504],
                    exceptions=[requests.Timeout, requests.ConnectionError],
                )
            ],
        )

    def test_should_retry_status_code(self, retry_handler):
        """Test that the retry handler correctly identifies status codes to retry on."""
        # Create mock responses with different status codes
        response_500 = MagicMock(spec=requests.Response)
        response_500.status_code = 500

        response_404 = MagicMock(spec=requests.Response)
        response_404.status_code = 404

        # Should retry on 500
        assert retry_handler.should_retry(0, response_500) is True
        # Should not retry on 404
        assert retry_handler.should_retry(0, response_404) is False
        # Should not retry after max_retries
        assert retry_handler.should_retry(3, response_500) is False

    def test_should_retry_exception(self, retry_handler):
        """Test that the retry handler correctly identifies exceptions to retry on."""
        # Should retry on Timeout
        assert retry_handler.should_retry(0, exception=requests.Timeout()) is True
        # Should retry on ConnectionError
        assert retry_handler.should_retry(0, exception=requests.ConnectionError()) is True
        # Should not retry on other exceptions
        assert retry_handler.should_retry(0, exception=ValueError()) is False
        # Should not retry after max_retries
        assert retry_handler.should_retry(3, exception=requests.Timeout()) is False

    def test_get_delay(self, retry_handler):
        """Test that the retry handler correctly calculates the delay."""
        # Using FixedRetryStrategy with delay=0.01
        assert retry_handler.get_delay(1) == 0.01
        assert retry_handler.get_delay(2) == 0.01
        assert retry_handler.get_delay(3) == 0.01

    @patch("time.sleep")
    def test_execute_with_retry_success_first_try(self, mock_sleep, retry_handler):
        """Test that the retry handler returns the response if the first try succeeds."""
        # Mock a successful request function
        mock_response = MagicMock(spec=requests.Response)
        mock_response.ok = True
        request_func = MagicMock(return_value=mock_response)

        # Execute with retry
        response = retry_handler.execute_with_retry(request_func)

        # Should return the response from the first try
        assert response == mock_response
        # Should call the request function once
        request_func.assert_called_once()
        # Should not sleep
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_execute_with_retry_success_after_retry(self, mock_sleep, retry_handler):
        """Test that the retry handler retries and returns the response if a retry succeeds."""
        # Mock a request function that fails once then succeeds
        mock_error_response = MagicMock(spec=requests.Response)
        mock_error_response.ok = False
        mock_error_response.status_code = 500

        mock_success_response = MagicMock(spec=requests.Response)
        mock_success_response.ok = True

        request_func = MagicMock(side_effect=[mock_error_response, mock_success_response])

        # Execute with retry
        response = retry_handler.execute_with_retry(request_func)

        # Should return the successful response
        assert response == mock_success_response
        # Should call the request function twice
        assert request_func.call_count == 2
        # Should sleep once
        mock_sleep.assert_called_once_with(0.01)

    @patch("time.sleep")
    def test_execute_with_retry_all_failures(self, mock_sleep, retry_handler):
        """Test that the retry handler raises an exception if all retries fail."""
        # Mock a request function that always fails with a 500 error
        mock_error_response = MagicMock(spec=requests.Response)
        mock_error_response.ok = False
        mock_error_response.status_code = 500

        request_func = MagicMock(return_value=mock_error_response)

        # Execute with retry - should return the last error response after max retries
        response = retry_handler.execute_with_retry(request_func)

        # Should return the last error response
        assert response == mock_error_response
        # Should call the request function max_retries + 1 times (initial + retries)
        assert request_func.call_count == 4
        # Should sleep max_retries times
        assert mock_sleep.call_count == 3

    @patch("time.sleep")
    def test_execute_with_retry_exception(self, mock_sleep, retry_handler):
        """Test that the retry handler handles exceptions correctly."""
        # Mock a request function that raises an exception
        request_func = MagicMock(side_effect=requests.Timeout("Connection timed out"))

        # Execute with retry - should raise CrudClientError after max retries
        with pytest.raises(CrudClientError) as excinfo:
            retry_handler.execute_with_retry(request_func)

        # Error message should mention the timeout
        assert "Connection timed out" in str(excinfo.value)
        # Should call the request function max_retries + 1 times (initial + retries)
        assert request_func.call_count == 4
        # Should sleep max_retries times
        assert mock_sleep.call_count == 3

    @patch("time.sleep")
    def test_execute_with_retry_non_retryable_exception(self, mock_sleep, retry_handler):
        """Test that the retry handler doesn't retry on non-retryable exceptions."""
        # Mock a request function that raises a non-retryable exception
        request_func = MagicMock(side_effect=ValueError("Invalid value"))

        # Execute with retry - should raise the original exception
        with pytest.raises(ValueError) as excinfo:
            retry_handler.execute_with_retry(request_func)

        # Error message should be from the original exception
        assert "Invalid value" in str(excinfo.value)
        # Should call the request function only once
        request_func.assert_called_once()
        # Should not sleep
        mock_sleep.assert_not_called()

    def test_maybe_retry_after_403(self, retry_handler):
        """Test the maybe_retry_after_403 method."""
        # Create mock objects
        session = MagicMock(spec=requests.Session)
        setup_auth_func = MagicMock()

        # Mock a 403 response
        response_403 = MagicMock(spec=requests.Response)
        response_403.status_code = 403

        # Mock a successful retry response
        retry_response = MagicMock(spec=requests.Response)
        retry_response.status_code = 200
        session.request.return_value = retry_response

        # Call maybe_retry_after_403
        result = retry_handler.maybe_retry_after_403(
            "GET", "https://example.com", {}, response_403, session, setup_auth_func
        )

        # Should return the retry response
        assert result == retry_response
        # Should call setup_auth_func
        setup_auth_func.assert_called_once()
        # Should make a new request
        session.request.assert_called_once_with("GET", "https://example.com", **{})

    def test_maybe_retry_after_403_non_403(self, retry_handler):
        """Test that maybe_retry_after_403 doesn't retry for non-403 responses."""
        # Create mock objects
        session = MagicMock(spec=requests.Session)
        setup_auth_func = MagicMock()

        # Mock a non-403 response
        response_404 = MagicMock(spec=requests.Response)
        response_404.status_code = 404

        # Call maybe_retry_after_403
        result = retry_handler.maybe_retry_after_403(
            "GET", "https://example.com", {}, response_404, session, setup_auth_func
        )

        # Should return the original response
        assert result == response_404
        # Should not call setup_auth_func
        setup_auth_func.assert_not_called()
        # Should not make a new request
        session.request.assert_not_called()

    @patch("time.sleep")
    def test_on_retry_callback(self, mock_sleep):
        """Test that the on_retry_callback is called correctly."""
        # Create a mock callback
        callback = MagicMock()

        # Create a retry handler with the callback
        retry_handler = RetryHandler(
            max_retries=2,
            retry_strategy=FixedRetryStrategy(delay=0.01),
            retry_conditions=[RetryCondition(status_codes=[500])],
            on_retry_callback=callback,
        )

        # Mock a request function that always fails with a 500 error
        mock_error_response = MagicMock(spec=requests.Response)
        mock_error_response.ok = False
        mock_error_response.status_code = 500

        request_func = MagicMock(return_value=mock_error_response)

        # Execute with retry
        retry_handler.execute_with_retry(request_func)

        # Callback should be called twice (once for each retry)
        assert callback.call_count == 2

        # First call should be with attempt=1, delay=0.01, response=mock_error_response
        callback.assert_any_call(1, 0.01, mock_error_response, None)

        # Second call should be with attempt=2, delay=0.01, response=mock_error_response
        callback.assert_any_call(2, 0.01, mock_error_response, None)

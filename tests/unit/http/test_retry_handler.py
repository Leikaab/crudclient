from unittest.mock import MagicMock

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

    # Using retry_handler fixture from conftest.py

    def test_should_retry_status_code(self, retry_handler, mocker):
        """Test that the retry handler correctly identifies status codes to retry on."""
        # Arrange
        response_500 = mocker.Mock(spec=requests.Response)
        response_500.status_code = 500

        response_404 = mocker.Mock(spec=requests.Response)
        response_404.status_code = 404

        # Act & Assert
        # Should retry on 500
        assert retry_handler.should_retry(0, response_500) is True
        # Should not retry on 404
        assert retry_handler.should_retry(0, response_404) is False
        # Should not retry after max_retries
        assert retry_handler.should_retry(3, response_500) is False

    def test_should_retry_exception(self, retry_handler):
        """Test that the retry handler correctly identifies exceptions to retry on."""
        # Arrange
        timeout_exception = requests.Timeout()
        connection_error = requests.ConnectionError()
        value_error = ValueError()

        # Act & Assert
        # Should retry on Timeout
        assert retry_handler.should_retry(0, exception=timeout_exception) is True
        # Should retry on ConnectionError
        assert retry_handler.should_retry(0, exception=connection_error) is True
        # Should not retry on other exceptions
        assert retry_handler.should_retry(0, exception=value_error) is False
        # Should not retry after max_retries
        assert retry_handler.should_retry(3, exception=timeout_exception) is False

    def test_get_delay(self, retry_handler):
        """Test that the retry handler correctly calculates the delay."""
        # Arrange - Using FixedRetryStrategy with delay=0.01 from fixture

        # Act & Assert
        assert retry_handler.get_delay(1) == 0.01
        assert retry_handler.get_delay(2) == 0.01
        assert retry_handler.get_delay(3) == 0.01

    def test_execute_with_retry_success_first_try(self, retry_handler, mocker):
        """Test that the retry handler returns the response if the first try succeeds."""
        # Arrange
        mock_sleep = mocker.patch("time.sleep")
        mock_response = mocker.Mock(spec=requests.Response)
        mock_response.ok = True
        request_func = mocker.Mock(return_value=mock_response)

        # Act
        response = retry_handler.execute_with_retry(request_func)

        # Assert
        assert response == mock_response
        request_func.assert_called_once()
        mock_sleep.assert_not_called()

    def test_execute_with_retry_success_after_retry(self, retry_handler, mocker):
        """Test that the retry handler retries and returns the response if a retry succeeds."""
        # Arrange
        mock_sleep = mocker.patch("time.sleep")

        # Mock a request function that fails once then succeeds
        mock_error_response = mocker.Mock(spec=requests.Response)
        mock_error_response.ok = False
        mock_error_response.status_code = 500

        mock_success_response = mocker.Mock(spec=requests.Response)
        mock_success_response.ok = True

        request_func = mocker.Mock(side_effect=[mock_error_response, mock_success_response])

        # Act
        response = retry_handler.execute_with_retry(request_func)

        # Assert
        assert response == mock_success_response
        assert request_func.call_count == 2
        mock_sleep.assert_called_once_with(0.01)

    def test_execute_with_retry_all_failures(self, retry_handler, mocker):
        """Test that the retry handler raises an exception if all retries fail."""
        # Arrange
        mock_sleep = mocker.patch("time.sleep")

        # Mock a request function that always fails with a 500 error
        mock_error_response = mocker.Mock(spec=requests.Response)
        mock_error_response.ok = False
        mock_error_response.status_code = 500

        request_func = mocker.Mock(return_value=mock_error_response)

        # Act
        response = retry_handler.execute_with_retry(request_func)

        # Assert
        assert response == mock_error_response
        # Should call the request function max_retries + 1 times (initial + retries)
        assert request_func.call_count == 4
        # Should sleep max_retries times
        assert mock_sleep.call_count == 3

    def test_execute_with_retry_exception(self, retry_handler, mocker):
        """Test that the retry handler handles exceptions correctly."""
        # Arrange
        mock_sleep = mocker.patch("time.sleep")

        # Mock a request function that raises an exception
        request_func = mocker.Mock(side_effect=requests.Timeout("Connection timed out"))

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            retry_handler.execute_with_retry(request_func)

        # Error message should mention the timeout
        assert "Connection timed out" in str(excinfo.value)
        # Should call the request function max_retries + 1 times (initial + retries)
        assert request_func.call_count == 4
        # Should sleep max_retries times
        assert mock_sleep.call_count == 3

    def test_execute_with_retry_non_retryable_exception(self, retry_handler, mocker):
        """Test that the retry handler doesn't retry on non-retryable exceptions."""
        # Arrange
        mock_sleep = mocker.patch("time.sleep")

        # Mock a request function that raises a non-retryable exception
        request_func = mocker.Mock(side_effect=ValueError("Invalid value"))

        # Act & Assert
        with pytest.raises(ValueError) as excinfo:
            retry_handler.execute_with_retry(request_func)

        # Error message should be from the original exception
        assert "Invalid value" in str(excinfo.value)
        # Should call the request function only once
        request_func.assert_called_once()
        # Should not sleep
        mock_sleep.assert_not_called()

    def test_maybe_retry_after_403(self, retry_handler, mocker):
        """Test the maybe_retry_after_403 method."""
        # Arrange
        session = mocker.Mock(spec=requests.Session)
        setup_auth_func = mocker.Mock()

        # Mock a 403 response
        response_403 = mocker.Mock(spec=requests.Response)
        response_403.status_code = 403

        # Mock a successful retry response
        retry_response = mocker.Mock(spec=requests.Response)
        retry_response.status_code = 200
        session.request.return_value = retry_response

        # Act
        result = retry_handler.maybe_retry_after_403(
            "GET", "https://example.com", {}, response_403, session, setup_auth_func
        )

        # Assert
        assert result == retry_response
        setup_auth_func.assert_called_once()
        session.request.assert_called_once_with("GET", "https://example.com", **{})

    def test_maybe_retry_after_403_non_403(self, retry_handler, mocker):
        """Test that maybe_retry_after_403 doesn't retry for non-403 responses."""
        # Arrange
        session = mocker.Mock(spec=requests.Session)
        setup_auth_func = mocker.Mock()

        # Mock a non-403 response
        response_404 = mocker.Mock(spec=requests.Response)
        response_404.status_code = 404

        # Act
        result = retry_handler.maybe_retry_after_403(
            "GET", "https://example.com", {}, response_404, session, setup_auth_func
        )

        # Assert
        assert result == response_404
        setup_auth_func.assert_not_called()
        session.request.assert_not_called()

    def test_on_retry_callback(self, mocker):
        """Test that the on_retry_callback is called correctly."""
        # Arrange
        mocker.patch("time.sleep")  # Patch time.sleep but don't assign to unused variable
        callback = mocker.Mock()

        # Create a retry handler with the callback
        retry_handler = RetryHandler(
            max_retries=2,
            retry_strategy=FixedRetryStrategy(delay=0.01),
            retry_conditions=[RetryCondition(status_codes=[500])],
            on_retry_callback=callback,
        )

        # Mock a request function that always fails with a 500 error
        mock_error_response = mocker.Mock(spec=requests.Response)
        mock_error_response.ok = False
        mock_error_response.status_code = 500

        request_func = mocker.Mock(return_value=mock_error_response)

        # Act
        retry_handler.execute_with_retry(request_func)

        # Assert
        # Callback should be called twice (once for each retry)
        assert callback.call_count == 2

        # First call should be with attempt=1, delay=0.01, response=mock_error_response
        callback.assert_any_call(1, 0.01, mock_error_response, None)

        # Second call should be with attempt=2, delay=0.01, response=mock_error_response
        callback.assert_any_call(2, 0.01, mock_error_response, None)

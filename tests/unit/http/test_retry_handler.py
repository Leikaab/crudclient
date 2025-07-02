import logging  # <-- Add import
from typing import Optional
from unittest.mock import MagicMock

import pytest
import requests
from pytest_mock import MockerFixture
from requests import exceptions as requests_exceptions  # Import requests exceptions

from crudclient.exceptions import CrudClientError, NetworkError
from crudclient.http import (
    ExponentialBackoffStrategy,
    FixedRetryStrategy,
    RetryCondition,
    RetryEvent,
    RetryHandler,
)
from crudclient.testing.verification import Verifier
from tests.unit.helpers import translate_mock_calls_for_verifier


class TestRetryStrategies:
    """Tests for the retry strategies."""

    def test_fixed_retry_strategy(self) -> None:
        """Test that the fixed retry strategy returns the same delay for each attempt."""
        strategy = FixedRetryStrategy(delay=2.0)
        assert strategy.get_delay(1) == 2.0
        assert strategy.get_delay(2) == 2.0
        assert strategy.get_delay(3) == 2.0

    def test_exponential_backoff_strategy(self) -> None:
        """Test that the exponential backoff strategy increases the delay exponentially."""
        strategy = ExponentialBackoffStrategy(base_delay=1.0, max_delay=10.0, factor=2.0, jitter=False)
        assert strategy.get_delay(1) == 1.0
        assert strategy.get_delay(2) == 2.0
        assert strategy.get_delay(3) == 4.0
        assert strategy.get_delay(4) == 8.0
        assert strategy.get_delay(5) == 10.0

    def test_exponential_backoff_with_jitter(self) -> None:
        """Test that the exponential backoff strategy adds jitter when enabled."""
        strategy = ExponentialBackoffStrategy(base_delay=1.0, max_delay=10.0, factor=2.0, jitter=True)
        delay1 = strategy.get_delay(3)
        delay2 = strategy.get_delay(3)
        assert delay1 != delay2
        assert 3.0 <= delay1 <= 6.0
        assert 3.0 <= delay2 <= 6.0


class TestRetryCondition:
    """Tests for the retry condition class."""

    def test_retry_on_status_code(self) -> None:
        """Test that the retry condition correctly identifies status codes to retry on."""
        condition = RetryCondition(status_codes=[500, 502, 503])

        response_500 = MagicMock(spec=requests.Response)
        response_500.status_code = 500

        response_404 = MagicMock(spec=requests.Response)
        response_404.status_code = 404

        assert condition.should_retry(response_500) is True
        assert condition.should_retry(response_404) is False

    def test_retry_on_exception(self) -> None:
        """Test that the retry condition correctly identifies exceptions to retry on."""
        condition = RetryCondition(exceptions=[requests.Timeout, requests.ConnectionError])

        assert condition.should_retry(exception=requests.Timeout()) is True
        assert condition.should_retry(exception=requests.ConnectionError()) is True
        assert condition.should_retry(exception=ValueError()) is False

    def test_retry_on_event(self) -> None:
        """Test that the retry condition correctly handles RetryEvent enums."""
        condition = RetryCondition(events=[RetryEvent.SERVER_ERROR, RetryEvent.TIMEOUT])

        response_500 = MagicMock(spec=requests.Response)
        response_500.status_code = 500

        assert condition.should_retry(response_500) is True
        assert condition.should_retry(exception=requests.Timeout()) is True

    def test_custom_retry_condition(self) -> None:
        """Test that custom retry conditions work correctly."""

        def custom_condition(response: Optional[requests.Response], exception: Optional[BaseException]) -> bool:
            if response and response.headers.get("Retry-After"):
                return True
            return False

        condition = RetryCondition(custom_condition=custom_condition)

        response_with_header = MagicMock(spec=requests.Response)
        response_with_header.headers = {"Retry-After": "30"}
        response_with_header.status_code = 200

        response_without_header = MagicMock(spec=requests.Response)
        response_without_header.headers = {}
        response_without_header.status_code = 200

        assert condition.should_retry(response_with_header) is True
        assert condition.should_retry(response_without_header) is False


class TestRetryHandler:
    """Tests for the retry handler class."""

    def test_should_retry_status_code(self, retry_handler: RetryHandler, mocker: MockerFixture) -> None:
        """Test that the retry handler correctly identifies status codes to retry on."""
        response_500 = mocker.Mock(spec=requests.Response)
        response_500.status_code = 500

        response_404 = mocker.Mock(spec=requests.Response)
        response_404.status_code = 404

        assert retry_handler.should_retry(0, response_500) is True
        assert retry_handler.should_retry(0, response_404) is False
        assert retry_handler.should_retry(3, response_500) is False

    def test_should_retry_exception(self, retry_handler: RetryHandler) -> None:
        """Test that the retry handler correctly identifies exceptions to retry on."""
        timeout_exception = requests.Timeout()
        connection_error = requests.ConnectionError()
        value_error = ValueError()

        assert retry_handler.should_retry(0, exception=timeout_exception) is True
        assert retry_handler.should_retry(0, exception=connection_error) is True
        assert retry_handler.should_retry(0, exception=value_error) is False
        assert retry_handler.should_retry(3, exception=timeout_exception) is False

    def test_get_delay(self) -> None:
        """Test that the retry handler correctly calculates the delay."""
        # Instantiate specific handler for this test
        retry_handler = RetryHandler(retry_strategy=FixedRetryStrategy(delay=0.01))

        assert retry_handler.get_delay(1) == 0.01
        assert retry_handler.get_delay(2) == 0.01
        assert retry_handler.get_delay(3) == 0.01

    def test_execute_with_retry_success_first_try(self, retry_handler: RetryHandler, mocker: MockerFixture) -> None:
        """Test that the retry handler returns the response if the first try succeeds."""
        mock_sleep = mocker.patch("time.sleep")
        mock_response = mocker.Mock(spec=requests.Response)
        mock_response.ok = True
        mock_response.status_code = 200  # Add status code for success
        request_func = mocker.Mock(return_value=mock_response)

        response, _ = retry_handler.execute_with_retry("GET", "http://test.com/retry", request_func)

        assert response == mock_response
        translate_mock_calls_for_verifier(request_func)
        Verifier.verify_call_count(request_func, "", 1)
        translate_mock_calls_for_verifier(mock_sleep)
        Verifier.verify_not_called(mock_sleep, "")

    def test_execute_with_retry_success_after_retry(self, mocker: MockerFixture) -> None:
        """Test that the retry handler retries and returns the response if a retry succeeds."""
        # Instantiate specific handler for this test
        # Use jitter=False for predictable delay, default base_delay is 0.5
        retry_handler = RetryHandler(retry_strategy=ExponentialBackoffStrategy(jitter=False))
        mock_sleep = mocker.patch("time.sleep")

        mock_error_response = mocker.Mock(spec=requests.Response)
        mock_error_response.ok = False
        mock_error_response.status_code = 500

        mock_success_response = mocker.Mock(spec=requests.Response)
        mock_success_response.ok = True
        mock_success_response.status_code = 200  # Add status code for success

        request_func = mocker.Mock(side_effect=[mock_error_response, mock_success_response])

        response, _ = retry_handler.execute_with_retry("GET", "http://test.com/retry", request_func)

        assert response == mock_success_response
        translate_mock_calls_for_verifier(request_func)
        Verifier.verify_call_count(request_func, "", 2)
        translate_mock_calls_for_verifier(mock_sleep)
        Verifier.verify_called_once_with(mock_sleep, "", 1.0)  # Expect default base delay (1.0)

    def test_execute_with_retry_all_failures(self, retry_handler: RetryHandler, mocker: MockerFixture) -> None:
        """Test that the retry handler raises an exception if all retries fail."""
        mock_sleep = mocker.patch("time.sleep")

        mock_error_response = mocker.Mock(spec=requests.Response)
        mock_error_response.ok = False
        mock_error_response.status_code = 500

        request_func = mocker.Mock(return_value=mock_error_response)

        response, _ = retry_handler.execute_with_retry("GET", "http://test.com/retry", request_func)

        assert response == mock_error_response
        translate_mock_calls_for_verifier(request_func)
        Verifier.verify_call_count(request_func, "", 4)
        translate_mock_calls_for_verifier(mock_sleep)
        Verifier.verify_call_count(mock_sleep, "", 3)

    # Modified test
    def test_execute_with_retry_exception_logs_error(
        self,
        retry_handler: RetryHandler,
        mocker: MockerFixture,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that the retry handler handles exceptions correctly and logs an error."""
        mock_sleep = mocker.patch("time.sleep")
        exception_instance = requests.Timeout("Connection timed out")
        request_func = mocker.Mock(side_effect=exception_instance)

        # Capture ERROR logs from the retry handler
        caplog.set_level(logging.ERROR, logger="crudclient.http.retry")

        with pytest.raises(CrudClientError) as excinfo:
            retry_handler.execute_with_retry("GET", "http://test.com/retry", request_func)

        assert "Connection timed out" in str(excinfo.value)
        translate_mock_calls_for_verifier(request_func)
        Verifier.verify_call_count(request_func, "", 4)  # Default max_retries is 3, so 4 attempts
        translate_mock_calls_for_verifier(mock_sleep)
        Verifier.verify_call_count(mock_sleep, "", 3)

        # Assert Log
        error_log_found = False
        for record in caplog.records:
            if (
                record.name == "crudclient.http.retry"
                and record.levelno == logging.ERROR
                and "Not retrying" in record.message  # Check for the correct message
                and "GET http://test.com/retry" in record.message
                and "after exception Timeout" in record.message
            ):  # Check for exception context
                error_log_found = True
                break
        assert error_log_found, "Expected ERROR log for exhausted retries due to exception not found"

    def test_execute_with_retry_non_retryable_exception(self, retry_handler: RetryHandler, mocker: MockerFixture) -> None:
        """Test that the retry handler doesn't retry on non-retryable exceptions."""
        mock_sleep = mocker.patch("time.sleep")

        request_func = mocker.Mock(side_effect=ValueError("Invalid value"))

        with pytest.raises(ValueError) as excinfo:
            retry_handler.execute_with_retry("GET", "http://test.com/retry", request_func)

        assert "Invalid value" in str(excinfo.value)
        translate_mock_calls_for_verifier(request_func)
        Verifier.verify_call_count(request_func, "", 1)
        translate_mock_calls_for_verifier(mock_sleep)
        Verifier.verify_not_called(mock_sleep, "")

    def test_retry_on_403_configured(self, mocker: MockerFixture) -> None:
        """Test execute_with_retry retries on 403 if configured, but doesn't call setup_auth."""
        mock_sleep = mocker.patch("time.sleep")
        setup_auth_func = mocker.Mock()

        response_403 = mocker.Mock(spec=requests.Response)
        response_403.ok = False
        response_403.status_code = 403

        response_ok = mocker.Mock(spec=requests.Response)
        response_ok.ok = True
        response_ok.status_code = 200

        request_func = mocker.Mock(side_effect=[response_403, response_ok])

        retry_handler = RetryHandler(
            max_retries=1,
            retry_strategy=FixedRetryStrategy(delay=0.01),
            retry_conditions=[RetryCondition(status_codes=[403])],
        )

        response, attempts = retry_handler.execute_with_retry("GET", "http://test.com/retry", request_func, setup_auth_func=setup_auth_func)

        assert response == response_ok
        assert attempts == 2
        translate_mock_calls_for_verifier(request_func)
        Verifier.verify_call_count(request_func, "", 2)
        translate_mock_calls_for_verifier(setup_auth_func)
        Verifier.verify_not_called(setup_auth_func, "")
        translate_mock_calls_for_verifier(mock_sleep)
        Verifier.verify_called_once_with(mock_sleep, "", 0.01)

    def test_no_retry_on_404_when_403_configured(self, mocker: MockerFixture) -> None:
        """Test execute_with_retry doesn't retry on 404 if only 403 is configured."""
        mock_sleep = mocker.patch("time.sleep")
        setup_auth_func = mocker.Mock()

        response_404 = mocker.Mock(spec=requests.Response)
        response_404.ok = False
        response_404.status_code = 404

        request_func = mocker.Mock(return_value=response_404)

        retry_handler = RetryHandler(
            max_retries=1,
            retry_strategy=FixedRetryStrategy(delay=0.01),
            retry_conditions=[RetryCondition(status_codes=[403])],
        )

        response, attempts = retry_handler.execute_with_retry("GET", "http://test.com/retry", request_func, setup_auth_func=setup_auth_func)

        assert response == response_404
        assert attempts == 1
        translate_mock_calls_for_verifier(request_func)
        Verifier.verify_call_count(request_func, "", 1)
        translate_mock_calls_for_verifier(setup_auth_func)
        Verifier.verify_not_called(setup_auth_func, "")
        translate_mock_calls_for_verifier(mock_sleep)
        Verifier.verify_not_called(mock_sleep, "")

    def test_on_retry_callback(self, mocker: MockerFixture) -> None:
        """Test that the on_retry_callback is called correctly."""
        mocker.patch("time.sleep")
        callback = mocker.Mock()

        retry_handler = RetryHandler(
            max_retries=2,
            retry_strategy=FixedRetryStrategy(delay=0.01),
            retry_conditions=[RetryCondition(status_codes=[500])],
            on_retry_callback=callback,
        )

        mock_error_response = mocker.Mock(spec=requests.Response)
        mock_error_response.ok = False
        mock_error_response.status_code = 500

        request_func = mocker.Mock(return_value=mock_error_response)

        retry_handler.execute_with_retry("GET", "http://test.com/retry", request_func)

        translate_mock_calls_for_verifier(callback)
        Verifier.verify_call_count(callback, "", 2)

        translate_mock_calls_for_verifier(callback)
        Verifier.verify_any_call(callback, "", 1, 0.01, mock_error_response, None)

        translate_mock_calls_for_verifier(callback)
        Verifier.verify_any_call(callback, "", 2, 0.01, mock_error_response, None)

    def test_execute_with_retry_raises_network_error(self, retry_handler: RetryHandler, mocker: MockerFixture) -> None:
        """Test that NetworkError is raised for requests.exceptions.RequestException."""
        mock_sleep = mocker.patch("time.sleep")
        original_exception = requests_exceptions.ConnectionError("Failed to connect")
        request_func = mocker.Mock(side_effect=original_exception)
        method = "GET"
        url = "http://test.com/network-error"

        # No need to mock requests.Request as the handler currently doesn't capture it on network errors

        with pytest.raises(NetworkError) as excinfo:
            retry_handler.execute_with_retry(method, url, request_func)

        # Assert NetworkError attributes
        assert excinfo.value.original_exception is original_exception
        # apiconfig's NetworkError doesn't have a request attribute
        # Just check the error message contains the expected text
        assert "Failed to connect" in str(excinfo.value)

        # Assert retry attempts
        translate_mock_calls_for_verifier(request_func)
        Verifier.verify_call_count(request_func, "", 4)  # Default max_retries is 3 -> 4 attempts
        translate_mock_calls_for_verifier(mock_sleep)
        Verifier.verify_call_count(mock_sleep, "", 3)

import logging  # &lt;-- Add import
from unittest.mock import MagicMock

import pytest
import requests_mock
from pytest_mock import MockerFixture

from crudclient.exceptions import InternalServerError  # Corrected name
from crudclient.exceptions import (
    APIError,
    BadRequestError,
    ClientAuthenticationError,
    ConflictError,
    CrudClientError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    UnprocessableEntityError,
)
from crudclient.http.client import HttpClient
from crudclient.http.errors import ErrorHandler

# Ensure HttpLifecycleLogger is imported if needed for type hints or direct use (though likely not needed here)
# from crudclient.http.logging import HttpLifecycleLogger
from crudclient.http.request import RequestFormatter
from crudclient.http.response import ResponseHandler
from crudclient.http.retry import RetryHandler
from crudclient.http.session import SessionManager
from crudclient.testing.verification import Verifier
from tests.unit.helpers import translate_mock_calls_for_verifier

# Import fixtures from conftest.py


class TestHttpClient:

    def test_http_client_initialization(self, http_client: HttpClient, mock_client_config: MagicMock) -> None:
        """Test that the HttpClient is initialized correctly with all components."""
        # Arrange - done via fixtures

        # Act - HttpClient is already instantiated via fixture

        # Assert
        assert http_client.config == mock_client_config
        assert isinstance(http_client.session_manager, SessionManager)
        assert isinstance(http_client.request_formatter, RequestFormatter)
        assert isinstance(http_client.response_handler, ResponseHandler)
        assert isinstance(http_client.error_handler, ErrorHandler)
        assert isinstance(http_client.retry_handler, RetryHandler)

    def test_get_request(self, http_client: HttpClient, requests_mock: requests_mock.Mocker) -> None:
        """Test that the get method makes a GET request to the correct URL."""
        # Arrange
        endpoint = "users"
        url = f"{http_client.config.base_url}/{endpoint}"
        requests_mock.get(url, json={"status": "success"})

        # Act
        response = http_client.get(endpoint)

        # Assert
        assert response == '{"status": "success"}'

    def test_post_request(self, http_client: HttpClient, requests_mock: requests_mock.Mocker) -> None:
        """Test that the post method makes a POST request to the correct URL."""
        # Arrange
        endpoint = "users"
        data = {"name": "John Doe"}
        url = f"{http_client.config.base_url}/{endpoint}"
        requests_mock.post(url, json={"status": "success"})

        # Act
        response = http_client.post(endpoint, data=data)

        # Assert
        assert response == '{"status": "success"}'

    def test_put_request(self, http_client: HttpClient, requests_mock: requests_mock.Mocker) -> None:
        """Test that the put method makes a PUT request to the correct URL."""
        # Arrange
        endpoint = "users/1"
        data = {"name": "John Doe"}
        url = f"{http_client.config.base_url}/{endpoint}"
        requests_mock.put(url, json={"status": "success"})

        # Act
        response = http_client.put(endpoint, data=data)

        # Assert
        assert response == '{"status": "success"}'

    def test_delete_request(self, http_client: HttpClient, requests_mock: requests_mock.Mocker) -> None:
        """Test that the delete method makes a DELETE request to the correct URL."""
        # Arrange
        endpoint = "users/1"
        url = f"{http_client.config.base_url}/{endpoint}"
        requests_mock.delete(url, json={"status": "success"})

        # Act
        response = http_client.delete(endpoint)

        # Assert
        assert response == '{"status": "success"}'

    def test_patch_request(self, http_client: HttpClient, requests_mock: requests_mock.Mocker) -> None:
        """Test that the patch method makes a PATCH request to the correct URL."""
        # Arrange
        endpoint = "users/1"
        data = {"name": "John Doe"}
        url = f"{http_client.config.base_url}/{endpoint}"
        requests_mock.patch(url, json={"status": "success"})

        # Act
        response = http_client.patch(endpoint, data=data)

        # Assert
        assert response == '{"status": "success"}'

    # Modified test
    def test_request_with_server_error_logs_error(
        self,
        http_client: HttpClient,
        requests_mock: requests_mock.Mocker,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that server errors are handled correctly and logged at ERROR level."""
        # Arrange
        endpoint = "users"
        url = f"{http_client.config.base_url}/{endpoint}"
        response_text = '{"error": "Server error"}'
        requests_mock.get(url, status_code=500, text=response_text)
        caplog.set_level(logging.ERROR, logger="crudclient.http.client")  # Capture ERROR logs

        # Act & Assert
        with pytest.raises(CrudClientError):
            http_client.get(endpoint)

        # Assert Log
        error_log_found = False
        for record in caplog.records:
            if (
                record.name == "crudclient.http.client"
                and record.levelno == logging.ERROR
                and "HTTP error encountered for GET" in record.message
                and url in record.message
                and "Status 500" in record.message
                and response_text in record.message
            ):
                error_log_found = True
                break
        assert error_log_found, "Expected ERROR log message not found"

    # New test for 4xx logging

    def test_request_logs_http_error_4xx(
        self,
        http_client: HttpClient,
        requests_mock: requests_mock.Mocker,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that 4xx HTTP errors are logged at WARNING level."""
        # Arrange
        endpoint = "users/missing"
        url = f"{http_client.config.base_url}/{endpoint}"
        response_text = '{"detail": "Not found here"}'
        requests_mock.get(url, status_code=404, text=response_text)
        caplog.set_level(logging.WARNING, logger="crudclient.http.client")  # Capture WARNING logs

        # Act & Assert
        with pytest.raises(NotFoundError):  # Expect NotFoundError for 404
            http_client.get(endpoint)

        # Assert Log
        warning_log_found = False
        for record in caplog.records:
            if (
                record.name == "crudclient.http.client"
                and record.levelno == logging.WARNING
                and "HTTP error encountered for GET" in record.message
                and url in record.message
                and "Status 404" in record.message
                and response_text in record.message
            ):
                warning_log_found = True
                break
        assert warning_log_found, "Expected WARNING log message not found"

    def test_request_with_no_content(self, http_client: HttpClient, requests_mock: requests_mock.Mocker) -> None:
        """Test that 204 No Content responses return None."""
        # Arrange
        endpoint = "users/1"
        url = f"{http_client.config.base_url}/{endpoint}"
        requests_mock.delete(url, status_code=204)

        # Act
        response = http_client.delete(endpoint)

        # Assert
        assert response is None

    def test_close(self, http_client: HttpClient, mocker: MockerFixture) -> None:
        """Test that the close method closes the session."""
        # Arrange
        mock_close = mocker.patch.object(http_client.session_manager, "close")

        # Act
        http_client.close()

        # Assert
        translate_mock_calls_for_verifier(mock_close)
        Verifier.verify_call_count(mock_close, "", 1)

    @pytest.mark.parametrize(
        "status_code, expected_exception",
        [
            (400, BadRequestError),
            (401, ClientAuthenticationError),
            (403, ForbiddenError),
            (404, NotFoundError),
            (409, ConflictError),
            (422, UnprocessableEntityError),
            (429, RateLimitError),
            (500, InternalServerError),  # Corrected name
            (503, ServiceUnavailableError),
            (418, APIError),  # Generic APIError for unmapped 4xx/5xx
        ],
    )
    def test_api_error_subclasses_raised(
        self,
        http_client: HttpClient,
        requests_mock: requests_mock.Mocker,
        status_code: int,
        expected_exception: type[APIError],
    ) -> None:
        """Test that specific APIError subclasses are raised for HTTP status codes."""
        # Arrange
        endpoint = f"test/{status_code}"
        url = f"{http_client.config.base_url}/{endpoint}"
        response_json = {"error": f"Error {status_code}"}
        requests_mock.get(url, status_code=status_code, json=response_json)

        # Act & Assert
        with pytest.raises(expected_exception) as excinfo:
            http_client.get(endpoint)

        # Assert exception attributes
        assert isinstance(excinfo.value, APIError)  # All are APIErrors
        assert excinfo.value.request is not None
        # Check for attributes common to requests.Request/PreparedRequest and the mock proxy
        assert hasattr(excinfo.value.request, "method")
        assert hasattr(excinfo.value.request, "url")
        assert excinfo.value.response is not None
        # Don't check isinstance as HttpResponseProtocol and requests.Response are incompatible
        assert excinfo.value.response.status_code == status_code
        assert excinfo.value.response.request == excinfo.value.request

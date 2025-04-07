from unittest.mock import patch

import pytest
import requests_mock

from crudclient.exceptions import AuthenticationError, CrudClientError, NotFoundError
from crudclient.http.client import HttpClient
from crudclient.http.errors import ErrorHandler
from crudclient.http.request import RequestFormatter
from crudclient.http.response import ResponseHandler
from crudclient.http.retry import RetryHandler
from crudclient.http.session import SessionManager

from .test_config import MockClientConfig


class TestHttpClient:
    @pytest.fixture
    def config(self):
        return MockClientConfig()

    @pytest.fixture
    def http_client(self, config):
        return HttpClient(config)

    @pytest.fixture
    def mock_request(self):
        with requests_mock.Mocker() as m:
            yield m

    def test_http_client_initialization(self, http_client, config):
        """Test that the HttpClient is initialized correctly with all components."""
        assert http_client.config == config
        assert isinstance(http_client.session_manager, SessionManager)
        assert isinstance(http_client.request_formatter, RequestFormatter)
        assert isinstance(http_client.response_handler, ResponseHandler)
        assert isinstance(http_client.error_handler, ErrorHandler)
        assert isinstance(http_client.retry_handler, RetryHandler)

    def test_get_request(self, http_client, mock_request):
        """Test that the get method makes a GET request to the correct URL."""
        endpoint = "users"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.get(url, json={"status": "success"})

        response = http_client.get(endpoint)
        assert response == '{"status": "success"}'

    def test_post_request(self, http_client, mock_request):
        """Test that the post method makes a POST request to the correct URL."""
        endpoint = "users"
        data = {"name": "John Doe"}
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.post(url, json={"status": "success"})

        response = http_client.post(endpoint, data=data)
        assert response == '{"status": "success"}'

    def test_put_request(self, http_client, mock_request):
        """Test that the put method makes a PUT request to the correct URL."""
        endpoint = "users/1"
        data = {"name": "John Doe"}
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.put(url, json={"status": "success"})

        response = http_client.put(endpoint, data=data)
        assert response == '{"status": "success"}'

    def test_delete_request(self, http_client, mock_request):
        """Test that the delete method makes a DELETE request to the correct URL."""
        endpoint = "users/1"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.delete(url, json={"status": "success"})

        response = http_client.delete(endpoint)
        assert response == '{"status": "success"}'

    def test_patch_request(self, http_client, mock_request):
        """Test that the patch method makes a PATCH request to the correct URL."""
        endpoint = "users/1"
        data = {"name": "John Doe"}
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.patch(url, json={"status": "success"})

        response = http_client.patch(endpoint, data=data)
        assert response == '{"status": "success"}'

    def test_request_with_error(self, http_client, mock_request):
        """Test that errors are handled correctly."""
        endpoint = "users/999"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.get(url, status_code=404, json={"error": "Not found"})

        with pytest.raises(NotFoundError):
            http_client.get(endpoint)

    def test_request_with_auth_error(self, http_client, mock_request):
        """Test that authentication errors are handled correctly."""
        endpoint = "users"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.get(url, status_code=401, json={"error": "Unauthorized"})

        with pytest.raises(AuthenticationError):
            http_client.get(endpoint)

    def test_request_with_server_error(self, http_client, mock_request):
        """Test that server errors are handled correctly."""
        endpoint = "users"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.get(url, status_code=500, json={"error": "Server error"})

        with pytest.raises(CrudClientError):
            http_client.get(endpoint)

    def test_request_with_no_content(self, http_client, mock_request):
        """Test that 204 No Content responses are handled correctly."""
        endpoint = "users/1"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.delete(url, status_code=204)

        response = http_client.delete(endpoint)
        assert response is None

    def test_close(self, http_client):
        """Test that the close method closes the session."""
        with patch.object(http_client.session_manager, 'close') as mock_close:
            http_client.close()
            mock_close.assert_called_once()

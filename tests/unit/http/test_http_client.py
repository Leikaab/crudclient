import pytest

from crudclient.exceptions import AuthenticationError, CrudClientError, NotFoundError
from crudclient.http.errors import ErrorHandler
from crudclient.http.request import RequestFormatter
from crudclient.http.response import ResponseHandler
from crudclient.http.retry import RetryHandler
from crudclient.http.session import SessionManager

# Import fixtures from conftest.py


class TestHttpClient:

    def test_http_client_initialization(self, http_client, config):
        """Test that the HttpClient is initialized correctly with all components."""
        # Arrange - done via fixtures

        # Act - HttpClient is already instantiated via fixture

        # Assert
        assert http_client.config == config
        assert isinstance(http_client.session_manager, SessionManager)
        assert isinstance(http_client.request_formatter, RequestFormatter)
        assert isinstance(http_client.response_handler, ResponseHandler)
        assert isinstance(http_client.error_handler, ErrorHandler)
        assert isinstance(http_client.retry_handler, RetryHandler)

    def test_get_request(self, http_client, mock_request):
        """Test that the get method makes a GET request to the correct URL."""
        # Arrange
        endpoint = "users"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.get(url, json={"status": "success"})

        # Act
        response = http_client.get(endpoint)

        # Assert
        assert response == '{"status": "success"}'

    def test_post_request(self, http_client, mock_request):
        """Test that the post method makes a POST request to the correct URL."""
        # Arrange
        endpoint = "users"
        data = {"name": "John Doe"}
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.post(url, json={"status": "success"})

        # Act
        response = http_client.post(endpoint, data=data)

        # Assert
        assert response == '{"status": "success"}'

    def test_put_request(self, http_client, mock_request):
        """Test that the put method makes a PUT request to the correct URL."""
        # Arrange
        endpoint = "users/1"
        data = {"name": "John Doe"}
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.put(url, json={"status": "success"})

        # Act
        response = http_client.put(endpoint, data=data)

        # Assert
        assert response == '{"status": "success"}'

    def test_delete_request(self, http_client, mock_request):
        """Test that the delete method makes a DELETE request to the correct URL."""
        # Arrange
        endpoint = "users/1"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.delete(url, json={"status": "success"})

        # Act
        response = http_client.delete(endpoint)

        # Assert
        assert response == '{"status": "success"}'

    def test_patch_request(self, http_client, mock_request):
        """Test that the patch method makes a PATCH request to the correct URL."""
        # Arrange
        endpoint = "users/1"
        data = {"name": "John Doe"}
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.patch(url, json={"status": "success"})

        # Act
        response = http_client.patch(endpoint, data=data)

        # Assert
        assert response == '{"status": "success"}'

    def test_request_with_error(self, http_client, mock_request):
        """Test that errors are handled correctly."""
        # Arrange
        endpoint = "users/999"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.get(url, status_code=404, json={"error": "Not found"})

        # Act & Assert
        with pytest.raises(NotFoundError):
            http_client.get(endpoint)

    def test_request_with_auth_error(self, http_client, mock_request):
        """Test that authentication errors are handled correctly."""
        # Arrange
        endpoint = "users"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.get(url, status_code=401, json={"error": "Unauthorized"})

        # Act & Assert
        with pytest.raises(AuthenticationError):
            http_client.get(endpoint)

    def test_request_with_server_error(self, http_client, mock_request):
        """Test that server errors are handled correctly."""
        # Arrange
        endpoint = "users"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.get(url, status_code=500, json={"error": "Server error"})

        # Act & Assert
        with pytest.raises(CrudClientError):
            http_client.get(endpoint)

    def test_request_with_no_content(self, http_client, mock_request):
        """Test that 204 No Content responses are handled correctly."""
        # Arrange
        endpoint = "users/1"
        url = f"{http_client.config.base_url}/{endpoint}"
        mock_request.delete(url, status_code=204)

        # Act
        response = http_client.delete(endpoint)

        # Assert
        assert response is None

    def test_close(self, http_client, mocker):
        """Test that the close method closes the session."""
        # Arrange
        mock_close = mocker.patch.object(http_client.session_manager, "close")

        # Act
        http_client.close()

        # Assert
        mock_close.assert_called_once()

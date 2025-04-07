import pytest

# Import fixtures from conftest.py


class TestClient:

    def test_no_url_get(self, client, mock_request):
        # Arrange
        endpoint = None
        # We need to mock the URL that would be constructed with an empty endpoint
        url = f"{client.base_url}/"
        mock_request.get(url, status_code=200)

        # Act & Assert
        with pytest.raises(TypeError):
            client.get(endpoint)

    def test_get(self, client, mock_request):
        # Arrange
        endpoint = "/users"
        params = {"page": 1}
        url = f"{client.base_url}/{endpoint.lstrip('/')}"
        mock_request.get(url, json={"status": "success"})

        # Act
        response = client.get(endpoint, params=params)

        # Assert
        assert response == '{"status": "success"}'

    def test_post(self, client, mock_request):
        # Arrange
        endpoint = "/users"
        data = {"name": "John Doe"}
        url = f"{client.base_url}/{endpoint.lstrip('/')}"
        mock_request.post(url, json={"status": "success"})

        # Act
        response = client.post(endpoint, data=data)

        # Assert
        assert response == '{"status": "success"}'

    def test_put(self, client, mock_request):
        # Arrange
        endpoint = "/users/1"
        data = {"name": "John Doe"}
        url = f"{client.base_url}/{endpoint.lstrip('/')}"
        mock_request.put(url, json={"status": "success"})

        # Act
        response = client.put(endpoint, data=data)

        # Assert
        assert response == '{"status": "success"}'

    def test_delete(self, client, mock_request):
        # Arrange
        endpoint = "/users/1"
        url = f"{client.base_url}/{endpoint.lstrip('/')}"
        mock_request.delete(url, json={"status": "success"})

        # Act
        response = client.delete(endpoint)

        # Assert
        assert response == '{"status": "success"}'

    def test_patch(self, client, mock_request):
        # Arrange
        endpoint = "/users/1"
        data = {"name": "John Doe"}
        url = f"{client.base_url}/{endpoint.lstrip('/')}"
        mock_request.patch(url, json={"status": "success"})

        # Act
        response = client.patch(endpoint, data=data)

        # Assert
        assert response == '{"status": "success"}'

    def test_close(self, client):
        # Arrange

        # Act
        client.close()

        # Assert
        assert client.session.close() is None

import pytest
import requests_mock

from crudclient.client import Client
from crudclient.config import ClientConfig


class MockClientConfig(ClientConfig):
    def __init__(self):
        self.base_url = "https://api.example.com"
        self.headers = {"Authorization": "Bearer token"}
        self.api_key = "mykey"
        self.retries = 3
        self.timeout = 5


class TestClient:
    @pytest.fixture
    def client(self):
        # Create a mock config for the client
        config = MockClientConfig()
        return Client(config)

    @pytest.fixture
    def mock_request(self):
        with requests_mock.Mocker() as m:
            yield m

    def test_get(self, client, mock_request):
        # Mock the request to the API
        endpoint = "/users"
        params = {"page": 1}
        url = f"{client.base_url}{endpoint}"

        # Simulate a successful response from the API
        mock_request.get(url, json={"status": "success"})

        # Test the get method
        response = client.get(endpoint, params=params)
        assert response == '{"status": "success"}'

    def test_post(self, client, mock_request):
        # Mock the POST request to the API
        endpoint = "/users"
        data = {"name": "John Doe"}
        url = f"{client.base_url}{endpoint}"

        # Simulate a successful response from the API for POST
        mock_request.post(url, json={"status": "success"})

        # Test the post method
        response = client.post(endpoint, data=data)
        assert response == '{"status": "success"}'

    def test_put(self, client, mock_request):
        # Mock the PUT request to the API
        endpoint = "/users/1"
        data = {"name": "John Doe"}
        url = f"{client.base_url}{endpoint}"

        # Simulate a successful response from the API for PUT
        mock_request.put(url, json={"status": "success"})

        # Test the put method
        response = client.put(endpoint, data=data)
        assert response == '{"status": "success"}'

    def test_delete(self, client, mock_request):
        # Mock the DELETE request to the API
        endpoint = "/users/1"
        url = f"{client.base_url}{endpoint}"

        # Simulate a successful response from the API for DELETE
        mock_request.delete(url, json={"status": "success"})

        # Test the delete method
        response = client.delete(endpoint)
        assert response == '{"status": "success"}'

    def test_patch(self, client, mock_request):
        # Mock the PATCH request to the API
        endpoint = "/users/1"
        data = {"name": "John Doe"}
        url = f"{client.base_url}{endpoint}"

        # Simulate a successful response from the API for PATCH
        mock_request.patch(url, json={"status": "success"})

        # Test the patch method
        response = client.patch(endpoint, data=data)
        assert response == '{"status": "success"}'

    def test_close(self, client):
        # Test the close method
        client.close()
        assert client.session.close() is None

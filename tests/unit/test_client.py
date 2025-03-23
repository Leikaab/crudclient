import pytest  # noqa F401

from .test_client_auth import TestClientAuth


class TestClient(TestClientAuth):

    def test_no_url_get(self, client, mock_request):
        # Mock the request to the API
        endpoint = None
        with pytest.raises(ValueError):
            client.get(endpoint)

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

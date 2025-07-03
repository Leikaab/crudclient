import requests_mock

from crudclient.client import Client

"""
Tests for client error handling in the HTTP client.

This module contains tests for how the HTTP client handles various client error conditions,
including 4xx status codes.
"""

from typing import cast

import pytest
import requests

from crudclient.exceptions import (
    APIError,
    AuthenticationError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)


class TestHttpClientClientErrors:
    """Tests for handling client errors in the HTTP client."""

    def test_400_error(self, http_client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        Test handling of 400 Bad Request.

        This test verifies that the client properly handles 400 Bad Request
        responses from the server.
        """
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=400, json={"error": "Bad Request", "message": "Invalid parameters"})

        with pytest.raises(APIError) as excinfo:
            http_client.get("/users")

        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 400
        # Cast to requests.Response to access json() method
        response = cast(requests.Response, excinfo.value.response)
        assert response.json()["message"] == "Invalid parameters"

    def test_401_error(self, http_client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        Test handling of 401 Unauthorized.

        This test verifies that the client properly handles 401 Unauthorized
        responses from the server and raises an AuthenticationError.
        """
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Authentication required"})

        with pytest.raises(AuthenticationError) as excinfo:
            http_client.get("/users")

        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 401
        # Cast to requests.Response to access json() method
        response = cast(requests.Response, excinfo.value.response)
        assert response.json()["message"] == "Authentication required"

    def test_403_error(self, http_client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        Test handling of 403 Forbidden.

        This test verifies that the client properly handles 403 Forbidden
        responses from the server and raises an AuthenticationError.
        """
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=403, json={"error": "Forbidden", "message": "Insufficient permissions"})

        with pytest.raises(ForbiddenError) as excinfo:
            http_client.get("/users")

        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 403
        # Cast to requests.Response to access json() method
        response = cast(requests.Response, excinfo.value.response)
        assert response.json()["message"] == "Insufficient permissions"

    def test_404_error(self, http_client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        Test handling of 404 Not Found.

        This test verifies that the client properly handles 404 Not Found
        responses from the server and raises a NotFoundError.
        """
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=404, json={"error": "Not Found", "message": "Resource not found"})

        with pytest.raises(NotFoundError) as excinfo:
            http_client.get("/users")

        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 404
        # Cast to requests.Response to access json() method
        response = cast(requests.Response, excinfo.value.response)
        assert response.json()["message"] == "Resource not found"

    def test_422_error(self, http_client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        Test handling of 422 Unprocessable Entity.

        This test verifies that the client properly handles 422 Unprocessable Entity
        responses from the server and raises an InvalidResponseError.
        """
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=422, json={"error": "Unprocessable Entity", "message": "Validation failed"})

        with pytest.raises(UnprocessableEntityError) as excinfo:
            http_client.get("/users")

        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 422
        # Cast to requests.Response to access json() method
        response = cast(requests.Response, excinfo.value.response)
        assert response.json()["message"] == "Validation failed"

    def test_429_error(self, http_client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        Test handling of 429 Too Many Requests.

        This test verifies that the client properly handles 429 Too Many Requests
        responses from the server.
        """
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=429, json={"error": "Too Many Requests", "message": "Rate limit exceeded"})

        with pytest.raises(APIError) as excinfo:
            http_client.get("/users")

        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 429
        # Cast to requests.Response to access json() method
        response = cast(requests.Response, excinfo.value.response)
        assert response.json()["message"] == "Rate limit exceeded"

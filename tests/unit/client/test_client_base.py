from typing import Any

import pytest
import requests_mock

from crudclient.client import Client

# Import fixtures from conftest.py


class TestClient:

    def test_no_url_get(self, client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        GIVEN a client and a mocked request
        WHEN attempting a GET request with a None endpoint
        THEN a TypeError should be raised.
        """
        # GIVEN
        endpoint = None
        url = f"{client.base_url}/"
        mock_request.get(url, status_code=200)  # Mock to prevent actual HTTP call

        # WHEN / THEN
        with pytest.raises(TypeError):
            client.get(endpoint)  # type: ignore[arg-type]

    def test_get(self, client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        GIVEN a client, a mocked request, an endpoint, and parameters
        WHEN a GET request is made to the endpoint
        THEN the response should match the mocked JSON response.
        """
        # GIVEN
        endpoint = "/users"
        params = {"page": 1}
        expected_response_json = {"status": "success"}
        url = f"{client.base_url}/{endpoint.lstrip('/')}"
        mock_request.get(url, json=expected_response_json)

        # WHEN
        response = client.get(endpoint, params=params)

        # THEN
        assert response == '{"status": "success"}'  # Assuming default strategy returns raw text

    def test_post(self, client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        GIVEN a client, a mocked request, an endpoint, and data
        WHEN a POST request is made to the endpoint with the data
        THEN the response should match the mocked JSON response.
        """
        # GIVEN
        endpoint = "/users"
        data = {"name": "John Doe"}
        expected_response_json = {"status": "success"}
        url = f"{client.base_url}/{endpoint.lstrip('/')}"
        mock_request.post(url, json=expected_response_json)

        # WHEN
        response = client.post(endpoint, data=data)

        # THEN
        assert response == '{"status": "success"}'

    def test_put(self, client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        GIVEN a client, a mocked request, an endpoint, and data
        WHEN a PUT request is made to the endpoint with the data
        THEN the response should match the mocked JSON response.
        """
        # GIVEN
        endpoint = "/users/1"
        data = {"name": "John Doe"}
        expected_response_json = {"status": "success"}
        url = f"{client.base_url}/{endpoint.lstrip('/')}"
        mock_request.put(url, json=expected_response_json)

        # WHEN
        response = client.put(endpoint, data=data)

        # THEN
        assert response == '{"status": "success"}'

    def test_delete(self, client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        GIVEN a client, a mocked request, and an endpoint
        WHEN a DELETE request is made to the endpoint
        THEN the response should match the mocked JSON response.
        """
        # GIVEN
        endpoint = "/users/1"
        expected_response_json = {"status": "success"}
        url = f"{client.base_url}/{endpoint.lstrip('/')}"
        mock_request.delete(url, json=expected_response_json)

        # WHEN
        response = client.delete(endpoint)

        # THEN
        assert response == '{"status": "success"}'

    def test_patch(self, client: Client, mock_request: requests_mock.Mocker) -> None:
        """
        GIVEN a client, a mocked request, an endpoint, and data
        WHEN a PATCH request is made to the endpoint with the data
        THEN the response should match the mocked JSON response.
        """
        # GIVEN
        endpoint = "/users/1"
        data = {"name": "John Doe"}
        expected_response_json = {"status": "success"}
        url = f"{client.base_url}/{endpoint.lstrip('/')}"
        mock_request.patch(url, json=expected_response_json)

        # WHEN
        response = client.patch(endpoint, data=data)

        # THEN
        assert response == '{"status": "success"}'

    # --- Type Error Tests ---

    @pytest.mark.parametrize("invalid_endpoint", [123, None, True, []])
    def test_get_invalid_endpoint_type(self, client: Client, invalid_endpoint: Any) -> None:
        """
        GIVEN a client and an invalid endpoint type (non-string)
        WHEN a GET request is attempted with the invalid endpoint
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid endpoint type

        # WHEN / THEN
        with pytest.raises(TypeError, match="endpoint must be a string"):
            client.get(invalid_endpoint)  # type: ignore[arg-type]

    @pytest.mark.parametrize("invalid_params", [123, "string", True, []])
    def test_get_invalid_params_type(self, client: Client, invalid_params: Any) -> None:
        """
        GIVEN a client and invalid params type (non-dict/None)
        WHEN a GET request is attempted with the invalid params
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid params type

        # WHEN / THEN
        with pytest.raises(TypeError, match="params must be a dictionary or None"):
            client.get("/users", params=invalid_params)

    @pytest.mark.parametrize("invalid_endpoint", [123, None, True, []])
    def test_post_invalid_endpoint_type(self, client: Client, invalid_endpoint: Any) -> None:
        """
        GIVEN a client and an invalid endpoint type (non-string)
        WHEN a POST request is attempted with the invalid endpoint
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid endpoint type

        # WHEN / THEN
        with pytest.raises(TypeError, match="endpoint must be a string"):
            client.post(invalid_endpoint)  # type: ignore[arg-type]

    @pytest.mark.parametrize("invalid_data", [123, "string", True, []])
    def test_post_invalid_data_type(self, client: Client, invalid_data: Any) -> None:
        """
        GIVEN a client and invalid data type (non-dict/None)
        WHEN a POST request is attempted with the invalid data
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid data type

        # WHEN / THEN
        with pytest.raises(TypeError, match="data must be a dictionary or None"):
            client.post("/users", data=invalid_data)

    @pytest.mark.parametrize("invalid_files", [123, "string", True, []])
    def test_post_invalid_files_type(self, client: Client, invalid_files: Any) -> None:
        """
        GIVEN a client and invalid files type (non-dict/None)
        WHEN a POST request is attempted with the invalid files
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid files type

        # WHEN / THEN
        with pytest.raises(TypeError, match="files must be a dictionary or None"):
            client.post("/users", files=invalid_files)

    @pytest.mark.parametrize("invalid_endpoint", [123, None, True, []])
    def test_put_invalid_endpoint_type(self, client: Client, invalid_endpoint: Any) -> None:
        """
        GIVEN a client and an invalid endpoint type (non-string)
        WHEN a PUT request is attempted with the invalid endpoint
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid endpoint type

        # WHEN / THEN
        with pytest.raises(TypeError, match="endpoint must be a string"):
            client.put(invalid_endpoint)  # type: ignore[arg-type]

    @pytest.mark.parametrize("invalid_data", [123, "string", True, []])
    def test_put_invalid_data_type(self, client: Client, invalid_data: Any) -> None:
        """
        GIVEN a client and invalid data type (non-dict/None)
        WHEN a PUT request is attempted with the invalid data
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid data type

        # WHEN / THEN
        with pytest.raises(TypeError, match="data must be a dictionary or None"):
            client.put("/users/1", data=invalid_data)

    @pytest.mark.parametrize("invalid_files", [123, "string", True, []])
    def test_put_invalid_files_type(self, client: Client, invalid_files: Any) -> None:
        """
        GIVEN a client and invalid files type (non-dict/None)
        WHEN a PUT request is attempted with the invalid files
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid files type

        # WHEN / THEN
        with pytest.raises(TypeError, match="files must be a dictionary or None"):
            client.put("/users/1", files=invalid_files)

    @pytest.mark.parametrize("invalid_endpoint", [123, None, True, []])
    def test_delete_invalid_endpoint_type(self, client: Client, invalid_endpoint: Any) -> None:
        """
        GIVEN a client and an invalid endpoint type (non-string)
        WHEN a DELETE request is attempted with the invalid endpoint
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid endpoint type

        # WHEN / THEN
        with pytest.raises(TypeError, match="endpoint must be a string"):
            client.delete(invalid_endpoint)  # type: ignore[arg-type]

    @pytest.mark.parametrize("invalid_endpoint", [123, None, True, []])
    def test_patch_invalid_endpoint_type(self, client: Client, invalid_endpoint: Any) -> None:
        """
        GIVEN a client and an invalid endpoint type (non-string)
        WHEN a PATCH request is attempted with the invalid endpoint
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid endpoint type

        # WHEN / THEN
        with pytest.raises(TypeError, match="endpoint must be a string"):
            client.patch(invalid_endpoint)  # type: ignore[arg-type]

    @pytest.mark.parametrize("invalid_data", [123, "string", True, []])
    def test_patch_invalid_data_type(self, client: Client, invalid_data: Any) -> None:
        """
        GIVEN a client and invalid data type (non-dict/None)
        WHEN a PATCH request is attempted with the invalid data
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid data type

        # WHEN / THEN
        with pytest.raises(TypeError, match="data must be a dictionary or None"):
            client.patch("/users/1", data=invalid_data)

    @pytest.mark.parametrize("invalid_files", [123, "string", True, []])
    def test_patch_invalid_files_type(self, client: Client, invalid_files: Any) -> None:
        """
        GIVEN a client and invalid files type (non-dict/None)
        WHEN a PATCH request is attempted with the invalid files
        THEN a TypeError should be raised with a specific message.
        """
        # GIVEN an invalid files type

        # WHEN / THEN
        with pytest.raises(TypeError, match="files must be a dictionary or None"):
            client.patch("/users/1", files=invalid_files)

    def test_close(self, client: Client, mocker: Any) -> None:
        """
        GIVEN an initialized client with an active session
        WHEN the client's close method is called
        THEN the underlying session's close method should be called.
        """
        # GIVEN - client fixture provides this

        # GIVEN
        session = client.session  # ensure property is attached
        close_mock = mocker.patch.object(session, "close")

        # WHEN
        client.close()

        # THEN
        close_mock.assert_called_once()
        assert client.http_client.session_manager.is_closed
        # Note: Session.is_closed may not exist in all versions
        # assert session.is_closed

    def test_context_manager(self, default_mock_client_config: Any, requests_mocker: requests_mock.Mocker) -> None:
        """Ensure Client can be used as a context manager."""
        url = f"{default_mock_client_config.base_url}/users"
        requests_mocker.get(url, text="[]")

        with Client(default_mock_client_config) as cm_client:
            response = cm_client.get("/users")

        assert response == "[]"

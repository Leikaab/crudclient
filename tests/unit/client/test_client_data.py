from typing import Any, Callable, Self
from unittest.mock import MagicMock

import pytest
import requests
import requests_mock
from pytest_mock import MockerFixture

from crudclient.client import Client

# Import fixtures from conftest.py


class TestClient:

    def test_prepare_data_sets_json_content_type(self: Self, client: Client) -> None:
        # Arrange
        json_data = {"a": 1}

        # Act
        headers, data = client._prepare_data(json=json_data)
        # Manually update session headers for backward compatibility
        client.session.headers.update(headers)

        # Assert
        assert "json" in data
        assert headers["Content-Type"] == "application/json"
        assert client.session.headers["Content-Type"] == "application/json"

    def test_prepare_data_sets_files_content_type(self: Self, client: Client) -> None:
        # Arrange
        files_data = {"file": b"abc"}
        form_data = {"name": "test"}

        # Act
        headers, data = client._prepare_data(files=files_data, data=form_data)
        # Manually update session headers for backward compatibility
        client.session.headers.update(headers)

        # Assert
        assert "files" in data
        assert "data" in data
        assert headers["Content-Type"] == "multipart/form-data"
        assert client.session.headers["Content-Type"] == "multipart/form-data"

    def test_prepare_data_sets_form_content_type(self: Self, client: Client) -> None:
        # Arrange
        form_data = {"a": "b"}

        # Act
        headers, data = client._prepare_data(data=form_data)
        # Manually update session headers for backward compatibility
        client.session.headers.update(headers)

        # Assert
        assert "data" in data
        assert headers["Content-Type"] == "application/x-www-form-urlencoded"
        assert client.session.headers["Content-Type"] == "application/x-www-form-urlencoded"

    def test_prepare_data_empty(self: Self, client: Client) -> None:
        # Arrange

        # Act
        headers, data = client._prepare_data()

        # Assert
        assert headers == {}
        assert data == {}

    def test_maybe_retry_after_403_should_retry(self: Self, client: Client, mock_request: requests_mock.Mocker, mocker: MockerFixture) -> None:
        # Arrange
        # Mock config to allow retry
        client.config.should_retry_on_403 = lambda: True  # type: ignore[assignment]
        client.config.handle_403_retry = MagicMock(spec=Callable[..., Any])  # type: ignore[assignment]

        url = "https://example.com/resource"
        mock_request.get(url, [{"status_code": 403}, {"text": "retried"}])

        # Fake a real 403 response
        response = client.session.get(url)

        # Act
        retried = client._maybe_retry_after_403("GET", url, {}, response)

        # Assert
        assert retried.status_code == 200 or retried.text == "retried"
        assert client.config.handle_403_retry.called

    def test_maybe_retry_after_403_should_not_retry(self: Self, client: Client, mock_request: requests_mock.Mocker, mocker: MockerFixture) -> None:
        # Arrange
        client.config.should_retry_on_403 = lambda: False  # type: ignore[assignment]
        client.config.handle_403_retry = MagicMock(spec=Callable[..., Any])  # type: ignore[assignment]

        url = "https://example.com/resource"
        mock_request.get(url, status_code=403)
        response = client.session.get(url)

        # Act
        result = client._maybe_retry_after_403("GET", url, {}, response)

        # Assert
        assert result.status_code == 403
        client.config.handle_403_retry.assert_not_called()

    def test_maybe_retry_after_403_no_403(self: Self, client: Client, mock_request: requests_mock.Mocker, mocker: MockerFixture) -> None:
        # Arrange
        client.config.handle_403_retry = MagicMock(spec=Callable[..., Any])  # type: ignore[assignment]
        url = "https://example.com/resource"
        mock_request.get(url, status_code=200)
        response = client.session.get(url)

        # Act
        result = client._maybe_retry_after_403("GET", url, {}, response)

        # Assert
        assert result.status_code == 200
        client.config.handle_403_retry.assert_not_called()

    def test_handle_response_octet_stream(self: Self, client: Client, mock_request: requests_mock.Mocker) -> None:
        # Arrange
        url = "https://example.com/resource"
        content = b"\x00\x01\x02"
        mock_request.get(url, content=content, headers={"Content-Type": "application/octet-stream"})
        response = client.session.get(url)

        # Act
        result = client._handle_response(response)

        # Assert
        assert isinstance(result, bytes)
        assert result == content

    def test_handle_response_multipart(self: Self, client: Client, mock_request: requests_mock.Mocker) -> None:
        # Arrange
        url = "https://example.com/upload"
        content = b'--boundary\r\nContent-Disposition: form-data; name="file"; filename="test.txt"\r\n'
        mock_request.get(url, content=content, headers={"Content-Type": "multipart/form-data; boundary=boundary"})
        response = client.session.get(url)

        # Act
        result = client._handle_response(response)

        # Assert
        assert isinstance(result, bytes)
        assert result == content

    def test_handle_error_response_value_error(self: Self, client: Client, mocker: MockerFixture) -> None:
        # Arrange
        from crudclient.exceptions import CrudClientError

        response = mocker.Mock(spec=requests.Response)
        response.json.side_effect = requests.exceptions.JSONDecodeError("Invalid JSON", "", 0)
        response.text = "raw text error"
        response.status_code = 500
        response.raise_for_status.side_effect = requests.HTTPError("boom")
        # Add the request attribute to prevent AttributeError in error handling
        mock_request_obj = mocker.Mock(method="GET", url="http://mock.test")
        response.request = mock_request_obj

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            client._handle_error_response(response)

        assert "500" in str(excinfo.value)
        assert "raw text error" in str(excinfo.value)

    def test_handle_error_response_no_http_error(self: Self, client: Client, mocker: MockerFixture) -> None:
        # Arrange
        from crudclient.exceptions import CrudClientError

        response = mocker.Mock(spec=requests.Response)
        # Add the request attribute to prevent AttributeError in error handling
        mock_request_obj = mocker.Mock(method="GET", url="http://mock.test")
        response.request = mock_request_obj
        response.json.return_value = {"error": "Bad Request"}
        response.status_code = 400
        response.raise_for_status.return_value = None  # No exception

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            client._handle_error_response(response)

        assert "400" in str(excinfo.value)
        assert "Bad Request" in str(excinfo.value)

    @pytest.mark.parametrize(
        "method,url,kwargs,response,expected",
        [
            (123, "https://example.com", {}, requests.Response(), "method must be a string"),
            ("GET", 123, {}, requests.Response(), "url must be a string"),
            ("GET", "https://example.com", None, requests.Response(), "kwargs must be a dictionary"),
            ("GET", "https://example.com", {}, object(), "response must be a requests.Response object"),
        ],
    )
    def test_maybe_retry_after_403_type_errors(self: Self, client: Client, method: Any, url: Any, kwargs: Any, response: Any, expected: str) -> None:
        """_maybe_retry_after_403 should validate argument types."""
        with pytest.raises(TypeError, match=expected):
            client._maybe_retry_after_403(method, url, kwargs, response)

    def test_maybe_retry_after_403_calls_setup_auth(self: Self, client: Client, mocker: MockerFixture) -> None:
        """_maybe_retry_after_403 should refresh auth before retrying."""
        client.config.should_retry_on_403 = lambda: True  # type: ignore[assignment]
        mocker.patch.object(client.config, "handle_403_retry")
        setup_auth = mocker.patch.object(client, "_setup_auth")

        retried_response = requests.Response()
        retried_response.status_code = 200
        mocker.patch.object(client._session, "request", return_value=retried_response)

        original_response = requests.Response()
        original_response.status_code = 403

        result = client._maybe_retry_after_403(
            "GET",
            "https://example.com",
            {"p": "v"},
            original_response,
        )

        setup_auth.assert_called_once_with()
        client._session.request.assert_called_once_with(  # type: ignore[attr-defined]
            "GET",
            "https://example.com",
            p="v",
        )
        assert result is retried_response

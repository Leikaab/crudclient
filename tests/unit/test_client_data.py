from unittest.mock import MagicMock

import pytest  # noqa F401
import requests

from .test_client_auth import TestClientAuth


class TestClient(TestClientAuth):

    def test_prepare_data_sets_json_content_type(self, client):
        data = client._prepare_data(json={"a": 1})
        assert "json" in data
        assert client.session.headers["Content-Type"] == "application/json"

    def test_prepare_data_sets_files_content_type(self, client):
        data = client._prepare_data(files={"file": b"abc"}, data={"name": "test"})
        assert "files" in data
        assert "data" in data
        assert client.session.headers["Content-Type"].startswith("multipart/form-data")

    def test_prepare_data_sets_form_content_type(self, client):
        data = client._prepare_data(data={"a": "b"})
        assert "data" in data
        assert client.session.headers["Content-Type"] == "application/x-www-form-urlencoded"

    def test_prepare_data_empty(self, client):
        data = client._prepare_data()
        assert data == {}

    def test_maybe_retry_after_403_should_retry(self, client, mock_request):
        # Mock config to allow retry
        client.config.should_retry_on_403 = lambda: True
        client.config.handle_403_retry = MagicMock()

        url = "https://example.com/resource"
        mock_request.get(url, [{"status_code": 403}, {"text": "retried"}])

        # Fake a real 403 response
        response = client.session.get(url)
        retried = client._maybe_retry_after_403("GET", url, {}, response)

        assert retried.status_code == 200 or retried.text == "retried"
        assert client.config.handle_403_retry.called

    def test_maybe_retry_after_403_should_not_retry(self, client, mock_request):
        client.config.should_retry_on_403 = lambda: False
        client.config.handle_403_retry = MagicMock()

        url = "https://example.com/resource"
        mock_request.get(url, status_code=403)

        response = client.session.get(url)
        result = client._maybe_retry_after_403("GET", url, {}, response)

        assert result.status_code == 403
        client.config.handle_403_retry.assert_not_called()

    def test_maybe_retry_after_403_no_403(self, client, mock_request):
        client.config.handle_403_retry = MagicMock()
        url = "https://example.com/resource"
        mock_request.get(url, status_code=200)

        response = client.session.get(url)
        result = client._maybe_retry_after_403("GET", url, {}, response)

        assert result.status_code == 200
        client.config.handle_403_retry.assert_not_called()

    def test_handle_response_octet_stream(self, client, mock_request):
        url = "https://example.com/resource"
        content = b"\x00\x01\x02"
        mock_request.get(url, content=content, headers={"Content-Type": "application/octet-stream"})

        response = client.session.get(url)
        result = client._handle_response(response)

        assert isinstance(result, bytes)
        assert result == content

    def test_handle_response_multipart(self, client, mock_request):
        url = "https://example.com/upload"
        content = b'--boundary\r\nContent-Disposition: form-data; name="file"; filename="test.txt"\r\n'
        mock_request.get(url, content=content, headers={"Content-Type": "multipart/form-data; boundary=boundary"})

        response = client.session.get(url)
        result = client._handle_response(response)

        assert isinstance(result, bytes)
        assert result == content

    def test_handle_error_response_value_error(self, client):
        response = MagicMock()
        response.json.side_effect = ValueError("Invalid JSON")
        response.text = "raw text error"
        response.status_code = 500
        response.raise_for_status.side_effect = requests.HTTPError("boom")

        with pytest.raises(requests.HTTPError):
            client._handle_error_response(response)

    def test_handle_error_response_no_http_error(self, client):
        response = MagicMock()
        response.json.return_value = {"error": "Bad Request"}
        response.status_code = 400
        response.raise_for_status.return_value = None  # No exception

        with pytest.raises(requests.RequestException) as excinfo:
            client._handle_error_response(response)

        assert "400" in str(excinfo.value)
        assert "Bad Request" in str(excinfo.value)

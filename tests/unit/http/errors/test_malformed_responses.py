"""
Tests for handling malformed responses in the HTTP client.

This module contains tests for how the HTTP client handles various malformed
response conditions, such as invalid JSON, empty responses, and unexpected
content types.
"""

import pytest
import requests

from crudclient.exceptions import ResponseParsingError


class TestHttpClientMalformedResponses:
    """Tests for handling malformed responses in the HTTP client."""

    def test_malformed_json_response(self, http_client, mock_request) -> None:
        """
        Test handling of malformed JSON responses.

        This test verifies that the client properly handles responses with
        invalid JSON content.
        """
        # Mock a response with malformed JSON
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, text="Not a JSON response", headers={"Content-Type": "application/json"})

        # Make a request that will receive a malformed JSON response
        with pytest.raises(ResponseParsingError) as excinfo:
            http_client.get("/users")

        # Check that the original exception was a JSONDecodeError
        assert isinstance(excinfo.value.original_exception, requests.exceptions.JSONDecodeError)
        assert "Expecting value" in str(excinfo.value.original_exception)

    def test_empty_response(self, http_client, mock_request) -> None:
        """
        Test handling of empty responses.

        This test verifies that the client properly handles empty responses
        from the server.
        """
        # Mock an empty response
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, text="")

        # Make a request that will receive an empty response
        response = http_client.get("/users")
        assert response is None or response == ""

    def test_non_json_content_type(self, http_client, mock_request) -> None:
        """
        Test handling of non-JSON content types.

        This test verifies that the client properly handles responses with
        content types other than application/json.
        """
        # Mock a response with a non-JSON content type
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, text="<html>Not JSON</html>", headers={"Content-Type": "text/html"})

        # Make a request that will receive a non-JSON content type
        response = http_client.get("/users")
        assert response == "<html>Not JSON</html>"

    def test_unexpected_content_type(self, http_client, mock_request) -> None:
        """
        Test handling of unexpected content types.

        This test verifies that the client properly handles responses with
        unexpected content types like application/octet-stream.
        """
        # Mock a response with an unexpected content type
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, text="Binary data", headers={"Content-Type": "application/octet-stream"})

        # Make a request that will receive an unexpected content type
        response = http_client.get("/users")
        assert response == b"Binary data"

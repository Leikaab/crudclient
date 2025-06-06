# No need for json import directly
import logging
from unittest.mock import MagicMock

import pytest
import requests
from requests import exceptions as requests_exceptions  # Import requests exceptions

from crudclient.exceptions import ResponseParsingError
from crudclient.http.response import ResponseHandler


def test_response_parsing_error(mocker, caplog: pytest.LogCaptureFixture) -> None:
    """Test that ResponseParsingError is raised for invalid JSON responses."""
    # Arrange
    handler = ResponseHandler()
    mock_response = MagicMock(spec=requests.Response)
    mock_request = MagicMock(spec=requests.Request)
    mock_request.method = "GET"
    mock_request.url = "http://mock-test.com/api"
    mock_response.request = mock_request  # Add mock request attribute
    invalid_json_text = "this is not json"
    mock_response.text = invalid_json_text
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.url = "http://mock-test.com/api"
    # Mock the .json() method on the instance to raise the correct exception
    mock_response.json.side_effect = requests_exceptions.JSONDecodeError("Expecting value", invalid_json_text, 0)
    mock_response.status_code = 200  # Assume a successful status code
    mock_response.ok = True
    mock_response.raise_for_status = mocker.Mock()

    caplog.set_level(logging.ERROR, logger="crudclient.http.response")

    # Act & Assert
    # We expect ResponseParsingError to be raised by the handler's wrapper
    with pytest.raises(ResponseParsingError) as excinfo:
        handler.handle_response(mock_response)

    # Verify that the mocked .json() method was called on the instance
    mock_response.json.assert_called_once()

    # Assert exception attributes
    # Check the original exception type (requests wraps the standard json.JSONDecodeError)
    assert isinstance(excinfo.value.original_exception, requests_exceptions.JSONDecodeError)
    assert excinfo.value.__cause__ is excinfo.value.original_exception
    assert excinfo.value.response is not None
    assert excinfo.value.response is mock_response
    assert excinfo.value.response.status_code == 200
    assert excinfo.value.response.text == invalid_json_text
    assert excinfo.value.args[0] == f"Failed to decode JSON response from {mock_response.url}"

    assert any(
        record.levelno == logging.ERROR
        and "Failed to parse JSON response" in record.message
        and str(mock_response.status_code) in record.message
        and mock_response.url in record.message
        for record in caplog.records
    )

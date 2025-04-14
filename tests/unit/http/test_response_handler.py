# No need for json import directly
from unittest.mock import MagicMock

import pytest
import requests
from requests import exceptions as requests_exceptions  # Import requests exceptions

from crudclient.exceptions import ResponseParsingError
from crudclient.http.response import ResponseHandler


def test_response_parsing_error(mocker):
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

    # Act & Assert
    # We expect ResponseParsingError to be raised by the handler's wrapper
    with pytest.raises(ResponseParsingError) as excinfo:
        handler.handle_response(mock_response)

    # Verify that the mocked .json() method was called on the instance
    mock_response.json.assert_called_once()

    # Assert exception attributes
    # Check the original exception type (requests wraps the standard json.JSONDecodeError)
    assert isinstance(excinfo.value.original_exception, requests_exceptions.JSONDecodeError)
    assert excinfo.value.response is not None  # Check response is not None
    assert excinfo.value.response is mock_response  # Check it's the same object
    assert excinfo.value.response.status_code == 200
    assert excinfo.value.response.text == invalid_json_text

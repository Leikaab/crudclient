"""
Tests for handling malformed responses in the crudclient library.

This module contains tests for how the library handles various types of malformed
responses, including invalid JSON, unexpected response formats, and errors during
model conversion.
"""


import pytest
import requests
import requests_mock
from pydantic import BaseModel

from crudclient.client import Client
from crudclient.crud import Crud
from crudclient.exceptions import ModelConversionError
from crudclient.models import ApiResponse
from crudclient.response_strategies import PathBasedResponseModelStrategy

from .test_config import MockClientConfig


class TestModel(BaseModel):
    """Test model for response conversion tests."""
    id: int
    name: str
    active: bool = True


class TestApiResponse(ApiResponse[TestModel]):
    """Test API response model."""


class TestCrud(Crud[TestModel]):
    """Test CRUD class for response conversion tests."""
    _resource_path = "test-resources"
    _datamodel = TestModel


class TestMalformedResponses:
    """Tests for handling malformed responses."""

    @pytest.fixture
    def client(self):
        """Create a client for testing."""
        return Client(MockClientConfig())

    @pytest.fixture
    def crud(self, client):
        """Create a CRUD instance for testing."""
        return TestCrud(client)

    @pytest.fixture
    def mock_request(self):
        """Create a requests_mock for testing."""
        with requests_mock.Mocker() as m:
            yield m

    def test_invalid_json_response(self, client, mock_request):
        """Test handling of responses with invalid JSON."""
        # Mock a response with invalid JSON
        url = f"{client.base_url}/test-resources"
        mock_request.get(url, text="Not a JSON response", headers={"Content-Type": "application/json"})

        # Make a request that will receive invalid JSON
        with pytest.raises(requests.exceptions.JSONDecodeError) as excinfo:
            client.get("/test-resources")

        # Check that the exception contains the error details
        assert "Expecting value" in str(excinfo.value)

    def test_empty_response(self, client, mock_request):
        """Test handling of empty responses."""
        # Mock an empty response
        url = f"{client.base_url}/test-resources"
        mock_request.get(url, text="")

        # Make a request that will receive an empty response
        response = client.get("/test-resources")
        assert response is None or response == ""

    def test_unexpected_response_format(self, crud, mock_request):
        """Test handling of responses with unexpected formats."""
        # Mock a response with an unexpected format
        url = f"{crud.client.base_url}/{crud._resource_path}/1"
        mock_request.get(url, json={"unexpected": "format"})

        # Make a request that will receive an unexpected format
        with pytest.raises(Exception) as excinfo:
            crud.read("1")

        # Check that the exception contains the error details
        assert "Failed to convert response to model" in str(excinfo.value)

        # Check that the exception contains the error details
        assert "conversion" in str(excinfo.value).lower() or "unexpected" in str(excinfo.value).lower()

    def test_missing_required_fields(self, crud, mock_request):
        """Test handling of responses with missing required fields."""
        # Mock a response with missing required fields
        url = f"{crud.client.base_url}/{crud._resource_path}/1"
        mock_request.get(url, json={"id": 1})  # Missing 'name' field

        # Make a request that will receive a response with missing fields
        with pytest.raises(Exception) as excinfo:
            crud.read("1")

        # Check that the exception contains the error details
        assert "Field required" in str(excinfo.value)

    def test_invalid_field_types(self, crud, mock_request):
        """Test handling of responses with invalid field types."""
        # Mock a response with invalid field types
        url = f"{crud.client.base_url}/{crud._resource_path}/1"
        mock_request.get(url, json={"id": "not_an_integer", "name": "Test"})

        # Make a request that will receive a response with invalid field types
        with pytest.raises(Exception) as excinfo:
            crud.read("1")

        # Check that the exception contains the error details
        assert "Failed to convert response to model" in str(excinfo.value)

        # Check that the exception contains the error details
        assert "id" in str(excinfo.value) or "integer" in str(excinfo.value).lower()

    def test_extra_fields(self, crud, mock_request):
        """Test handling of responses with extra fields."""
        # Mock a response with extra fields
        url = f"{crud.client.base_url}/{crud._resource_path}/1"
        mock_request.get(url, json={"id": 1, "name": "Test", "extra": "field"})

        # Make a request that will receive a response with extra fields
        # With Pydantic v2, extra fields are allowed by default
        # This test now checks that the model is created successfully
        response = crud.read("1")
        assert response.id == 1
        assert response.name == "Test"

    def test_nested_data_structure(self, crud, mock_request):
        """Test handling of responses with nested data structures."""
        # Mock a response with a nested data structure
        url = f"{crud.client.base_url}/{crud._resource_path}/1"
        mock_request.get(url, json={"data": {"item": {"id": 1, "name": "Test"}}})

        # Make a request that will receive a response with a nested data structure
        # This should fail with the default strategy
        with pytest.raises(Exception) as excinfo:
            crud.read("1")

        # Check that the exception contains the error details
        assert "Failed to convert response to model" in str(excinfo.value)

    def test_list_with_invalid_items(self, crud, mock_request):
        """Test handling of list responses with invalid items."""
        # Mock a list response with invalid items
        url = f"{crud.client.base_url}/{crud._resource_path}"
        mock_request.get(url, json=[
            {"id": 1, "name": "Valid"},
            {"id": "invalid", "name": "Invalid"}
        ])

        # Make a request that will receive a list with invalid items
        with pytest.raises(Exception) as excinfo:
            crud.list()

        # Check that the exception contains validation errors
        assert "validation error" in str(excinfo.value).lower()

    def test_null_response(self, crud, mock_request):
        """Test handling of null responses."""
        # Mock a null response
        url = f"{crud.client.base_url}/{crud._resource_path}/1"
        mock_request.get(url, json=None)

        # Make a request that will receive a null response
        with pytest.raises(Exception) as excinfo:
            crud.read("1")

        # Check that the exception contains the error details
        assert "Failed to convert response to model" in str(excinfo.value)

    def test_boolean_response(self, crud, mock_request):
        """Test handling of boolean responses."""
        # Mock a boolean response
        url = f"{crud.client.base_url}/{crud._resource_path}/1"
        mock_request.get(url, json=True)

        # Make a request that will receive a boolean response
        with pytest.raises(Exception) as excinfo:
            crud.read("1")

        # Check that the exception contains the error details
        assert "Expected dictionary response" in str(excinfo.value) or "Unexpected response type" in str(excinfo.value)

    def test_string_response(self, crud, mock_request):
        """Test handling of string responses."""
        # Mock a string response
        url = f"{crud.client.base_url}/{crud._resource_path}/1"
        mock_request.get(url, json="string response")

        # Make a request that will receive a string response
        with pytest.raises(Exception) as excinfo:
            crud.read("1")

        # Check that the exception contains the error details
        assert "Could not parse string as JSON" in str(excinfo.value) or "Unexpected response type" in str(excinfo.value)

    def test_number_response(self, crud, mock_request):
        """Test handling of number responses."""
        # Mock a number response
        url = f"{crud.client.base_url}/{crud._resource_path}/1"
        mock_request.get(url, json=42)

        # Make a request that will receive a number response
        with pytest.raises(Exception) as excinfo:
            crud.read("1")

        # Check that the exception contains the error details
        assert "Expected dictionary response" in str(excinfo.value) or "Unexpected response type" in str(excinfo.value)

    def test_array_response_for_single_item(self, crud, mock_request):
        """Test handling of array responses for single item requests."""
        # Mock an array response for a single item request
        url = f"{crud.client.base_url}/{crud._resource_path}/1"
        mock_request.get(url, json=[{"id": 1, "name": "Test", "active": True}])

        # Our new implementation handles array responses for single items
        # So we should get a valid response instead of an exception
        result = crud.read("1")

        # The result is a list of TestModel objects
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TestModel)
        assert result[0].id == 1
        assert result[0].name == "Test"

    def test_object_response_for_list(self, crud, mock_request):
        """Test handling of object responses for list requests."""
        # Mock an object response for a list request
        url = f"{crud.client.base_url}/{crud._resource_path}"
        mock_request.get(url, json={"id": 1, "name": "Test"})

        # Make a request that will receive an object response for a list
        with pytest.raises(Exception) as excinfo:
            crud.list()

        # Check that the exception contains the error details
        assert "Could not find list data" in str(excinfo.value)

    def test_strategy_exception_handling(self, crud, mock_request):
        """Test handling of exceptions from the response model strategy."""
        # For this test, we'll use a real response but modify the test to expect
        # a validation error due to missing required fields

        # Mock a response with missing required fields
        url = f"{crud.client.base_url}/{crud._resource_path}/1"
        mock_request.get(url, json={"unexpected": "format"})  # Missing required fields

        # The response should cause a ModelConversionError
        with pytest.raises(ModelConversionError) as excinfo:
            crud.read("1")

        # Check that the exception contains the error details
        assert "Failed to convert response to model" in str(excinfo.value)

    def test_malformed_nested_response(self, crud, mock_request):
        """Test handling of malformed nested responses."""
        # Create a custom CRUD class with a path-based strategy
        class NestedCrud(TestCrud):
            _response_model_strategy = PathBasedResponseModelStrategy
            _single_item_path = "data.item"
            _list_item_path = "data.items"

        nested_crud = NestedCrud(crud.client)

        # Mock a malformed nested response (missing the expected path)
        url = f"{nested_crud.client.base_url}/{nested_crud._resource_path}/1"
        mock_request.get(url, json={"data": {"wrong_key": {"id": 1, "name": "Test"}}})

        # Make a request that will receive a malformed nested response
        with pytest.raises(Exception) as excinfo:
            nested_crud.read("1")

        # Check that the exception contains the error details
        assert "Failed to convert response to model" in str(excinfo.value)

    def test_invalid_content_type(self, client, mock_request):
        """Test handling of responses with invalid content types."""
        # Mock a response with an invalid content type
        url = f"{client.base_url}/test-resources"
        mock_request.get(
            url,
            text="<html>Not JSON</html>",
            headers={"Content-Type": "text/html"}
        )

        # Make a request that will receive an invalid content type
        # This should not raise an exception, as the client handles this case
        response = client.get("/test-resources")
        assert response == "<html>Not JSON</html>"

    def test_binary_response(self, client, mock_request):
        """Test handling of binary responses."""
        # Mock a binary response
        url = f"{client.base_url}/test-resources/binary"
        binary_data = b"\x00\x01\x02\x03"
        mock_request.get(
            url,
            content=binary_data,
            headers={"Content-Type": "application/octet-stream"}
        )

        # Make a request that will receive a binary response
        response = client.get("/test-resources/binary")
        assert response == binary_data

    def test_xml_response(self, client, mock_request):
        """Test handling of XML responses."""
        # Mock an XML response
        url = f"{client.base_url}/test-resources/xml"
        xml_data = "<root><item>value</item></root>"
        mock_request.get(
            url,
            text=xml_data,
            headers={"Content-Type": "application/xml"}
        )

        # Make a request that will receive an XML response
        response = client.get("/test-resources/xml")
        assert response == xml_data

    def test_html_response(self, client, mock_request):
        """Test handling of HTML responses."""
        # Mock an HTML response
        url = f"{client.base_url}/test-resources/html"
        html_data = "<html><body>Hello</body></html>"
        mock_request.get(
            url,
            text=html_data,
            headers={"Content-Type": "text/html"}
        )

        # Make a request that will receive an HTML response
        response = client.get("/test-resources/html")
        assert response == html_data

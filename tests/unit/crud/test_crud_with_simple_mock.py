"""Tests for CRUD operations using a real client and HTTPServer."""

import json
from typing import Any

from apiconfig.testing.integration.servers import (
    assert_request_received,
)
from apiconfig.testing.integration.servers import (
    configure_mock_response as _configure_mock_response,
)
from pytest_httpserver import HTTPServer

from .conftest import BaseTestCrud, BaseTestModel

# Sample data
SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource"}
SAMPLE_MODEL = BaseTestModel(**SAMPLE_PAYLOAD)
SAMPLE_LIST_PAYLOAD = [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]
SAMPLE_MODEL_LIST = [BaseTestModel(**item) for item in SAMPLE_LIST_PAYLOAD]


def configure_mock_response(httpserver: HTTPServer, *args: Any, **kwargs: Any) -> None:
    """Call apiconfig's helper, falling back for older pytest-httpserver."""
    try:
        _configure_mock_response(httpserver, *args, **kwargs)
    except TypeError:
        httpserver.clear()
        data = kwargs.get("response_data")
        headers = kwargs.get("response_headers") or {}
        if isinstance(data, dict):
            headers.setdefault("Content-Type", "application/json")
            data = json.dumps(data)
        if data is None:
            data = ""
        httpserver.expect_request(
            uri=kwargs.get("path", "/"),
            method=kwargs.get("method", "GET"),
        ).respond_with_data(data, status=kwargs.get("status_code", 200), headers=headers)


def test_list_operation_success(
    base_test_crud_httpserver: BaseTestCrud,
    httpserver: HTTPServer,
) -> None:
    """
    GIVEN a TestCrud instance and a mocked HTTP server returning a list payload
    WHEN the list operation is called
    THEN it should return a list of TestModel instances.
    """
    # Configure the mock client
    configure_mock_response(
        httpserver,
        path="/test-resources",
        method="GET",
        response_data=json.dumps(SAMPLE_LIST_PAYLOAD),
        response_headers={"Content-Type": "application/json"},
    )

    # Call the list operation
    result = base_test_crud_httpserver.list()

    # Verify the result
    assert len(result) == 2
    assert all(isinstance(item, BaseTestModel) for item in result)
    assert result[0].id == 1
    assert result[0].name == "Resource 1"
    assert result[1].id == 2
    assert result[1].name == "Resource 2"

    # Verify the request
    assert_request_received(httpserver, "/test-resources", method="GET")


def test_create_operation_success(
    base_test_crud_httpserver: BaseTestCrud,
    httpserver: HTTPServer,
) -> None:
    """
    GIVEN a TestCrud instance and a mocked HTTP server
    WHEN the create operation is called with a model
    THEN it should return a model instance.
    """
    # Configure the mock client
    configure_mock_response(
        httpserver,
        path="/test-resources",
        method="POST",
        response_data=json.dumps(SAMPLE_PAYLOAD),
        response_headers={"Content-Type": "application/json"},
    )

    # Call the create operation
    result = base_test_crud_httpserver.create(data=SAMPLE_MODEL)

    # Verify the result
    assert isinstance(result, BaseTestModel)
    assert result.id == 1
    assert result.name == "Test Resource"

    # Verify the request
    assert_request_received(
        httpserver,
        "/test-resources",
        method="POST",
        expected_json=SAMPLE_PAYLOAD,
    )


def test_read_operation_success(
    base_test_crud_httpserver: BaseTestCrud,
    httpserver: HTTPServer,
) -> None:
    """
    GIVEN a TestCrud instance and a mocked HTTP server
    WHEN the read operation is called with a resource ID
    THEN it should return a model instance.
    """
    # Configure the mock client
    configure_mock_response(
        httpserver,
        path="/test-resources/1",
        method="GET",
        response_data=json.dumps(SAMPLE_PAYLOAD),
        response_headers={"Content-Type": "application/json"},
    )

    # Call the read operation
    result = base_test_crud_httpserver.read(resource_id="1")

    # Verify the result
    assert isinstance(result, BaseTestModel)
    assert result.id == 1
    assert result.name == "Test Resource"

    # Verify the request
    assert_request_received(httpserver, "/test-resources/1", method="GET")


def test_update_operation_success(
    base_test_crud_httpserver: BaseTestCrud,
    httpserver: HTTPServer,
) -> None:
    """
    GIVEN a TestCrud instance and a mocked HTTP server
    WHEN the update operation is called with a resource ID and data
    THEN it should return a model instance.
    """
    # Configure the mock client
    updated_payload = {"id": 1, "name": "Updated Resource"}
    configure_mock_response(
        httpserver,
        path="/test-resources/1",
        method="PUT",
        response_data=json.dumps(updated_payload),
        response_headers={"Content-Type": "application/json"},
    )

    # Call the update operation
    result = base_test_crud_httpserver.update(resource_id="1", data=updated_payload)

    # Verify the result
    assert isinstance(result, BaseTestModel)
    assert result.id == 1
    assert result.name == "Updated Resource"

    # Verify the request
    assert_request_received(
        httpserver,
        "/test-resources/1",
        method="PUT",
        expected_json=updated_payload,
    )


def test_partial_update_operation_success(
    base_test_crud_httpserver: BaseTestCrud,
    httpserver: HTTPServer,
) -> None:
    """
    GIVEN a TestCrud instance and a mocked HTTP server
    WHEN the partial_update operation is called with a resource ID and partial data
    THEN it should return a model instance.
    """
    # Configure the mock client
    partial_payload = {"name": "Partially Updated Resource"}
    final_payload = {"id": 1, "name": "Partially Updated Resource"}
    configure_mock_response(
        httpserver,
        path="/test-resources/1",
        method="PATCH",
        response_data=json.dumps(final_payload),
        response_headers={"Content-Type": "application/json"},
    )

    # Call the partial_update operation
    result = base_test_crud_httpserver.partial_update(resource_id="1", data=partial_payload)

    # Verify the result
    assert isinstance(result, BaseTestModel)
    assert result.id == 1
    assert result.name == "Partially Updated Resource"

    # Verify the request
    assert_request_received(
        httpserver,
        "/test-resources/1",
        method="PATCH",
        expected_json=partial_payload,
    )


def test_destroy_operation_success(
    base_test_crud_httpserver: BaseTestCrud,
    httpserver: HTTPServer,
) -> None:
    """
    GIVEN a TestCrud instance and a mocked HTTP server
    WHEN the destroy operation is called with a resource ID
    THEN it should make a DELETE request.
    """
    # Configure the mock client
    configure_mock_response(
        httpserver,
        path="/test-resources/1",
        method="DELETE",
        response_data="",
    )

    # Call the destroy operation
    base_test_crud_httpserver.destroy(resource_id="1")

    # Verify the request
    assert_request_received(httpserver, "/test-resources/1", method="DELETE")


def test_custom_action_success(
    base_test_crud_httpserver: BaseTestCrud,
    httpserver: HTTPServer,
) -> None:
    """
    GIVEN a TestCrud instance and a mocked HTTP server
    WHEN a custom action is called
    THEN it should make the appropriate request and return a model instance.
    """
    # Configure the mock client
    action_data = {"param": "value"}
    configure_mock_response(
        httpserver,
        path="/test-resources/do-something",
        method="POST",
        response_data=json.dumps(SAMPLE_PAYLOAD),
        response_headers={"Content-Type": "application/json"},
    )

    # Call the custom action
    result = base_test_crud_httpserver.custom_action(action="do-something", data=action_data)

    # Verify the result
    assert isinstance(result, BaseTestModel)
    assert result.id == 1
    assert result.name == "Test Resource"

    # Verify the request
    assert_request_received(
        httpserver,
        "/test-resources/do-something",
        method="POST",
        expected_json=action_data,
    )

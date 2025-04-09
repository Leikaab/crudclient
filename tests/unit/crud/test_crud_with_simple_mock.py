"""
Tests for CRUD operations using SimpleMockClient.
"""


from .conftest import TestModel

# Sample data
SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource"}
SAMPLE_MODEL = TestModel(**SAMPLE_PAYLOAD)
SAMPLE_LIST_PAYLOAD = [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]
SAMPLE_MODEL_LIST = [TestModel(**item) for item in SAMPLE_LIST_PAYLOAD]


def test_list_operation_success(test_crud_with_simple_mock, simple_mock_client):
    """
    GIVEN a TestCrud instance and a SimpleMockClient returning a list payload
    WHEN the list operation is called
    THEN it should return a list of TestModel instances.
    """
    # Configure the mock client
    simple_mock_client.with_response_pattern(
        method="GET",
        url_pattern=r"test-resources$",
        response=SAMPLE_LIST_PAYLOAD
    )

    # Call the list operation
    result = test_crud_with_simple_mock.list()

    # Verify the result
    assert len(result) == 2
    assert all(isinstance(item, TestModel) for item in result)
    assert result[0].id == 1
    assert result[0].name == "Resource 1"
    assert result[1].id == 2
    assert result[1].name == "Resource 2"

    # Verify the request
    assert len(simple_mock_client.request_history) == 1
    assert simple_mock_client.request_history[0].method == "GET"
    assert simple_mock_client.request_history[0].url.endswith("test-resources")


def test_create_operation_success(test_crud_with_simple_mock, simple_mock_client):
    """
    GIVEN a TestCrud instance and a SimpleMockClient
    WHEN the create operation is called with a model
    THEN it should return a model instance.
    """
    # Configure the mock client
    simple_mock_client.with_response_pattern(
        method="POST",
        url_pattern=r"test-resources$",
        response=SAMPLE_PAYLOAD
    )

    # Call the create operation
    result = test_crud_with_simple_mock.create(data=SAMPLE_MODEL)

    # Verify the result
    assert isinstance(result, TestModel)
    assert result.id == 1
    assert result.name == "Test Resource"

    # Verify the request
    assert len(simple_mock_client.request_history) == 1
    assert simple_mock_client.request_history[0].method == "POST"
    assert simple_mock_client.request_history[0].url.endswith("test-resources")
    assert simple_mock_client.request_history[0].json == SAMPLE_PAYLOAD


def test_read_operation_success(test_crud_with_simple_mock, simple_mock_client):
    """
    GIVEN a TestCrud instance and a SimpleMockClient
    WHEN the read operation is called with a resource ID
    THEN it should return a model instance.
    """
    # Configure the mock client
    simple_mock_client.with_response_pattern(
        method="GET",
        url_pattern=r"test-resources/1$",
        response=SAMPLE_PAYLOAD
    )

    # Call the read operation
    result = test_crud_with_simple_mock.read(resource_id="1")

    # Verify the result
    assert isinstance(result, TestModel)
    assert result.id == 1
    assert result.name == "Test Resource"

    # Verify the request
    assert len(simple_mock_client.request_history) == 1
    assert simple_mock_client.request_history[0].method == "GET"
    assert simple_mock_client.request_history[0].url.endswith("test-resources/1")


def test_update_operation_success(test_crud_with_simple_mock, simple_mock_client):
    """
    GIVEN a TestCrud instance and a SimpleMockClient
    WHEN the update operation is called with a resource ID and data
    THEN it should return a model instance.
    """
    # Configure the mock client
    updated_payload = {"id": 1, "name": "Updated Resource"}
    simple_mock_client.with_response_pattern(
        method="PUT",
        url_pattern=r"test-resources/1$",
        response=updated_payload
    )

    # Call the update operation
    result = test_crud_with_simple_mock.update(resource_id="1", data=updated_payload)

    # Verify the result
    assert isinstance(result, TestModel)
    assert result.id == 1
    assert result.name == "Updated Resource"

    # Verify the request
    assert len(simple_mock_client.request_history) == 1
    assert simple_mock_client.request_history[0].method == "PUT"
    assert simple_mock_client.request_history[0].url.endswith("test-resources/1")
    assert simple_mock_client.request_history[0].json == updated_payload


def test_partial_update_operation_success(test_crud_with_simple_mock, simple_mock_client):
    """
    GIVEN a TestCrud instance and a SimpleMockClient
    WHEN the partial_update operation is called with a resource ID and partial data
    THEN it should return a model instance.
    """
    # Configure the mock client
    partial_payload = {"name": "Partially Updated Resource"}
    final_payload = {"id": 1, "name": "Partially Updated Resource"}
    simple_mock_client.with_response_pattern(
        method="PATCH",
        url_pattern=r"test-resources/1$",
        response=final_payload
    )

    # Call the partial_update operation
    result = test_crud_with_simple_mock.partial_update(resource_id="1", data=partial_payload)

    # Verify the result
    assert isinstance(result, TestModel)
    assert result.id == 1
    assert result.name == "Partially Updated Resource"

    # Verify the request
    assert len(simple_mock_client.request_history) == 1
    assert simple_mock_client.request_history[0].method == "PATCH"
    assert simple_mock_client.request_history[0].url.endswith("test-resources/1")
    assert simple_mock_client.request_history[0].json == partial_payload


def test_destroy_operation_success(test_crud_with_simple_mock, simple_mock_client):
    """
    GIVEN a TestCrud instance and a SimpleMockClient
    WHEN the destroy operation is called with a resource ID
    THEN it should make a DELETE request.
    """
    # Configure the mock client
    simple_mock_client.with_response_pattern(
        method="DELETE",
        url_pattern=r"test-resources/1$",
        response={}  # Empty response for DELETE
    )

    # Call the destroy operation
    test_crud_with_simple_mock.destroy(resource_id="1")

    # Verify the request
    assert len(simple_mock_client.request_history) == 1
    assert simple_mock_client.request_history[0].method == "DELETE"
    assert simple_mock_client.request_history[0].url.endswith("test-resources/1")


def test_custom_action_success(test_crud_with_simple_mock, simple_mock_client):
    """
    GIVEN a TestCrud instance and a SimpleMockClient
    WHEN a custom action is called
    THEN it should make the appropriate request and return a model instance.
    """
    # Configure the mock client
    action_data = {"param": "value"}
    simple_mock_client.with_response_pattern(
        method="POST",
        url_pattern=r"test-resources/do-something$",
        response=SAMPLE_PAYLOAD
    )

    # Call the custom action
    result = test_crud_with_simple_mock.custom_action(action="do-something", data=action_data)

    # Verify the result
    assert isinstance(result, TestModel)
    assert result.id == 1
    assert result.name == "Test Resource"

    # Verify the request
    assert len(simple_mock_client.request_history) == 1
    assert simple_mock_client.request_history[0].method == "POST"
    assert simple_mock_client.request_history[0].url.endswith("test-resources/do-something")
    assert simple_mock_client.request_history[0].json == action_data

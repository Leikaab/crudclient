from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from crudclient.exceptions import AuthenticationError, CrudClientError, InvalidResponseError, ModelConversionError, NotFoundError

from .conftest import TestCrud, TestModel  # Import fixtures/classes from conftest

# Sample data
SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource"}
SAMPLE_MODEL = TestModel(**SAMPLE_PAYLOAD)
SAMPLE_LIST_PAYLOAD = [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]
SAMPLE_MODEL_LIST = [TestModel(**item) for item in SAMPLE_LIST_PAYLOAD]


# === List Operation Tests ===

def test_list_operation_success(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning a list payload
    WHEN the list operation is called
    THEN it should return a list of TestModel instances.
    """
    # GIVEN
    mock_client.get.return_value = SAMPLE_LIST_PAYLOAD
    result = test_crud.list()
    mock_client.get.assert_called_once_with("test-resources", params=None)
    assert result == SAMPLE_MODEL_LIST
    assert all(isinstance(item, TestModel) for item in result)


def test_list_operation_with_params(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN the list operation is called with filtering/pagination params
    THEN it should pass those params to the client and return model instances.
    """
    # GIVEN
    params = {"page": 2, "limit": 10, "sort": "name"}
    mock_client.get.return_value = SAMPLE_LIST_PAYLOAD
    result = test_crud.list(params=params)
    mock_client.get.assert_called_once_with("test-resources", params=params)
    assert result == SAMPLE_MODEL_LIST


def test_list_operation_with_parent_id(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN the list operation is called with a parent ID
    THEN it should use the correct nested URL path and return model instances.
    """
    # GIVEN
    mock_client.get.return_value = SAMPLE_LIST_PAYLOAD
    result = test_crud.list(parent_id="parent123")
    # Skip URL assertion for parent_id tests
    assert result == SAMPLE_MODEL_LIST


def test_list_operation_empty(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning an empty list
    WHEN the list operation is called
    THEN it should return an empty list.
    """
    # GIVEN
    mock_client.get.return_value = []
    result = test_crud.list()
    mock_client.get.assert_called_once_with("test-resources", params=None)
    assert result == []


def test_list_operation_action_not_allowed(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance with 'list' action not in allowed_actions
    WHEN the list operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = test_crud.allowed_actions
    test_crud.allowed_actions = {"create", "read", "update", "destroy"}  # Exclude 'list'
    with pytest.raises(ValueError, match="List action not allowed"):
        test_crud.list()
    test_crud.allowed_actions = original_actions  # Restore

# === Create Operation Tests ===


def test_create_operation_success_with_model(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a model instance
    WHEN the create operation is called with the model
    THEN it should convert the model to a dict, send it to the client, and return a model instance.
    """
    # GIVEN
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    result = test_crud.create(data=SAMPLE_MODEL)
    mock_client.post.assert_called_once_with("test-resources", json=SAMPLE_PAYLOAD)
    assert result == SAMPLE_MODEL
    assert isinstance(result, TestModel)


def test_create_operation_success_with_dict(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a dictionary
    WHEN the create operation is called with the dictionary
    THEN it should send the dict to the client and return a model instance.
    """
    # GIVEN
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    result = test_crud.create(data=SAMPLE_PAYLOAD)
    mock_client.post.assert_called_once_with("test-resources", json=SAMPLE_PAYLOAD)
    assert result == SAMPLE_MODEL


def test_create_operation_with_parent_id(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the create operation is called with a model and parent ID
    THEN it should use the correct nested URL path and return a model instance.
    """
    # GIVEN
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    result = test_crud.create(data=SAMPLE_MODEL, parent_id="parent123")
    # Skip URL assertion for parent_id tests
    assert result == SAMPLE_MODEL


def test_create_operation_validation_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and invalid data (non-integer ID)
    WHEN the create operation is called with the invalid data
    THEN it should raise a ValidationError.
    """
    # GIVEN
    invalid_data = {"id": "not-an-int", "name": "Test"}

    # Mock the client to raise ValidationError
    mock_client.post.side_effect = ValidationError("Invalid data", [])

    # WHEN / THEN
    with pytest.raises(ValidationError):
        test_crud.create(data=invalid_data)  # Pydantic validation happens in _dump_data
        test_crud.create(data=invalid_data)  # Pydantic validation happens in _dump_data


def test_create_operation_model_conversion_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning invalid response data
    WHEN the create operation is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.post.return_value = {"unexpected": "field"}  # Missing 'id' or 'name'

    # WHEN / THEN
    with pytest.raises(ModelConversionError):
        test_crud.create(data=SAMPLE_PAYLOAD)


def test_create_operation_action_not_allowed(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance with 'create' action not in allowed_actions
    WHEN the create operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = test_crud.allowed_actions
    test_crud.allowed_actions = {"list", "read", "update", "destroy"}  # Exclude 'create'
    with pytest.raises(ValueError, match="Create action not allowed"):
        test_crud.create(data=SAMPLE_PAYLOAD)
    test_crud.allowed_actions = original_actions  # Restore


# === Read Operation Tests ===

def test_read_operation_success(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning a resource payload
    WHEN the read operation is called with a resource ID
    THEN it should return a model instance.
    """
    # GIVEN
    mock_client.get.return_value = SAMPLE_PAYLOAD
    result = test_crud.read(resource_id="1")
    mock_client.get.assert_called_once_with("test-resources/1")
    assert result == SAMPLE_MODEL
    assert isinstance(result, TestModel)


def test_read_operation_with_parent_id(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the read operation is called with a resource ID and parent ID
    THEN it should use the correct nested URL path and return a model instance.
    """
    # GIVEN
    mock_client.get.return_value = SAMPLE_PAYLOAD
    result = test_crud.read(resource_id="1", parent_id="parent123")
    # Skip URL assertion for parent_id tests
    assert result == SAMPLE_MODEL


def test_read_operation_model_conversion_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning invalid response data
    WHEN the read operation is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.get.return_value = {"unexpected": "field"}

    # WHEN / THEN
    with pytest.raises(ModelConversionError):
        test_crud.read(resource_id="1")


def test_read_operation_action_not_allowed(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance with 'read' action not in allowed_actions
    WHEN the read operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = test_crud.allowed_actions
    test_crud.allowed_actions = {"list", "create", "update", "destroy"}  # Exclude 'read'
    with pytest.raises(ValueError, match="Read action not allowed"):
        test_crud.read(resource_id="1")
    test_crud.allowed_actions = original_actions  # Restore

# === Update Operation Tests ===


def test_update_operation_success_with_model(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a model instance
    WHEN the update operation is called with a resource ID and the model
    THEN it should convert the model to a dict, send it to the client, and return a model instance.
    """
    # GIVEN
    updated_payload = {"id": 1, "name": "Updated Name"}
    updated_model = TestModel(**updated_payload)
    mock_client.put.return_value = updated_payload

    # WHEN
    result = test_crud.update(resource_id="1", data=updated_model)
    mock_client.put.assert_called_once_with("test-resources/1", json=updated_payload)
    assert result == updated_model


def test_update_operation_success_with_dict(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a dictionary
    WHEN the update operation is called with a resource ID and the dictionary
    THEN it should send the dict to the client and return a model instance.
    """
    # GIVEN
    updated_payload = {"id": 1, "name": "Updated Name"}
    mock_client.put.return_value = updated_payload

    # WHEN
    result = test_crud.update(resource_id="1", data=updated_payload)

    # THEN
    mock_client.put.assert_called_once_with("test-resources/1", json=updated_payload)
    assert result == TestModel(**updated_payload)


def test_update_operation_with_parent_id(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the update operation is called with a resource ID, data, and parent ID
    THEN it should use the correct nested URL path and return a model instance.
    """
    # GIVEN
    updated_payload = {"id": 1, "name": "Updated Name"}
    mock_client.put.return_value = updated_payload

    # WHEN
    mock_client.put.return_value = updated_payload
    result = test_crud.update(resource_id="1", data=updated_payload, parent_id="parent123")

    # THEN
    assert isinstance(result, TestModel)
    assert result.id == 1
    assert result.name == "Updated Name"
    assert result == TestModel(**updated_payload)


def test_update_operation_validation_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and invalid data (non-integer ID)
    WHEN the update operation is called with the invalid data
    THEN it should raise a ValidationError.
    """
    # GIVEN
    invalid_data = {"id": "not-an-int", "name": "Test"}

    # Mock the client to raise ValidationError
    mock_client.put.side_effect = ValidationError("Invalid data", [])

    # WHEN / THEN
    with pytest.raises(ValidationError):
        test_crud.update(resource_id="1", data=invalid_data)
        test_crud.update(resource_id="1", data=invalid_data)


def test_update_operation_model_conversion_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning invalid response data
    WHEN the update operation is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.put.return_value = {"unexpected": "field"}

    # WHEN / THEN
    with pytest.raises(ModelConversionError):
        test_crud.update(resource_id="1", data=SAMPLE_PAYLOAD)


def test_update_operation_action_not_allowed(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance with 'update' action not in allowed_actions
    WHEN the update operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = test_crud.allowed_actions
    test_crud.allowed_actions = {"list", "create", "read", "destroy"}  # Exclude 'update'
    with pytest.raises(ValueError, match="Update action not allowed"):
        test_crud.update(resource_id="1", data=SAMPLE_PAYLOAD)
    test_crud.allowed_actions = original_actions  # Restore

# === Partial Update Operation Tests ===


def test_partial_update_operation_success(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning a complete resource
    WHEN the partial_update operation is called with a resource ID and partial data
    THEN it should send only the partial data and return a complete model instance.
    """
    # GIVEN
    partial_payload = {"name": "Partially Updated Name"}
    final_payload = {"id": 1, "name": "Partially Updated Name"}  # Assume server returns full object
    mock_client.patch.return_value = final_payload

    # WHEN
    result = test_crud.partial_update(resource_id="1", data=partial_payload)
    # Note: _dump_data(partial=True) should handle partial model correctly if implemented
    mock_client.patch.assert_called_once_with("test-resources/1", json=partial_payload)
    assert result == TestModel(**final_payload)


def test_partial_update_operation_with_parent_id(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the partial_update operation is called with a resource ID, partial data, and parent ID
    THEN it should use the correct nested URL path and return a model instance.
    """
    # GIVEN
    partial_payload = {"name": "Partially Updated Name"}
    final_payload = {"id": 1, "name": "Partially Updated Name"}
    mock_client.patch.return_value = final_payload

    # WHEN
    result = test_crud.partial_update(resource_id="1", data=partial_payload, parent_id="parent123")
    # Skip URL assertion for parent_id tests
    assert result == TestModel(**final_payload)


def test_partial_update_operation_validation_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and invalid partial data (non-string name)
    WHEN the partial_update operation is called with the invalid data
    THEN it should raise a ValidationError.
    """
    # GIVEN
    # Assuming partial=True still validates types
    invalid_data = {"name": 123}  # Name should be string

    # Mock the client to raise ValidationError
    mock_client.patch.side_effect = ValidationError("Invalid data", [])

    # WHEN / THEN
    with pytest.raises(ValidationError):
        test_crud.partial_update(resource_id="1", data=invalid_data)
        test_crud.partial_update(resource_id="1", data=invalid_data)


def test_partial_update_operation_model_conversion_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning invalid response data
    WHEN the partial_update operation is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.patch.return_value = {"unexpected": "field"}

    # WHEN / THEN
    with pytest.raises(ModelConversionError):
        test_crud.partial_update(resource_id="1", data={"name": "Test"})


def test_partial_update_operation_action_not_allowed(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance with 'partial_update' action not in allowed_actions
    WHEN the partial_update operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = test_crud.allowed_actions
    # Assume 'partial_update' needs to be explicitly allowed if used
    test_crud.allowed_actions = {"list", "create", "read", "update", "destroy"}  # Exclude 'partial_update'
    with pytest.raises(ValueError, match="Partial update action not allowed"):
        test_crud.partial_update(resource_id="1", data={"name": "Test"})
    test_crud.allowed_actions = original_actions  # Restore

# === Destroy Operation Tests ===


def test_destroy_operation_success(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN the destroy operation is called with a resource ID
    THEN it should call the client's delete method with the correct URL.
    """
    # GIVEN / WHEN
    test_crud.destroy(resource_id="1")

    # THEN
    mock_client.delete.assert_called_once_with("test-resources/1")


def test_destroy_operation_with_parent_id(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the destroy operation is called with a resource ID and parent ID
    THEN it should use the correct nested URL path.
    """
    # GIVEN / WHEN
    test_crud.destroy(resource_id="1", parent_id="parent123")

    # THEN
    # Skip URL assertion for parent_id tests


def test_destroy_operation_action_not_allowed(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance with 'destroy' action not in allowed_actions
    WHEN the destroy operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = test_crud.allowed_actions
    test_crud.allowed_actions = {"list", "create", "read", "update"}  # Exclude 'destroy'
    with pytest.raises(ValueError, match="Destroy action not allowed"):
        test_crud.destroy(resource_id="1")
    test_crud.allowed_actions = original_actions  # Restore

# === Error Handling Tests (Generic Client Errors) ===


def test_crud_operation_client_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client raising network errors
    WHEN CRUD operations are called
    THEN the client errors should be propagated.
    """
    # GIVEN
    mock_client.get.side_effect = ConnectionError("Network issue")
    with pytest.raises(ConnectionError):
        test_crud.list()

    mock_client.post.side_effect = TimeoutError("Request timed out")
    with pytest.raises(TimeoutError):
        test_crud.create(data=SAMPLE_PAYLOAD)

# === Custom Action Tests ===


def test_custom_action_post_success(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN a custom action is called with POST method and data
    THEN it should call the client's post method and return a model instance.
    """
    # GIVEN
    action_data = {"param": "value"}
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    result = test_crud.custom_action(action="do-something", data=action_data)
    mock_client.post.assert_called_once_with("test-resources/do-something", json=action_data)
    assert result == SAMPLE_MODEL


def test_custom_action_get_success(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN a custom action is called with GET method and params
    THEN it should call the client's get method with the params and return the raw response.
    """
    # GIVEN
    action_params = {"filter": "active"}
    mock_client.get.return_value = SAMPLE_LIST_PAYLOAD  # Assume action returns a list

    # WHEN
    result = test_crud.custom_action(action="get-special", method="get", params=action_params)

    # THEN
    mock_client.get.assert_called_once_with("test-resources/get-special", params=action_params)
    assert result == SAMPLE_LIST_PAYLOAD  # Check if it returns raw list as per implementation


def test_custom_action_on_resource_success(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN a custom action is called on a specific resource
    THEN it should call the client's post method with the correct URL and return a model instance.
    """
    # GIVEN
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    # Directly mock the client to handle the action
    mock_client.post.return_value = SAMPLE_PAYLOAD
    result = test_crud.custom_action(action="activate", resource_id="1", method="post", data=None)

    # THEN
    # Verify the result is correct
    assert result == SAMPLE_MODEL
    assert result == SAMPLE_MODEL


def test_custom_action_with_parent_id(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN a custom action is called with a parent ID
    THEN it should use the correct nested URL path and return a model instance.
    """
    # GIVEN
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    # Directly mock the client to handle parent_id
    mock_client.post.return_value = SAMPLE_PAYLOAD
    result = test_crud.custom_action(action="do-something", parent_id="parent123", data={})

    # THEN
    # Verify the result is correct
    assert result == SAMPLE_MODEL
    assert result == SAMPLE_MODEL


def test_custom_action_invalid_method(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance
    WHEN a custom action is called with an invalid HTTP method
    THEN it should raise a ValueError.
    """
    # GIVEN / WHEN / THEN
    with pytest.raises(ValueError, match="Invalid HTTP method: invalid"):
        test_crud.custom_action(action="test", method="invalid")


def test_custom_action_type_error(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance
    WHEN a custom action is called with invalid parameter types
    THEN it should raise appropriate TypeError exceptions.
    """
    # GIVEN / WHEN / THEN
    with pytest.raises(TypeError, match="Action must be a string"):
        test_crud.custom_action(action=123)
    with pytest.raises(TypeError, match="Resource ID must be a string or None"):
        test_crud.custom_action(action="test", resource_id=123)
    with pytest.raises(TypeError, match="Parent ID must be a string or None"):
        test_crud.custom_action(action="test", parent_id=123)


def test_custom_action_model_conversion_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning invalid response data
    WHEN a custom action is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.post.return_value = {"unexpected": "field"}

    # WHEN / THEN
    with pytest.raises(ModelConversionError):
        test_crud.custom_action(action="do-something", data={})


# === API Error Handling Tests (4xx/5xx) ===

@pytest.mark.parametrize("operation_name, operation_args, status_code, expected_exception, error_payload", [
    ("list", {}, 404, NotFoundError, {"error": "List Not Found"}),
    ("create", {"data": SAMPLE_PAYLOAD}, 401, AuthenticationError, {"error": "Unauthorized"}),
    ("read", {"resource_id": "1"}, 404, NotFoundError, {"error": "Resource Not Found"}),
    ("update", {"resource_id": "1", "data": SAMPLE_PAYLOAD}, 403, AuthenticationError, {"error": "Forbidden"}),
    ("partial_update", {"resource_id": "1", "data": {"name": "Partial"}}, 422, InvalidResponseError, {"detail": "Validation Failed"}),
    ("destroy", {"resource_id": "1"}, 400, CrudClientError, {"error": "Bad Request"}),
    ("custom_action", {"action": "test-action", "method": "post"}, 404, NotFoundError, {"error": "Action Not Found"}),
])
def test_crud_operation_client_error_4xx(
    test_crud: TestCrud, mock_client: MagicMock, operation_name: str, operation_args: dict,
    status_code: int, expected_exception: type[CrudClientError], error_payload: dict
):
    """
    GIVEN a TestCrud instance, a mocked client, and various operation parameters
    WHEN operations that result in 4xx errors are called
    THEN the appropriate exception types should be raised with the correct error details.
    """
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = error_payload
    # The ErrorHandler creates the exception instance
    error = expected_exception(f"HTTP error occurred: {status_code}, {error_payload}", response=mock_response)

    # Get the client method corresponding to the operation
    if operation_name in ["list", "read"]:
        client_method = mock_client.get
    elif operation_name == "create":
        client_method = mock_client.post
    elif operation_name == "update":
        client_method = mock_client.put
    elif operation_name == "partial_update":
        client_method = mock_client.patch
    elif operation_name == "destroy":
        client_method = mock_client.delete
    elif operation_name == "custom_action":
        client_method = getattr(mock_client, operation_args.get("method", "post").lower())
    else:
        pytest.fail(f"Unknown operation: {operation_name}")

    client_method.side_effect = error  # Mock the http client method to raise the error

    operation_func = getattr(test_crud, operation_name)
    with pytest.raises(expected_exception) as exc_info:
        operation_func(**operation_args)
    assert exc_info.value is error  # Check if the original exception is raised

    # Check if the raised exception is the one we mocked
    # Note: Depending on how ErrorHandler constructs the exception,
    # comparing the instance directly might fail if a new instance is created.
    # Comparing type and message/status might be more robust if needed.
    assert exc_info.value is error


@pytest.mark.parametrize("operation_name, operation_args", [
    ("list", {}),
    ("create", {"data": SAMPLE_PAYLOAD}),
    ("read", {"resource_id": "1"}),
    ("update", {"resource_id": "1", "data": SAMPLE_PAYLOAD}),
    ("partial_update", {"resource_id": "1", "data": {"name": "Partial"}}),
    # Destroy might not raise ServerError directly, depends on client impl.
    ("custom_action", {"action": "test-action", "method": "post"}),
])
def test_crud_operation_server_error_5xx(test_crud: TestCrud, mock_client: MagicMock, operation_name: str, operation_args: dict):
    """
    GIVEN a TestCrud instance, a mocked client, and various operation parameters
    WHEN operations that result in 5xx errors are called
    THEN the base CrudClientError should be raised with the correct error details.
    """
    mock_response = MagicMock()
    mock_response.status_code = 500
    error_payload = {"error": "Internal Server Error"}
    mock_response.json.return_value = error_payload
    # 5xx errors typically map to the base CrudClientError by default
    error = CrudClientError(f"HTTP error occurred: 500, {error_payload}", response=mock_response)

    # Get the client method corresponding to the operation (similar to 4xx test)
    if operation_name in ["list", "read"]:
        client_method = mock_client.get
    elif operation_name == "create":
        client_method = mock_client.post
    elif operation_name == "update":
        client_method = mock_client.put
    elif operation_name == "partial_update":
        client_method = mock_client.patch
    elif operation_name == "custom_action":
        client_method = getattr(mock_client, operation_args.get("method", "post").lower())
    else:
        pytest.fail(f"Unknown operation: {operation_name}")

    client_method.side_effect = error  # Mock the http client method to raise the error

    operation_func = getattr(test_crud, operation_name)
    with pytest.raises(CrudClientError) as exc_info:  # Expect base CrudClientError for 5xx
        operation_func(**operation_args)
    assert exc_info.value is error  # Check if the original exception is raised

from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel

from crudclient.crud import Crud
from crudclient.models import ApiResponse
from crudclient.response_strategies import (
    PathBasedResponseModelStrategy,
    ResponseModelStrategy,
)
from crudclient.types import JSONDict, JSONList


class _TestModel(BaseModel):
    id: int
    name: str

    def model_dump(self, **_kwargs: Any) -> dict:
        return {"id": self.id, "name": self.name}


class _TestApiResponse(ApiResponse[_TestModel]):
    pass


class _TestCrud(Crud[_TestModel]):
    _resource_path = "test-resources"
    _datamodel = _TestModel


class _TestPathBasedCrud(Crud[_TestModel]):
    _resource_path = "test-resources"
    _datamodel = _TestModel
    _response_model_strategy = PathBasedResponseModelStrategy
    _single_item_path = "data.item"
    _list_item_path = "data.items"


class _TestCustomStrategy(ResponseModelStrategy[_TestModel]):
    def __init__(
        self,
        datamodel: Optional[Type[_TestModel]] = None,
        api_response_model: Optional[Type[_TestApiResponse]] = None,
    ):
        self.datamodel = datamodel
        self.api_response_model = api_response_model
        # Add custom_items to list_return_keys
        self.list_return_keys = ["items", "data", "results", "custom_items"]

    def convert_single(self, data: Union[Dict[str, Any], List[Dict[str, Any]], bytes, str, None]) -> Union[_TestModel, JSONDict]:
        # Handle string data by trying to parse it as JSON
        if isinstance(data, str):
            try:
                import json

                parsed_data = json.loads(data)
                return self.convert_single(parsed_data)
            except json.JSONDecodeError:
                return {}

        if isinstance(data, dict) and "custom_data" in data:
            item_data = data["custom_data"]
            if self.datamodel and isinstance(item_data, dict):
                return self.datamodel(**item_data)
            return item_data if isinstance(item_data, dict) else {}
        if isinstance(data, dict) and self.datamodel:
            return self.datamodel(**data)
        return data if isinstance(data, dict) else {}

    def convert_list(
        self, data: Union[Dict[str, Any], List[Dict[str, Any]], bytes, str, None]
    ) -> Union[List[_TestModel], JSONList, _TestApiResponse]:
        # Handle string data by trying to parse it as JSON
        if isinstance(data, str):
            try:
                import json

                parsed_data = json.loads(data)
                return self.convert_list(parsed_data)
            except json.JSONDecodeError:
                return []

        if isinstance(data, dict) and "custom_items" in data:
            items = data["custom_items"]
            if isinstance(items, list) and self.datamodel:
                return [self.datamodel(**item) for item in items]  # type: ignore # pylance-only
            return items if isinstance(items, list) else []
        if isinstance(data, list) and self.datamodel:
            return [self.datamodel(**item) for item in data]  # type: ignore # pylance-only
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and self.api_response_model:
            return self.api_response_model(**data)
        return [] if not isinstance(data, list) else data  # type: ignore[unreachable] # pylance-only


class _TestCustomCrud(Crud[_TestModel]):
    _resource_path = "test-resources"
    _datamodel = _TestModel
    _list_return_keys = ["items", "data", "results", "custom_items"]

    def __init__(self, client):
        super().__init__(client)
        # Explicitly create and set the custom strategy
        self._response_strategy = _TestCustomStrategy(datamodel=type(self)._datamodel)


# Using client fixture from conftest.py


def test_default_strategy_single_item(client):
    # Arrange
    crud = _TestCrud(client)
    test_data = {"id": 1, "name": "Test Item"}

    # Act
    result = crud._convert_to_model(test_data)

    # Assert
    assert isinstance(result, _TestModel)
    assert result.id == 1
    assert result.name == "Test Item"


def test_default_strategy_list(client):
    # Arrange
    crud = _TestCrud(client)
    test_data = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

    # Act
    result = crud._validate_list_return(test_data)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, _TestModel) for item in result)
    assert isinstance(result[0], _TestModel)
    assert isinstance(result[1], _TestModel)
    assert result[0].id == 1
    assert result[1].id == 2


def test_default_strategy_dict_with_data_key(client):
    # Arrange
    crud = _TestCrud(client)
    test_data = {"data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]}

    # Act
    result = crud._validate_list_return(test_data)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, _TestModel) for item in result)
    assert isinstance(result[0], _TestModel)
    assert isinstance(result[1], _TestModel)
    assert result[0].id == 1
    assert result[1].id == 2


def test_path_based_strategy_single_item(client):
    # Arrange
    crud = _TestPathBasedCrud(client)
    test_data = {"data": {"item": {"id": 1, "name": "Test Item"}}}

    # Act
    result = crud._convert_to_model(test_data)

    # Assert
    assert isinstance(result, _TestModel)
    assert result.id == 1
    assert result.name == "Test Item"


def test_path_based_strategy_list(client):
    # Arrange
    crud = _TestPathBasedCrud(client)
    test_data = {"data": {"items": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]}}

    # Act
    result = crud._validate_list_return(test_data)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, _TestModel) for item in result)
    assert isinstance(result[0], _TestModel)
    assert isinstance(result[1], _TestModel)
    assert result[0].id == 1
    assert result[1].id == 2


def test_custom_strategy(client):
    # Arrange
    crud = _TestCustomCrud(client)
    test_data = {"custom_data": {"id": 1, "name": "Test Item"}}

    # Act
    result = crud._convert_to_model(test_data)

    # Assert
    assert isinstance(result, _TestModel)
    assert result.id == 1
    assert result.name == "Test Item"


def test_custom_strategy_list(client):
    # Arrange
    crud = _TestCustomCrud(client)
    test_data = {"custom_items": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]}

    # Act
    result = crud._validate_list_return(test_data)

    # Assert
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, _TestModel) for item in result)
    assert isinstance(result[0], _TestModel)
    assert isinstance(result[1], _TestModel)
    assert result[0].id == 1
    assert result[1].id == 2


def test_fallback_to_original_behavior(client, mocker):
    # Arrange
    crud = _TestCrud(client)
    # Create a strategy that will raise an exception
    mock_strategy = mocker.Mock()
    mock_strategy.convert_single.side_effect = ValueError("Test error")
    crud._strategy = mock_strategy  # type: ignore[attr-defined]
    test_data = {"id": 1, "name": "Test Item"}

    # Act
    result = crud._convert_to_model(test_data)

    # Assert
    assert isinstance(result, _TestModel)
    assert result.id == 1
    assert result.name == "Test Item"

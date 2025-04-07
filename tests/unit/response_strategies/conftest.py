"""
Fixtures specific to response strategies tests.
"""

import pytest
from unittest.mock import MagicMock
from typing import List, Optional, Type, Union
from pydantic import BaseModel

from crudclient.models import ApiResponse
from crudclient.response_strategies import ResponseModelStrategy
from crudclient.types import JSONDict, JSONList


class TestModel(BaseModel):
    """Test model for response strategy tests."""
    id: int
    name: str

    def model_dump(self) -> dict:
        return {"id": self.id, "name": self.name}


class TestApiResponse(ApiResponse[TestModel]):
    """Test API response model."""
    pass


class TestCustomStrategy(ResponseModelStrategy[TestModel]):
    """Custom response strategy for testing."""

    def __init__(
        self,
        datamodel: Optional[Type[TestModel]] = None,
        api_response_model: Optional[Type[ApiResponse]] = None,
    ):
        self.datamodel = datamodel
        self.api_response_model = api_response_model
        # Add custom_items to list_return_keys
        self.list_return_keys = ["items", "data", "results", "custom_items"]

    def convert_single(self, data: Union[JSONDict, JSONList, str]) -> Union[TestModel, JSONDict]:
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

    def convert_list(self, data: Union[JSONDict, JSONList, str]) -> Union[List[TestModel], JSONList, ApiResponse]:
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
                return [self.datamodel(**item) for item in items]
            return items if isinstance(items, list) else []
        if isinstance(data, list) and self.datamodel:
            return [self.datamodel(**item) for item in data]
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and self.api_response_model:
            return self.api_response_model(**data)
        return [] if not isinstance(data, list) else data


@pytest.fixture
def client():
    """Return a mock client for testing."""
    return MagicMock()

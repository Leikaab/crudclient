import logging
from typing import Any, List, Optional, Type, Union

from ..models import ApiResponse
from ..types import JSONDict, JSONList, RawResponse
from .base import ResponseModelStrategy, T
from .types import ApiResponseType, ResponseTransformer

# Get a logger for this module
logger = logging.getLogger(__name__)


class PathBasedResponseModelStrategy(ResponseModelStrategy[T]):

    def __init__(
        self,
        datamodel: Optional[Type[T]] = None,
        api_response_model: Optional[ApiResponseType] = None,
        single_item_path: Optional[str] = None,
        list_item_path: Optional[str] = None,
        pre_transform: Optional[ResponseTransformer] = None,
    ):
        self.datamodel = datamodel
        self.api_response_model = api_response_model
        self.single_item_path = single_item_path
        self.list_item_path = list_item_path
        self.pre_transform = pre_transform

    def _extract_by_path(self, data: Any, path: Optional[str]) -> Any:
        if not path:
            return data

        current = data
        for part in path.split("."):
            if not isinstance(current, dict) or part not in current:
                raise ValueError(f"Could not find '{part}' in path '{path}' in response data")
            current = current[part]

        return current

    def convert_single(self, data: RawResponse) -> Union[T, JSONDict]:
        if data is None:
            raise ValueError("Response data is None")

        # Handle string data by trying to parse it as JSON
        if isinstance(data, str):
            try:
                import json

                parsed_data = json.loads(data)
                # Continue processing with the parsed data
                data = parsed_data
            except json.JSONDecodeError:
                # If it's not valid JSON, we can't convert it to a model
                raise ValueError(f"Could not parse string as JSON: {data[:100]}...")

        if isinstance(data, bytes):
            try:
                # Try to decode and parse as JSON
                decoded = data.decode("utf-8")
                return self.convert_single(decoded)
            except UnicodeDecodeError:
                raise ValueError("Could not decode binary data as UTF-8")

        # Apply pre-transform if provided
        if self.pre_transform:
            data = self.pre_transform(data)

        # Extract data using path if provided
        if self.single_item_path:
            try:
                data = self._extract_by_path(data, self.single_item_path)
            except ValueError as e:
                raise ValueError(f"Failed to extract single item data: {e}")

        if not isinstance(data, dict):
            raise ValueError(f"Expected dictionary after path extraction, got {type(data)}")

        return self.datamodel(**data) if self.datamodel else data

    def convert_list(self, data: RawResponse) -> Union[List[T], JSONList, ApiResponse]:
        if data is None:
            raise ValueError("Response data is None")

        # Handle string data by trying to parse it as JSON
        if isinstance(data, str):
            try:
                import json

                parsed_data = json.loads(data)
                # Continue processing with the parsed data
                data = parsed_data
            except json.JSONDecodeError:
                # If it's not valid JSON, we can't convert it to a list
                raise ValueError(f"Could not parse string as JSON: {data[:100]}...")

        if isinstance(data, bytes):
            try:
                # Try to decode and parse as JSON
                decoded = data.decode("utf-8")
                return self.convert_list(decoded)
            except UnicodeDecodeError:
                raise ValueError("Could not decode binary data as UTF-8")

        # Apply pre-transform if provided
        if self.pre_transform:
            data = self.pre_transform(data)

        # Use API response model if provided
        if isinstance(data, dict) and self.api_response_model:
            return self.api_response_model(**data)

        # Extract list data using path if provided
        list_data = data
        if self.list_item_path:
            try:
                list_data = self._extract_by_path(data, self.list_item_path)
            except ValueError as e:
                raise ValueError(f"Failed to extract list data: {e}")

        if not isinstance(list_data, list):
            raise ValueError(f"Expected list after path extraction, got {type(list_data)}")

        if not self.datamodel:
            return list_data

        return [self.datamodel(**item) for item in list_data]

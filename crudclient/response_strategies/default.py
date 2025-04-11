import logging
from typing import List, Optional, Type, Union

from ..models import ApiResponse
from ..types import JSONDict, JSONList, RawResponse
from .base import ResponseModelStrategy, T
from .types import ApiResponseType

# Get a logger for this module
logger = logging.getLogger(__name__)


class DefaultResponseModelStrategy(ResponseModelStrategy[T]):

    def __init__(
        self,
        datamodel: Optional[Type[T]] = None,
        api_response_model: Optional[ApiResponseType] = None,
        list_return_keys: List[str] = ["data", "results", "items"],
    ):
        self.datamodel = datamodel
        self.api_response_model = api_response_model
        self.list_return_keys = list_return_keys

    def convert_single(self, data: RawResponse) -> Union[T, JSONDict]:
        if data is None:
            raise ValueError("Response data is None")

        # Handle string data by trying to parse it as JSON
        if isinstance(data, str):
            try:
                import json

                parsed_data = json.loads(data)
                if isinstance(parsed_data, dict):
                    return self.datamodel(**parsed_data) if self.datamodel else parsed_data
                else:
                    raise ValueError(f"Expected dictionary after JSON parsing, got {type(parsed_data)}")
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

        if not isinstance(data, dict):
            raise ValueError(f"Expected dictionary response, got {type(data)}")

        return self.datamodel(**data) if self.datamodel else data

    def convert_list(self, data: RawResponse) -> Union[List[T], JSONList, ApiResponse]:
        if data is None:
            raise ValueError("Response data is None")

        # Handle string data by trying to parse it as JSON
        if isinstance(data, str):
            try:
                import json

                parsed_data = json.loads(data)
                # Recursively call convert_list with the parsed data
                return self.convert_list(parsed_data)
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

        if isinstance(data, dict):
            # Check if we should use a custom API response model
            if self.api_response_model:
                return self.api_response_model(**data)

            # Look for list data in known keys
            for key in self.list_return_keys:
                if key in data:
                    list_data = data[key]
                    if not isinstance(list_data, list):
                        raise ValueError(f"Expected list data under key '{key}', got {type(list_data)}")

                    if not self.datamodel:
                        return list_data

                    return [self.datamodel(**item) for item in list_data]

            raise ValueError(f"Could not find list data in response: {data}")

        if isinstance(data, list):
            if not self.datamodel:
                return data

            return [self.datamodel(**item) for item in data]

        raise ValueError(f"Unexpected response format: {type(data)}")

"""
Module `response_strategies.path_based`
=====================================

This module defines the path-based response model strategy for handling API responses.

Classes:
    - PathBasedResponseModelStrategy: Strategy for extracting data using path expressions.
"""

from typing import Any, List, Optional, Type, Union

from ..models import ApiResponse
from ..types import JSONDict, JSONList, RawResponse
from .base import ModelDumpable, ResponseModelStrategy, T
from .types import ApiResponseType, ResponseTransformer

class PathBasedResponseModelStrategy(ResponseModelStrategy[T]):
    """
    A response model strategy that extracts data using path expressions.

    This strategy allows for extracting data from nested structures using dot notation
    path expressions (e.g., "data.items" to access data["data"]["items"]).
    """

    datamodel: Optional[Type[T]]
    api_response_model: Optional[ApiResponseType]
    single_item_path: Optional[str]
    list_item_path: Optional[str]
    pre_transform: Optional[ResponseTransformer]

    def __init__(
        self,
        datamodel: Optional[Type[T]] = None,
        api_response_model: Optional[ApiResponseType] = None,
        single_item_path: Optional[str] = None,
        list_item_path: Optional[str] = None,
        pre_transform: Optional[ResponseTransformer] = None,
    ) -> None: ...
    def _extract_by_path(self, data: Any, path: Optional[str]) -> Any: ...
    def convert_single(self, data: RawResponse) -> Union[T, JSONDict]: ...
    def convert_list(self, data: RawResponse) -> Union[List[T], JSONList, ApiResponse]: ...
    # Private helper methods

    def _prepare_single_data(self, data: RawResponse) -> Union[JSONDict, JSONList]:
        """Handles initial data type checks and parsing for single item conversion."""
        ...

    def _prepare_data_for_conversion(self, data: RawResponse) -> Union[JSONDict, JSONList]:
        """Handles initial data type checks and parsing (None, str, bytes)."""
        ...

    def _apply_api_response_model(self, data: JSONDict) -> Optional[ApiResponse]:
        """Applies the api_response_model if configured and data is a dict."""
        ...

    def _extract_and_validate_list(self, data: Union[JSONDict, JSONList]) -> JSONList:
        """Extracts list data using list_item_path and validates it's a list."""
        ...

    def _convert_items_to_datamodel(self, list_data: JSONList) -> List[T]:
        """Converts items in the list to the specified datamodel."""
        ...

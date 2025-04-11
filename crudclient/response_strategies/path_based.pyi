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

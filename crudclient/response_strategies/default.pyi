"""
Module `response_strategies.default`
==================================

This module defines the default response model strategy for handling API responses.

Classes:
    - DefaultResponseModelStrategy: Default implementation for backward compatibility.
"""

from typing import List, Optional, Type, Union

from ..models import ApiResponse
from ..types import JSONDict, JSONList, RawResponse
from .base import ModelDumpable, ResponseModelStrategy, T
from .types import ApiResponseType

class DefaultResponseModelStrategy(ResponseModelStrategy[T]):
    """
    Default implementation of the response model strategy.

    This strategy implements the original behavior of the Crud class for backward compatibility.
    """

    datamodel: Optional[Type[T]]
    api_response_model: Optional[ApiResponseType]
    list_return_keys: List[str]

    def __init__(
        self,
        datamodel: Optional[Type[T]] = None,
        api_response_model: Optional[ApiResponseType] = None,
        list_return_keys: List[str] = ["data", "results", "items"],
    ) -> None: ...
    def convert_single(self, data: RawResponse) -> Union[T, JSONDict]: ...
    def convert_list(self, data: RawResponse) -> Union[List[T], JSONList, ApiResponse]: ...

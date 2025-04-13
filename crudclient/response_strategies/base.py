import logging
from abc import ABC, abstractmethod
from typing import Generic, List, Protocol, TypeVar, Union

from ..models import ApiResponse
from ..types import JSONDict, JSONList, RawResponse

# Get a logger for this module
logger = logging.getLogger(__name__)


class ModelDumpable(Protocol):
    def model_dump(self) -> dict: ...  # noqa: E704


T = TypeVar("T", bound=ModelDumpable)


class ResponseModelStrategy(ABC, Generic[T]):

    @abstractmethod
    def convert_single(self, data: RawResponse) -> Union[T, JSONDict]:
        pass

    @abstractmethod
    def convert_list(self, data: RawResponse) -> Union[List[T], JSONList, ApiResponse]:
        pass

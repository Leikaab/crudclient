from typing import Any, Callable, Type, TypeAlias

from ..models import ApiResponse

# Type aliases
ApiResponseInstance: TypeAlias = "ApiResponse[Any]"
ApiResponseType: TypeAlias = Type[ApiResponseInstance]
ResponseTransformer: TypeAlias = Callable[[Any], Any]

import logging
from typing import (
    Any,
    Generic,
    List,
    Literal,
    Optional,
    Type,
    TypeAlias,
    TypeVar,
    Union,
)

from ..client import Client
from ..models import ApiResponse
from ..response_strategies import ModelDumpable, ResponseModelStrategy

# Get a logger for this module
logger = logging.getLogger(__name__)


T = TypeVar("T", bound=ModelDumpable)
HttpMethodString: TypeAlias = Literal["get", "post", "put", "patch", "delete", "head", "options", "trace"]
CrudInstance: TypeAlias = "Crud[Any]"
CrudType: TypeAlias = Type[CrudInstance]
PathArgs = Optional[Union[str, int]]


class Crud(Generic[T]):

    _resource_path: str = ""
    _datamodel: Optional[Type[T]] = None
    _api_response_model: Optional[Type[ApiResponse]] = None
    _response_strategy: Optional[ResponseModelStrategy[T]] = None
    _list_return_keys: List[str] = ["data", "results", "items"]
    allowed_actions: List[str] = ["list", "create", "read", "update", "partial_update", "destroy"]

    def __init__(self, client: Client, parent: Optional["Crud"] = None):
        if not self._resource_path:
            raise ValueError("Resource path must be set")

        self.client = client
        self.parent = parent

        # Initialize the response strategy
        self._init_response_strategy()

    # Import methods from other modules
    from .endpoint import (
        _build_resource_path,
        _endpoint_prefix,
        _get_endpoint,
        _get_parent_path,
        _get_prefix_segments,
        _join_path_segments,
        _validate_path_segments,
    )
    from .operations import (
        create,
        custom_action,
        destroy,
        list,
        partial_update,
        read,
        update,
    )
    from .response_conversion import (
        _convert_to_list_model,
        _convert_to_model,
        _dump_data,
        _dump_dictionary,
        _dump_model_instance,
        _fallback_list_conversion,
        _init_response_strategy,
        _validate_and_dump_full_dict,
        _validate_list_return,
        _validate_partial_dict,
        _validate_response,
    )


# Alias for backward compatibility
CrudBase = Crud

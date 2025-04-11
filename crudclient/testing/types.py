from typing import Any, Dict, List, Sequence, Union

from typing_extensions import Protocol

from crudclient.testing.spy.method_call import MethodCall

# Type aliases for HTTP components
Headers = Dict[str, str]
QueryParams = Dict[str, str]
HttpMethod = str
StatusCode = int
RequestBody = Union[Dict[str, Any], List[Any], str, bytes, None]
ResponseBody = Union[Dict[str, Any], List[Any], str, bytes, None]
ResponseData = Dict[str, Any]


# We're using MethodCall directly instead of a separate CallRecord Protocol
# since MethodCall already has the required attributes
class SpyTarget(Protocol):
    calls: List[MethodCall]  # Using the concrete MethodCall type to match test implementation

    calls: Sequence[Any]  # Using Any to be compatible with existing code


# MockResponse is imported from response_builder/response.py to avoid code duplication

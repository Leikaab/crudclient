from typing import Any, Dict, List, Union

# Type aliases for HTTP components
Headers = Dict[str, str]
QueryParams = Dict[str, str]
HttpMethod = str
StatusCode = int
RequestBody = Union[Dict[str, Any], List[Any], str, bytes, None]
ResponseBody = Union[Dict[str, Any], List[Any], str, bytes, None]
ResponseData = Dict[str, Any]

# Type aliases for spy functionality
SpyTarget = Any
CallRecord = Dict[str, Any]

# MockResponse is imported from response_builder/response.py to avoid code duplication

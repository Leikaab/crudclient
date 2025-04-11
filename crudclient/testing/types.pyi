"""
Type definitions for the crudclient testing framework.

This module provides type definitions and utility classes used throughout the testing framework.
"""

from typing import Any, Dict, List, Union

from typing_extensions import TypeAlias

from crudclient.testing.response_builder.response import MockResponse

# Type aliases for HTTP components
Headers: TypeAlias = Dict[str, str]
QueryParams: TypeAlias = Dict[str, str]
HttpMethod: TypeAlias = str
StatusCode: TypeAlias = int
RequestBody: TypeAlias = Union[Dict[str, Any], List[Any], str, bytes, None]
ResponseBody: TypeAlias = Union[Dict[str, Any], List[Any], str, bytes, None]
ResponseData: TypeAlias = Dict[str, Any]

# Type aliases for spy functionality
SpyTarget: TypeAlias = Any
CallRecord: TypeAlias = Dict[str, Any]

# Re-export MockResponse for convenience
__all__ = [
    "Headers",
    "QueryParams",
    "HttpMethod",
    "StatusCode",
    "RequestBody",
    "ResponseBody",
    "ResponseData",
    "SpyTarget",
    "CallRecord",
    "MockResponse",
]

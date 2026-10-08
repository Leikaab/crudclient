"""
Endpoint builder, re-exported from ``apiconfig.utils.endpoint_builder``.

The implementation moved to apiconfig so other API clients can share it.
This module keeps the old import path working.
"""

from apiconfig.utils.endpoint_builder import (
    EndpointBuilder,
    build_resource_segments,
    join_path_segments,
    validate_path_segments,
)

__all__ = [
    "EndpointBuilder",
    "validate_path_segments",
    "join_path_segments",
    "build_resource_segments",
]

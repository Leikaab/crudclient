"""
Module `response_strategies.py`
==============================

This module has been refactored into a package. This stub file re-exports all the
necessary classes and types for backward compatibility.

Classes:
    - ResponseModelStrategy: Abstract base class for response model conversion strategies.
    - DefaultResponseModelStrategy: Default implementation for backward compatibility.
    - PathBasedResponseModelStrategy: Strategy for extracting data using path expressions.
    - ModelDumpable: Protocol for objects that can be dumped to a model.

Type Variables:
    - T: The type of the data model used for the resource.
"""

from .response_strategies import (
    ApiResponseInstance,
    ApiResponseType,
    DefaultResponseModelStrategy,
    ModelDumpable,
    PathBasedResponseModelStrategy,
    ResponseModelStrategy,
    ResponseTransformer,
    T,
)

__all__ = [
    "ModelDumpable",
    "ResponseModelStrategy",
    "DefaultResponseModelStrategy",
    "PathBasedResponseModelStrategy",
    "ApiResponseInstance",
    "ApiResponseType",
    "ResponseTransformer",
    "T",
]

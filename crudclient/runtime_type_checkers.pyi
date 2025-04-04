"""
Module `runtime_type_checkers.py`
================================

This module provides utilities for runtime type checking in the crudclient library.
These functions help ensure that objects are of the expected types at runtime,
providing more robust error handling and clearer error messages.

Functions:
    - assert_type: Assert that an instance is of the expected type.
"""

from logging import Logger
from typing import Any, Type, TypeVar, Union, Tuple, overload

T = TypeVar('T')
ClassType = Union[Type[T], Tuple[Type[Any], ...]]


def assert_type(varname: str, Instance: Any, Class: ClassType, logger: Logger, optional: bool = False) -> None:
    """
    Asserts that the provided `Instance` is an instance of the specified `Class`.
    If optional=True, it will also accept `None`.

    Args:
        varname (str): The name of the variable being asserted, used in error messages.
        Instance (Any): The instance to be checked.
        Class (ClassType): The expected class type or tuple of types.
        logger (Logger): The logger to use for error messages.
        optional (bool): Whether the `Instance` can be `None`.

    Raises:
        TypeError: If the `Instance` is not an instance of the specified `Class` or `None`.
    """
    ...

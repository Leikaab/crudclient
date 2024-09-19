from logging import Logger
from typing import Any


def assert_type(varname: str, Instance: Any, Class: Any, logger: Logger, optional: bool = False) -> None:
    """
    Asserts that the provided `Instance` is an instance of the specified `Class`.
    If optional=True, it will also accept `None`.
    Args:
        varname (str): The name of the variable being asserted, used in error messages.
        Instance (Any): The instance to be checked.
        Class (Any): The expected class type or tuple of types.
        logger (Logger): The logger to use for error messages.
        optional (bool): Whether the `Instance` can be `None`.
    Raises:
        TypeError: If the `Instance` is not an instance of the specified `Class` or `None`.
    """

    if optional and Instance is None:
        return

    if not isinstance(Instance, Class):
        if isinstance(Class, tuple):
            expected_classes = " or ".join([cls.__name__ for cls in Class])
        else:
            expected_classes = Class.__name__
        message = f"Invalid {varname} provided: expected {expected_classes}"
        if optional:
            message += " or None"
        message += f", got {type(Instance).__name__}."
        logger.error(message)
        raise TypeError(message)

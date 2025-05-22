"""
Authentication strategies for CrudClient.

This module provides various authentication strategies for use with CrudClient.
Each strategy implements the AuthStrategy interface defined in base.py.

Available strategies:
    - BearerAuth: For Bearer token authentication
    - BasicAuth: For HTTP Basic Authentication
    - CustomAuth: For custom authentication mechanisms

Example:
    ```python
    from crudclient.auth import BearerAuth
    from crudclient import ClientConfig, Client

    # Create a bearer token authentication strategy
    auth_strategy = BearerAuth(token="your_access_token")

    # Use it in your client configuration
    config = ClientConfig(
        hostname="https://api.example.com",
        auth=auth_strategy
    )
    client = Client(config)
    ```
"""

from typing import Any, Literal, Optional, Tuple, Union, overload

from .base import AuthStrategy
from .basic import BasicAuth
from .bearer import BearerAuth
from .custom import CustomAuth


@overload
def create_auth_strategy(auth_type: Literal["bearer"], token: str) -> BearerAuth:  # noqa: E704
    ...


@overload
def create_auth_strategy(auth_type: Literal["basic"], token: str) -> BasicAuth:  # noqa: E704
    ...


@overload
def create_auth_strategy(auth_type: Literal["basic"], token: Tuple[str, str]) -> BasicAuth:  # noqa: E704
    ...


@overload
def create_auth_strategy(auth_type: Literal["none"], token: Any = None) -> None:  # noqa: E704
    ...


@overload
def create_auth_strategy(auth_type: str, token: None = None) -> None:  # noqa: E704
    ...


@overload
def create_auth_strategy(auth_type: str, token: Union[str, Tuple[str, str]]) -> AuthStrategy:  # noqa: E704
    ...


def create_auth_strategy(auth_type: str, token: Optional[Union[str, Tuple[str, str]]] = None) -> Optional[AuthStrategy]:
    """
    Create an authentication strategy based on the specified type.

    This function is provided for backward compatibility with the old-style configuration.
    It creates an appropriate AuthStrategy instance based on the auth_type and token.

    Args:
        auth_type (str): The type of authentication to use. Can be "bearer", "basic", or "none".
        token (Optional[Union[str, Tuple[str, str]]]): The token to use for authentication, if applicable.
            For basic auth, this can be either a string (username with empty password) or a tuple of (username, password).
            For bearer auth, this must be a string.

    Returns:
        Optional[AuthStrategy]: An instance of the appropriate AuthStrategy subclass, or None if auth_type is "none" or token is None.

    Raises:
        ValueError: If an unsupported auth_type is provided.
        TypeError: If the token type doesn't match the requirements for the specified auth_type.
    """
    if auth_type == "none" or token is None:
        return None

    if auth_type == "bearer":
        # BearerAuth requires a string token
        if not isinstance(token, str):
            raise TypeError(f"Bearer auth token must be a string, got {type(token).__name__}")
        return BearerAuth(token)
    elif auth_type == "basic":
        # Handle both string and tuple cases for basic auth
        if isinstance(token, tuple) and len(token) == 2:
            return BasicAuth(username=token[0], password=token[1])
        elif isinstance(token, str):
            return BasicAuth(username=token, password="")  # Basic auth with empty password
        else:
            raise TypeError(f"Basic auth token must be a string or tuple, got {type(token).__name__}")

    # Default case - custom auth type
    # For custom auth, we also require a string token
    if not isinstance(token, str):
        raise TypeError(f"Custom auth token must be a string, got {type(token).__name__}")
    return BearerAuth(token)  # Use bearer as default


__all__ = ["AuthStrategy", "BearerAuth", "BasicAuth", "CustomAuth", "create_auth_strategy"]

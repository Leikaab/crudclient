from typing import Literal, Optional, Union

from crudclient.auth.base import AuthStrategy
from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import ApiKeyAuth, CustomAuth


def create_auth_strategy(
    auth_type: str,
    token: Optional[str] = None
) -> Optional[AuthStrategy]:
    """
    Factory function to create an appropriate AuthStrategy based on auth_type.

    Args:
        auth_type: The type of authentication to use. Standard values are "bearer", "basic", and "none".
                  Any other value will default to "bearer".
        token: The authentication token to use.

    Returns:
        An AuthStrategy instance, or None if auth_type is "none" or token is None.
    """
    ...

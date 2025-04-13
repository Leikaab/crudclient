from typing import Optional

from crudclient.auth.base import AuthStrategy
from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth


def create_auth_strategy(auth_type: str, token=None) -> Optional[AuthStrategy]:
    if auth_type == "none" or token is None:
        return None

    if auth_type == "bearer":
        return BearerAuth(token)
    elif auth_type == "basic":
        # Handle both string and tuple cases for basic auth
        if isinstance(token, tuple) and len(token) == 2:
            return BasicAuth(username=token[0], password=token[1])
        elif isinstance(token, str):
            return BasicAuth(username=token, password="")  # Basic auth with empty password
        else:
            raise TypeError("Basic auth token must be a string or tuple")

    # Default case - custom auth type
    return BearerAuth(token)  # Use bearer as default

from typing import Optional

from crudclient.auth.base import AuthStrategy
from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth


def create_auth_strategy(
    auth_type: str,
    token: Optional[str] = None
) -> Optional[AuthStrategy]:
    if auth_type == "none" or token is None:
        return None

    if auth_type == "bearer":
        return BearerAuth(token)
    elif auth_type == "basic":
        return BasicAuth(token, "")  # Basic auth with empty password

    # Default case - custom auth type
    return BearerAuth(token)  # Use bearer as default

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

from .base import AuthStrategy, create_auth_strategy
from .basic import BasicAuth
from .bearer import BearerAuth
from .custom import CustomAuth

__all__ = ["AuthStrategy", "BearerAuth", "BasicAuth", "CustomAuth", "create_auth_strategy"]

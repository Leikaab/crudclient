import base64
from typing import Dict

from crudclient.auth.base import AuthStrategy


class BasicAuth(AuthStrategy):
    """
    Authentication strategy for Basic authentication.

    This strategy adds an Authorization header with a Basic auth token.

    Attributes:
        username (str): The username for Basic authentication.
        password (str): The password for Basic authentication.

    Methods:
        prepare_request_headers: Returns headers with the Basic auth token.
        prepare_request_params: Returns an empty dictionary.
    """

    username: str
    password: str

    def __init__(self, username: str, password: str) -> None:
        """
        Initialize a BasicAuth strategy.

        Args:
            username (str): The username for Basic authentication.
            password (str): The password for Basic authentication.
        """
        ...

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers with the Basic auth token.

        Returns:
            Dict[str, str]: Headers with the Authorization header set to "Basic {token}".
        """
        ...

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare URL parameters for the request.

        Returns:
            Dict[str, str]: An empty dictionary as Basic auth doesn't use URL parameters.
        """
        ...

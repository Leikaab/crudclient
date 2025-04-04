from typing import Dict

from crudclient.auth.base import AuthStrategy


class BearerAuth(AuthStrategy):
    """
    Authentication strategy for Bearer token authentication.

    This strategy adds an Authorization header with a Bearer token.

    Attributes:
        token (str): The Bearer token to use for authentication.

    Methods:
        prepare_request_headers: Returns headers with the Bearer token.
        prepare_request_params: Returns an empty dictionary.
    """

    token: str

    def __init__(self, token: str) -> None:
        """
        Initialize a BearerAuth strategy.

        Args:
            token (str): The Bearer token to use for authentication.
        """
        ...

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers with the Bearer token.

        Returns:
            Dict[str, str]: Headers with the Authorization header set to "Bearer {token}".
        """
        ...

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare URL parameters for the request.

        Returns:
            Dict[str, str]: An empty dictionary as Bearer auth doesn't use URL parameters.
        """
        ...

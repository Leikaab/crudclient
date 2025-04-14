from typing import Dict, Optional

from .base import AuthStrategy

class BearerAuth(AuthStrategy):
    """
    Bearer token authentication strategy.

    This strategy implements the Bearer token authentication scheme, commonly used
    in OAuth 2.0 and JWT-based APIs. It adds an "Authorization" header with the
    format "Bearer {token}" to each request.

    Note:
        An invalid or expired token may result in an `AuthenticationError` when
        making requests using this strategy.

    Attributes:
        token (str): The bearer token to use for authentication.
        header_name (str): The name of the header to use for the token. Defaults to "Authorization".
    """

    token: str
    header_name: str

    def __init__(self, token: str, header_name: str = "Authorization") -> None:
        """
        Initialize a BearerAuth strategy.

        Args:
            token (str): The bearer token to use for authentication.
            header_name (str, optional): The name of the header to use for the token.
                Defaults to "Authorization".
        """
        ...

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers for Bearer token authentication.

        Returns:
            Dict[str, str]: A dictionary containing the Authorization header with the Bearer token.
        """
        ...

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare query parameters for Bearer token authentication.

        Bearer token authentication does not use query parameters, so this method
        returns an empty dictionary.

        Returns:
            Dict[str, str]: An empty dictionary.
        """
        ...

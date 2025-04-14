from typing import Dict, Optional

from .base import AuthStrategy

class BasicAuth(AuthStrategy):
    """
    Basic authentication strategy.

    This strategy implements HTTP Basic Authentication, which sends credentials
    as a base64-encoded string in the format "username:password" in the
    Authorization header.

    Note:
        Incorrect credentials may result in an `AuthenticationError` when
        making requests using this strategy.

    Attributes:
        username (str): The username for authentication.
        password (str): The password for authentication.
    """

    username: str
    password: str

    def __init__(self, username: str, password: str) -> None:
        """
        Initialize a BasicAuth strategy.

        Args:
            username (str): The username for authentication.
            password (str): The password for authentication.
        """
        ...

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers for Basic authentication.

        Returns:
            Dict[str, str]: A dictionary containing the Authorization header with
                the Base64-encoded credentials.
        """
        ...

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare query parameters for Basic authentication.

        Basic authentication does not use query parameters, so this method
        returns an empty dictionary.

        Returns:
            Dict[str, str]: An empty dictionary.
        """
        ...

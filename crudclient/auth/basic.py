import base64
import logging
from typing import Dict

from crudclient.auth.base import AuthStrategy

log = logging.getLogger(__name__)


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
        log.debug("[BasicAuth] Initialized with username: %s (Password not logged)", username)
        self.username = username
        self.password = password

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers for Basic authentication.

        Returns:
            Dict[str, str]: A dictionary containing the Authorization header with
                the Base64-encoded credentials.
        """
        log.debug("[BasicAuth] Adding Basic Authentication header to request")
        auth_string = f"{self.username}:{self.password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {"Authorization": f"Basic {encoded_auth}"}

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare query parameters for Basic authentication.

        Basic authentication does not use query parameters, so this method
        returns an empty dictionary.

        Returns:
            Dict[str, str]: An empty dictionary.
        """
        return {}

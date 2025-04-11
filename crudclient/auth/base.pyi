from abc import ABC, abstractmethod
from typing import Dict, Optional

class AuthStrategy(ABC):
    """
    Abstract base class for authentication strategies.

    This class defines the interface that all authentication strategies must implement.
    Authentication strategies are responsible for preparing the headers and query parameters
    needed for authenticating requests to an API.

    Implementations of this class should be immutable after initialization.
    """

    @abstractmethod
    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers for authentication.

        This method should return a dictionary of headers that will be added to the request
        for authentication purposes.

        Returns:
            Dict[str, str]: A dictionary of headers for authentication.
        """
        ...

    @abstractmethod
    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare query parameters for authentication.

        This method should return a dictionary of query parameters that will be added to the
        request URL for authentication purposes.

        Returns:
            Dict[str, str]: A dictionary of query parameters for authentication.
        """
        ...

def create_auth_strategy(auth_type: str, api_key: Optional[str] = None) -> AuthStrategy:
    """
    Create an authentication strategy based on the specified type.

    This function is provided for backward compatibility with the old-style configuration.
    It creates an appropriate AuthStrategy instance based on the auth_type and api_key.

    Args:
        auth_type (str): The type of authentication to use. Can be "bearer", "basic", or "none".
        api_key (Optional[str]): The API key to use for authentication, if applicable.

    Returns:
        AuthStrategy: An instance of the appropriate AuthStrategy subclass.

    Raises:
        ValueError: If an unsupported auth_type is provided.
    """
    ...

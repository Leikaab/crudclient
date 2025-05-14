from abc import ABC, abstractmethod
from typing import Dict


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

    @abstractmethod
    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare query parameters for authentication.

        This method should return a dictionary of query parameters that will be added to the
        request URL for authentication purposes.

        Returns:
            Dict[str, str]: A dictionary of query parameters for authentication.
        """


# Alias for backward compatibility
BaseAuthStrategy = AuthStrategy

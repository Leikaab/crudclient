from abc import ABC, abstractmethod
from typing import Dict, Optional


class AuthStrategy(ABC):
    """
    Abstract base class for authentication strategies.

    This class defines the interface for all authentication strategies.
    Concrete implementations should override the prepare_request_headers
    and prepare_request_params methods to provide the specific authentication
    logic.

    Attributes:
        None

    Methods:
        prepare_request_headers: Returns headers to be included in the request.
        prepare_request_params: Returns URL parameters to be included in the request.
    """

    @abstractmethod
    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers to be included in the request.

        Returns:
            Dict[str, str]: Headers to include in the request.
        """
        ...

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare URL parameters to be included in the request.

        Returns:
            Dict[str, str]: URL parameters to include in the request.
        """
        ...

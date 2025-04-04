from typing import Callable, Dict, Optional

from crudclient.auth.base import AuthStrategy


class CustomAuth(AuthStrategy):
    """
    Authentication strategy for custom authentication methods.

    This strategy allows for custom authentication logic by providing
    callback functions for headers and URL parameters.

    Attributes:
        header_callback (Callable[[], Dict[str, str]]): A callback function that returns headers.
        param_callback (Optional[Callable[[], Dict[str, str]]]): A callback function that returns URL parameters.

    Methods:
        prepare_request_headers: Returns headers from the header_callback.
        prepare_request_params: Returns URL parameters from the param_callback.
    """

    header_callback: Callable[[], Dict[str, str]]
    param_callback: Optional[Callable[[], Dict[str, str]]]

    def __init__(
        self,
        header_callback: Callable[[], Dict[str, str]],
        param_callback: Optional[Callable[[], Dict[str, str]]] = None
    ) -> None:
        """
        Initialize a CustomAuth strategy.

        Args:
            header_callback (Callable[[], Dict[str, str]]): A callback function that returns headers.
            param_callback (Optional[Callable[[], Dict[str, str]]]): A callback function that returns URL parameters.
        """
        ...

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers using the header_callback.

        Returns:
            Dict[str, str]: Headers from the header_callback.
        """
        ...

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare URL parameters using the param_callback.

        Returns:
            Dict[str, str]: URL parameters from the param_callback, or an empty dictionary if no callback is provided.
        """
        ...


class ApiKeyAuth(AuthStrategy):
    """
    Authentication strategy for API key authentication.

    This strategy adds an API key to either the headers or URL parameters.

    Attributes:
        api_key (str): The API key to use for authentication.
        header_name (Optional[str]): The name of the header to use for the API key.
        param_name (Optional[str]): The name of the URL parameter to use for the API key.

    Methods:
        prepare_request_headers: Returns headers with the API key if header_name is provided.
        prepare_request_params: Returns URL parameters with the API key if param_name is provided.
    """

    api_key: str
    header_name: Optional[str]
    param_name: Optional[str]

    def __init__(
        self,
        api_key: str,
        header_name: Optional[str] = None,
        param_name: Optional[str] = None
    ) -> None:
        """
        Initialize an ApiKeyAuth strategy.

        Args:
            api_key (str): The API key to use for authentication.
            header_name (Optional[str]): The name of the header to use for the API key.
            param_name (Optional[str]): The name of the URL parameter to use for the API key.
        """
        ...

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers with the API key if header_name is provided.

        Returns:
            Dict[str, str]: Headers with the API key, or an empty dictionary if header_name is not provided.
        """
        ...

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare URL parameters with the API key if param_name is provided.

        Returns:
            Dict[str, str]: URL parameters with the API key, or an empty dictionary if param_name is not provided.
        """
        ...

from typing import Callable, Dict, Optional

from .base import AuthStrategy

class CustomAuth(AuthStrategy):
    """
    Custom authentication strategy.

    This strategy allows for custom authentication mechanisms by accepting
    callback functions that provide headers and/or query parameters for
    authentication. This is useful for complex authentication flows or
    when you need dynamic authentication logic.

    Note:
        Errors within the provided callbacks or incorrect authentication details
        returned by them may result in an `AuthenticationError` when making requests.

    Attributes:
        header_callback (Callable[[], Dict[str, str]]): A function that returns
            headers for authentication.
        param_callback (Optional[Callable[[], Dict[str, str]]]): A function that
            returns query parameters for authentication.
    """

    header_callback: Callable[[], Dict[str, str]]
    param_callback: Optional[Callable[[], Dict[str, str]]]

    def __init__(self, header_callback: Callable[[], Dict[str, str]], param_callback: Optional[Callable[[], Dict[str, str]]] = None) -> None:
        """
        Initialize a CustomAuth strategy.

        Args:
            header_callback (Callable[[], Dict[str, str]]): A function that returns
                headers for authentication.
            param_callback (Optional[Callable[[], Dict[str, str]]], optional): A function
                that returns query parameters for authentication. Defaults to None.
        """
        ...

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers for custom authentication.

        Returns:
            Dict[str, str]: A dictionary of headers for authentication,
                as returned by the header_callback.
        """
        ...

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare query parameters for custom authentication.

        Returns:
            Dict[str, str]: A dictionary of query parameters for authentication,
                as returned by the param_callback, or an empty dictionary if
                param_callback is None.
        """
        ...

class ApiKeyAuth(AuthStrategy):
    """
    API key authentication strategy.

    This strategy provides authentication using an API key, which can be
    included either as a header or as a query parameter.

    Note:
        An invalid API key may result in an `AuthenticationError` when
        making requests using this strategy.

    Attributes:
        api_key (str): The API key for authentication.
        header_name (str): The name of the header to use for the API key.
        param_name (Optional[str]): The name of the query parameter to use for the API key.
    """

    api_key: str
    header_name: str
    param_name: Optional[str]

    def __init__(self, api_key: str, header_name: str = "X-API-Key", param_name: Optional[str] = None) -> None:
        """
        Initialize an ApiKeyAuth strategy.

        Args:
            api_key (str): The API key for authentication.
            header_name (str, optional): The name of the header to use for the API key.
                Defaults to "X-API-Key".
            param_name (Optional[str], optional): The name of the query parameter to use
                for the API key. If provided, the API key will be sent as a query parameter
                instead of a header. Defaults to None.
        """
        ...

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers for API key authentication.

        Returns:
            Dict[str, str]: A dictionary containing the API key header,
                or an empty dictionary if param_name is provided.
        """
        ...

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare query parameters for API key authentication.

        Returns:
            Dict[str, str]: A dictionary containing the API key parameter,
                or an empty dictionary if param_name is not provided.
        """
        ...

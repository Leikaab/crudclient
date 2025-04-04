from typing import Dict, Callable, Optional
from .base import AuthStrategy


class CustomAuth(AuthStrategy):
    """
    Custom authentication strategy.

    This strategy allows for custom authentication mechanisms by accepting
    callback functions that provide headers and/or query parameters for
    authentication. This is useful for complex authentication flows or
    when you need dynamic authentication logic.

    Attributes:
        header_callback (Callable[[], Dict[str, str]]): A function that returns
            headers for authentication.
        param_callback (Optional[Callable[[], Dict[str, str]]]): A function that
            returns query parameters for authentication.
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

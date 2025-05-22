import logging
from typing import Callable, Dict, Optional

from crudclient.auth.base import AuthStrategy

log = logging.getLogger(__name__)


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

    header_callback: Optional[Callable[[], Dict[str, str]]]
    param_callback: Optional[Callable[[], Dict[str, str]]]

    def __init__(self, header_callback: Optional[Callable[[], Dict[str, str]]] = None, param_callback: Optional[Callable[[], Dict[str, str]]] = None):
        """
        Initialize a CustomAuth strategy.

        Args:
            header_callback (Optional[Callable[[], Dict[str, str]]]): A function that returns
                headers for authentication. Defaults to None.
            param_callback (Optional[Callable[[], Dict[str, str]]], optional): A function
                that returns query parameters for authentication. Defaults to None.
        """
        if header_callback is None and param_callback is None:
            raise ValueError("At least one callback must be provided")
        self.header_callback = header_callback
        self.param_callback = param_callback

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers for custom authentication.

        Returns:
            Dict[str, str]: A dictionary of headers for authentication,
                as returned by the header_callback.
        """
        if self.header_callback:
            log.debug("[CustomAuth] Invoking custom header callback to modify request")
            result = self.header_callback()
            if not isinstance(result, dict):
                raise TypeError("Header callback must return a dictionary")
            return result
        return {}

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare query parameters for custom authentication.

        Returns:
            Dict[str, str]: A dictionary of query parameters for authentication,
                as returned by the param_callback, or an empty dictionary if
                param_callback is None.
        """
        if self.param_callback:
            log.debug("[CustomAuth] Invoking custom parameter callback to modify request")
            result = self.param_callback()
            if not isinstance(result, dict):
                raise TypeError("Parameter callback must return a dictionary")
            return result
        return {}


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
        header_name (Optional[str]): The name of the header to use for the API key.
        param_name (Optional[str]): The name of the query parameter to use for the API key.
    """

    api_key: str
    header_name: Optional[str]
    param_name: Optional[str]

    def __init__(self, api_key: str, header_name: Optional[str] = None, param_name: Optional[str] = None):
        """
        Initialize an ApiKeyAuth strategy.

        Args:
            api_key (str): The API key for authentication.
            header_name (Optional[str], optional): The name of the header to use for the API key.
                Defaults to None.
            param_name (Optional[str], optional): The name of the query parameter to use
                for the API key. Defaults to None.
        """
        self.api_key = api_key
        self.header_name = header_name
        self.param_name = param_name

        # Validate that at least one of header_name or param_name is provided
        if header_name is None and param_name is None:
            raise ValueError("One of header_name or param_name must be provided")

        # Validate that only one of header_name or param_name is provided
        if header_name is not None and param_name is not None:
            raise ValueError("Only one of header_name or param_name should be provided")

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers for API key authentication.

        Returns:
            Dict[str, str]: A dictionary containing the API key header,
                or an empty dictionary if param_name is provided.
        """
        if self.header_name is not None:
            return {self.header_name: self.api_key}
        return {}

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Prepare query parameters for API key authentication.

        Returns:
            Dict[str, str]: A dictionary containing the API key parameter,
                or an empty dictionary if param_name is not provided.
        """
        if self.param_name is not None:
            return {self.param_name: self.api_key}
        return {}

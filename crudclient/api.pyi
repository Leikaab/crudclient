"""
Module `api.py`
===============

This module defines the base API class, which is the foundation for creating API clients with CRUD resources.
The API class manages client initialization, CRUD resource registration, and context management.
Users can subclass `API` to define specific endpoints and customize client behavior.

Class `API`
-----------

The `API` class provides a flexible and extensible way to interact with various endpoints of an API.
It includes methods for initializing the client, managing CRUD resources, and handling context management.

To create an API client:
    1. Subclass `API`.
    2. Define the `client_class`.
    3. Implement `_register_endpoints` to attach CRUD resources.
    4. Optionally, override other methods to customize behavior.

Example:
    class MyAPI(API):
        client_class = MyClient

        def _register_endpoints(self):
            self.contacts = Contacts(self.client)

    api = MyAPI(client_config=ClientConfig(**{'api_key': 'your_api_key'})
    contacts = api.contacts.list()

Classes:
    - API: Base class for creating API clients with CRUD resources.

Exceptions:
    - ConfigurationError: Raised for configuration-related issues, including invalid client/config or initialization problems.
"""

import logging
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Dict, Optional, Type, TypeVar, Union

from .client import Client
from .config import ClientConfig
from .crud import Crud
from .exceptions import ConfigurationError

T = TypeVar("T", bound=Crud)

class API(ABC):
    """
    Base class for creating API clients with CRUD resources.

    Attributes:
        client_class (Optional[Type[Client]]): The class used to initialize the client.
            Must be defined by subclasses.
        client (Optional[Client]): The initialized client instance.
        client_config (Optional[ClientConfig]): Configuration object for initializing the client.
        api_args (tuple): Positional arguments for potential use in API subclass.
        api_kwargs (dict): Keyword arguments for potential use in API subclass.
    """

    client_class: Optional[Type[Client]]
    client: Optional[Client]
    client_config: Optional[ClientConfig]
    api_kwargs: Dict[str, Any]

    def _assert_client(self, varname: str, Instance: Optional[Union[Client, ClientConfig]], Class: Type[Union[Client, ClientConfig]]) -> None:
        """
        Asserts that the provided `Instance` is an instance of the specified `Class` or `None`.
        Args:
            varname (str): The name of the variable being asserted.
            Instance (Client | ClientConfig | None): The instance to be checked.
            Class (Type[Client] | Type[ClientConfig]): The expected class type.
        Raises:
            ConfigurationError: If the `Instance` is not an instance of the specified `Class` or `None`.
        """
        ...

    def __init__(self, client: Optional[Client] = None, client_config: Optional[ClientConfig] = None, **kwargs: Any) -> None:
        """
        Initializes the API class.

        @param client: An existing client instance. If provided, this client will be used instead of initializing a new one.
        @type client: Optional[Client]
        @param client_config: A configuration object for initializing the client. If None, default configuration will be used.
        @type client_config: Optional[ClientConfig]
        @param args: Additional positional arguments for the API class. These are stored for potential use in API subclasses.
        @type args: tuple
        @param kwargs: Additional keyword arguments for the API class. These are stored for potential use in API subclasses.
        @type kwargs: dict

        @raises ConfigurationError: If the `client` or `client_config` is invalid, or if the client could not be initialized.
        """
        ...

    @abstractmethod
    def _register_endpoints(self) -> None:
        """
        Abstract method to register all CRUD endpoints.
        This method should be implemented by subclasses to attach CRUD resources to the API instance.

        Example:
            self.contacts = Contacts(self.client)
        """
        ...

    def _initialize_client(self) -> None:
        """
        Initializes the client using the provided client configuration.
        This method is called automatically during initialization if a client instance is not provided.

        @raises ConfigurationError: If the client could not be initialized due to missing `client_class` or other issues.
        """
        ...

    def __enter__(self) -> "API":
        """
        Enters the runtime context related to this object.

        This method initializes the client if it hasn't been initialized yet and returns the API instance.
        Typically used with the `with` statement to ensure proper setup and teardown.

        Example:
            with MyAPI() as api:
                contacts = api.contacts.list()

        @return: Returns the API instance itself for use within the `with` block.
        @rtype: API
        """
        ...

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[Any]) -> None:
        """
        Exits the runtime context related to this object.

        Closes the client session if it is open.

        @param exc_type: The exception type, if an exception was raised.
        @type exc_type: Optional[Type[BaseException]]
        @param exc_value: The exception instance, if an exception was raised.
        @type exc_value: Optional[BaseException]
        @param traceback: The traceback object, if an exception was raised.
        @type traceback: Optional[Any]
        """
        ...

    def close(self) -> None:
        """
        Closes the API client session, if it is open.

        This method ensures that the client's session is properly closed and that the client instance is set to None.
        """
        ...

    def use_custom_resource(self, resource_class: Type[T], *args: Any, **kwargs: Any) -> T:
        """
        Dynamically use custom resources that follow the CRUD structure,
        enabling the extension of the API without modifying the core API class.

        Example:
            api = MyAPI()
            contacts = api.use_custom_resource(Contacts)
            contact_list = contacts.list()

        @param resource_class: The class of the custom resource to be instantiated.
        @type resource_class: Type[T]
        @param args: Positional arguments to pass to the resource class constructor.
        @type args: Any
        @param kwargs: Keyword arguments to pass to the resource class constructor.
        @type kwargs: Any

        @return: An instance of the specified resource class, initialized with the provided arguments.
        @rtype: Crud
        """
        ...

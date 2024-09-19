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
    - InvalidClientError: Raised when an invalid client is provided.
    - InvalidClientConfigError: Raised when an invalid client configuration is provided.
    - ClientInitializationError: Raised when the client could not be initialized.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Type

from .client import Client, ClientConfig
from .crud import Crud
from .exceptions import ClientInitializationError, InvalidClientError
from .runtime_type_checkers import assert_type

# Get a logger for this module
logger = logging.getLogger(__name__)


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

    client_class: Optional[Type[Client]] = None

    def _assert_client(self, varname: str, Instance: Client | ClientConfig | None, Class: Type[Client] | Type[ClientConfig]) -> None:
        """
        Asserts that the provided `Instance` is an instance of the specified `Class` or `None`.
        Args:
            varname (str): The name of the variable being asserted.
            Instance (Client | ClientConfig | None): The instance to be checked.
            Class (Type[Client] | Type[ClientConfig]): The expected class type.
        Raises:
            InvalidClientError: If the `Instance` is not an instance of the specified `Class` or `None`.
        """

        try:
            assert_type(varname, Instance, Class, logger, optional=True)
        except TypeError as e:
            raise InvalidClientError(message=str(e))

    def __init__(self, client: Optional[Client] = None, client_config: Optional[ClientConfig] = None, **kwargs) -> None:
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

        @raises InvalidClientError: If the `client` is not an instance of Client or None.
        @raises InvalidClientConfigError: If the `client_config` is not a ClientConfig or None.
        @raises ClientInitializationError: If the client could not be initialized due to issues with the client_class or other factors.

        """
        logger.debug(f"Initializing API class with client: {client}, client_config: {client_config}")

        # Check if client is a valid Client object or None
        self._assert_client("client", client, Client)

        # Check if client_config is a valid ClientConfig object or None
        self._assert_client("client_config", client_config, ClientConfig)

        # Store the client and client configuration
        self.client: Optional[Client] = client
        self.client_config: Optional[ClientConfig] = client_config

        # Store other kwargs for potential use in API subclass
        self.api_kwargs = kwargs

        # Initialize the client if it is not provided
        if self.client is None:
            self._initialize_client()

        # Register CRUD resources
        self._register_endpoints()

    @abstractmethod
    def _register_endpoints(self) -> None:
        """
        Abstract method to register all CRUD endpoints.
        This method should be implemented by subclasses to attach CRUD resources to the API instance.

        Example:
            self.contacts = Contacts(self.client)
        """

    def _initialize_client(self) -> None:
        """
        Initializes the client using the provided client configuration.
        This method is called automatically during initialization if a client instance is not provided.

        @raises ClientInitializationError: If the client could not be initialized due to missing `client_class` or other issues.
        """

        logger.debug("Doing typechecks before initializing client.")

        # check if client_class is defined
        if not self.client_class:
            logger.error("client_class is not defined. Cannot initialize the client.")
            raise ClientInitializationError("Cannot initialize client because client_class is not set.")

        # check if client_config is defined
        if not self.client_config:
            logger.error("client_config is not defined. Cannot initialize the client.")
            raise ClientInitializationError("Cannot initialize client because client_config is not set.")

        logger.debug(f"Initializing API class with client class {self.client_class.__name__}, using client_config: {self.client_config}")

        try:
            self.client = self.client_class(config=self.client_config)
        except Exception as e:
            logger.exception("Failed to initialize the client.")
            raise ClientInitializationError("Failed to initialize the client.") from e
        logger.info("Client initialized successfully.")

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
        logger.debug("Entering API context.")
        if self.client is None:
            self._initialize_client()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the runtime context related to this object.

        Closes the client session if it is open.

        @param exc_type: The exception type, if an exception was raised.
        @type exc_type: type
        @param exc_value: The exception instance, if an exception was raised.
        @type exc_value: Exception
        @param traceback: The traceback object, if an exception was raised.
        @type traceback: traceback
        """
        logger.debug("Exiting API context.")
        self.close()
        if exc_type:
            logger.error("An exception occurred during API context.", exc_info=(exc_type, exc_value, traceback))

    def close(self) -> None:
        """
        Closes the API client session, if it is open.

        This method ensures that the client's session is properly closed and that the client instance is set to None.
        """
        if self.client:
            logger.info("Closing client session.")
            self.client.close()
        self.client = None
        logger.info("Client session fully closed and client set to None.")

    def use_custom_resource(self, resource_class: Type[Crud], *args, **kwargs) -> Crud:
        """
        Dynamically use custom resources that follow the CRUD structure,
        enabling the extension of the API without modifying the core API class.

        Example:
            api = MyAPI()
            contacts = api.use_custom_resource(Contacts)
            contact_list = contacts.list()

        @param resource_class: The class of the custom resource to be instantiated.
        @type resource_class: Type[Crud]
        @param args: Positional arguments to pass to the resource class constructor.
        @type args: tuple
        @param kwargs: Keyword arguments to pass to the resource class constructor.
        @type kwargs: dict

        @return: An instance of the specified resource class, initialized with the provided arguments.
        @rtype: Crud
        """

        assert self.client is not None, "Client must be initialized before using custom resources."
        logger.debug(f"Using custom resource: {resource_class.__name__} with args: {args} and kwargs: {kwargs}")
        return resource_class(self.client, *args, **kwargs)

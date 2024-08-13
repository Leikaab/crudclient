import logging
from abc import ABC, abstractmethod
from typing import Optional, Type

from .client import Client, ClientConfig
from .crud import Crud
from .exceptions import (
    ClientInitializationError,
    InvalidClientConfigError,
    InvalidClientError,
)

# Get a logger for this module
logger = logging.getLogger(__name__)


class API(ABC):

    client_class: Optional[Type[Client]] = None

    def __init__(
        self, client: Optional[Client] = None, client_config: Optional[ClientConfig] = None, *args, **kwargs
    ) -> None:
        """
        Initializes the API class.

        Parameters:
            client (Optional[Client]): An existing client instance. If provided, this client will be used
                instead of initializing a new one. Must be an instance of Client or None.
            client_config (Optional[ClientConfig]): ClientConfig object specifically for initializing
                the client. Used only if the `client` parameter is None. Must be a ClientConfig or None.
            *args: Additional positional arguments for the API class. Stored for potential use in API subclasses.
            **kwargs: Additional keyword arguments for the API class. Stored for potential use in API subclasses.

        Raises:
            InvalidClientError: If `client` is not an instance of Client or None.
            InvalidClientConfigError: If `client_config` is not a ClientConfig or None.
            ClientInitializationError: If the client could not be initialized.
        """
        logger.debug("Initializing API class.")

        # Check if client is a valid Client object
        if not (client is None or isinstance(client, Client)):
            logger.error(f"Invalid client provided: expected Client or None, got {type(client).__name__}.")
            raise InvalidClientError(
                f"client must be an instance of Client or None, got {
                    type(client).__name__} instead."
            )

        # Check if client_config is a valid ClientConfig object
        if not (client_config is None or isinstance(client_config, ClientConfig)):
            logger.error(
                f"Invalid client_config provided: expected ClientConfig or None, got {
                    type(client_config).__name__}."
            )
            raise InvalidClientConfigError(
                f"client_config must be a ClientConfig or None, got {
                    type(client_config).__name__} instead."
            )

        # Store the client and client configuration
        self.client: Optional[Client] = client
        self.client_config: Optional[ClientConfig] = client_config

        # Store other args/kwargs for potential use in API subclass
        self.api_args = args
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
        pass

    def _initialize_client(self) -> None:
        """
        Initializes the client using the provided client configuration.
        This method is called automatically during initialization if a client instance is not provided.

        Raises:
            ValueError: If `client_class` is not provided.
        """
        logger.debug("Initializing client.")

        # check if client_class is defined
        if not self.client_class:
            logger.error("client_class is not defined. Cannot initialize the client.")
            raise ValueError("client_class must be provided to initialize the client.")

        try:
            self.client = self.client_class(**self.client_config)
        except Exception as e:
            logger.exception("Failed to initialize the client.")
            raise ClientInitializationError("Failed to initialize the client.") from e
        logger.info("Client initialized successfully.")

    def __enter__(self) -> "API":
        """
        Enters the runtime context related to this object.

        Ensures that the client is initialized before entering the context.

        Returns:
            API: Returns the API instance itself for use within the `with` block.
        """
        logger.debug("Entering API context.")
        if self.client is None:
            self._initialize_client()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exits the runtime context related to this object.

        Closes the client session if it is open.

        Parameters:
            exc_type (type): The exception type, if an exception was raised.
            exc_value (Exception): The exception instance, if an exception was raised.
            traceback (traceback): The traceback object, if an exception was raised.
        """
        logger.debug("Exiting API context.")
        self.close()
        if exc_type:
            logger.error("An exception occurred during API context.", exc_info=(exc_type, exc_value, traceback))

    def close(self) -> None:
        """
        Closes the API client session, if it is open.
        """
        if self.client:
            logger.info("Closing client session.")
            self.client.close()
        self.client = None
        logger.info("Client session fully closed and client set to None.")

    def use_custom_resource(self, resource_class: Type[Crud], *args, **kwargs) -> Crud:
        """
        Allows for the dynamic use of custom resources that follow the CRUD structure,
        enabling the extension of the API without modifying the core API class.

        Parameters:
            resource_class (Type[Crud]): The class of the custom resource to be instantiated.
            *args: Positional arguments to pass to the resource class constructor.
            **kwargs: Keyword arguments to pass to the resource class constructor.

        Returns:
            Crud: An instance of the specified resource class, initialized with the provided arguments.
        """
        logger.debug(f"Using custom resource: {resource_class.__name__} with args: {args} and kwargs: {kwargs}")
        return resource_class(self.client, *args, **kwargs)

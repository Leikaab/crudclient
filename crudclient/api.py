import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Type, Union

from .client import Client
from .config import ClientConfig
from .crud import Crud
from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class API(ABC):

    client_class: Optional[Type[Client]] = None

    def _assert_client(self, varname: str, Instance: Optional[Union[Client, ClientConfig]], Class: Union[Type[Client], Type[ClientConfig]]) -> None:
        if not (Instance is None or isinstance(Instance, Class)):
            if isinstance(Class, tuple):
                expected_classes = " or ".join([cls.__name__ for cls in Class])
            else:
                expected_classes = Class.__name__
            message = f"Invalid {varname} provided: expected {expected_classes} or None, got {type(Instance).__name__}."
            logger.error(message)
            raise ConfigurationError(message=message)

    def __init__(self, client: Optional[Client] = None, client_config: Optional[ClientConfig] = None, **kwargs: Any) -> None:
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
        pass

    def _initialize_client(self) -> None:
        logger.debug("Doing typechecks before initializing client.")

        # check if client_class is defined
        if not self.client_class:
            logger.error("client_class is not defined. Cannot initialize the client.")
            raise ConfigurationError("Cannot initialize client because client_class is not set.")

        # check if client_config is defined
        if not self.client_config:
            logger.error("client_config is not defined. Cannot initialize the client.")
            raise ConfigurationError("Cannot initialize client because client_config is not set.")

        logger.debug(f"Initializing API class with client class {self.client_class.__name__}, using client_config: {self.client_config}")

        try:
            self.client = self.client_class(config=self.client_config)
        except Exception as e:
            logger.exception("Failed to initialize the client.")
            raise ConfigurationError("Failed to initialize the client.") from e
        logger.info("Client initialized successfully.")

    def __enter__(self) -> "API":
        logger.debug("Entering API context.")
        if self.client is None:
            self._initialize_client()
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Optional[Any]) -> None:
        logger.debug("Exiting API context.")
        self.close()
        if exc_type:
            logger.error("An exception occurred during API context.", exc_info=True)

    def close(self) -> None:
        if self.client:
            logger.info("Closing client session.")
            self.client.close()
        self.client = None
        logger.info("Client session fully closed and client set to None.")

    def use_custom_resource(self, resource_class: Type[Crud], *args: Any, **kwargs: Any) -> Crud:

        assert self.client is not None, "Client must be initialized before using custom resources."
        logger.debug(f"Using custom resource: {resource_class.__name__} with args: {args} and kwargs: {kwargs}")
        return resource_class(self.client, *args, **kwargs)

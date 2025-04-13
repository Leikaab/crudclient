from typing import Any, Dict, List, Optional, Type

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig

from .stubs_crud import StubCrud

class StubAPI(API):
    """
    A stub implementation of the API class for testing, managing multiple stubbed endpoints.

    This class facilitates testing scenarios involving multiple related API resources
    by providing a way to register `StubCrud` instances for different endpoints,
    all potentially sharing a common underlying `StubClient` and a shared, partitioned
    in-memory data store.

    Attributes:
        client_class: The class to use for the client (defaults to `crudclient.Client`).
                      Can be set to `StubClient` for full stubbing.
        endpoints: A dictionary mapping registered endpoint names to their `StubCrud` instances.
        _data_store: A dictionary holding the data for all registered endpoints,
                     partitioned by endpoint name. The structure is:
                     `{endpoint_name: {resource_id: resource_dict}}`.
    """

    client_class: Type[Client]
    endpoints: Dict[str, StubCrud]
    _data_store: Dict[str, Dict[str, Dict[str, Any]]]

    def __init__(self, client: Optional[Client] = None, client_config: Optional[ClientConfig] = None, **kwargs: Any) -> None:
        """
        Initialize the StubAPI.

        Args:
            client: An optional pre-configured client instance (e.g., a `StubClient`).
                    If None, a default client (based on `client_class`) is created.
            client_config: Configuration for the client. If None, a default stub
                           configuration (`hostname="https://stub.api.example.com"`) is used.
            **kwargs: Additional arguments passed to the base API constructor.
        """
        ...

    def register_endpoint(self, name: str, endpoint: str, model: Optional[Type[Any]] = None, **kwargs: Any) -> StubCrud:
        """
        Register a new stubbed CRUD endpoint associated with this API instance.

        Creates a `StubCrud` instance for the given endpoint path and model,
        assigns it a dedicated partition within the shared `_data_store`, and
        makes it accessible as an attribute of the `StubAPI` instance using the provided `name`.

        Args:
            name: The attribute name for accessing the endpoint (e.g., `api.users`).
            endpoint: The API path prefix for this endpoint (e.g., '/users').
            model: The Pydantic model or class representing resources for this endpoint.
            **kwargs: Additional keyword arguments passed directly to the `StubCrud` constructor.

        Returns:
            The newly created and registered `StubCrud` instance.
        """
        ...

    def _register_endpoints(self) -> None:
        """Internal method override; endpoints are registered via `register_endpoint`."""
        ...

    def __getattr__(self, name: str) -> StubCrud:
        """
        Provide attribute-style access to registered `StubCrud` endpoints.

        Args:
            name: The name of the attribute being accessed.

        Returns:
            The `StubCrud` instance associated with `name`.

        Raises:
            AttributeError: If `name` does not correspond to a registered endpoint.
        """
        ...

    def get_data_store(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Retrieve the complete, partitioned data store for all registered endpoints.

        Returns:
            The dictionary containing all data, keyed by endpoint name.
        """
        ...

    def clear_data_store(self) -> None:
        """
        Clear all data from the data stores of all registered endpoints and reset
        their internal ID counters.
        """
        ...

    def populate_data_store(self, endpoint_name: str, data: List[Dict[str, Any]]) -> None:
        """
        Populate the data store for a specific registered endpoint with initial data.

        If an item in the `data` list does not have an 'id' key, a random UUID
        will be generated and assigned. Updates the `_next_id` counter of the
        corresponding `StubCrud` instance based on the maximum numeric ID found.

        Args:
            endpoint_name: The name of the endpoint (must have been registered).
            data: A list of dictionaries, where each dictionary represents a resource.
        """
        ...

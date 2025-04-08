"""
Stub implementations for Client, API, and CRUD operations.
"""

from typing import Any, Dict, List, Optional, Type, Union, Callable

from crudclient.client import Client
from crudclient.api import API
from crudclient.config import ClientConfig
from crudclient.types import RawResponseSimple


class StubCrud:
    """
    Stub implementation of CRUD operations.

    This class provides configurable stub implementations of CRUD operations
    that can be used for testing.
    """

    def __init__(
        self,
        name: str,
        endpoint: str,
        model: Optional[Type[Any]] = None,
        **kwargs: Any
    ):
        """
        Initialize the stub CRUD.

        Args:
            name: Name of the endpoint
            endpoint: API endpoint
            model: Optional model class
            **kwargs: Additional arguments
        """
        self.name = name
        self.endpoint = endpoint
        self.model = model
        self.config = kwargs

        # Default responses
        self.list_response: Any = []
        self.get_response: Any = None
        self.create_response: Any = None
        self.update_response: Any = None
        self.delete_response: bool = True
        self.bulk_create_response: List[Any] = []
        self.bulk_update_response: List[Any] = []
        self.bulk_delete_response: int = 0

        # Custom handlers
        self.list_handler: Optional[Callable[..., Any]] = None
        self.get_handler: Optional[Callable[..., Any]] = None
        self.create_handler: Optional[Callable[..., Any]] = None
        self.update_handler: Optional[Callable[..., Any]] = None
        self.delete_handler: Optional[Callable[..., Any]] = None
        self.bulk_create_handler: Optional[Callable[..., Any]] = None
        self.bulk_update_handler: Optional[Callable[..., Any]] = None
        self.bulk_delete_handler: Optional[Callable[..., Any]] = None

    def configure_list(
        self,
        response: Any = None,
        handler: Optional[Callable[..., Any]] = None
    ) -> 'StubCrud':
        """
        Configure list operation.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.list_response = response

        if handler is not None:
            self.list_handler = handler

        return self

    def configure_get(
        self,
        response: Any = None,
        handler: Optional[Callable[..., Any]] = None
    ) -> 'StubCrud':
        """
        Configure get operation.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.get_response = response

        if handler is not None:
            self.get_handler = handler

        return self

    def configure_create(
        self,
        response: Any = None,
        handler: Optional[Callable[..., Any]] = None
    ) -> 'StubCrud':
        """
        Configure create operation.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.create_response = response

        if handler is not None:
            self.create_handler = handler

        return self

    def configure_update(
        self,
        response: Any = None,
        handler: Optional[Callable[..., Any]] = None
    ) -> 'StubCrud':
        """
        Configure update operation.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.update_response = response

        if handler is not None:
            self.update_handler = handler

        return self

    def configure_delete(
        self,
        response: bool = True,
        handler: Optional[Callable[..., Any]] = None
    ) -> 'StubCrud':
        """
        Configure delete operation.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.delete_response = response

        if handler is not None:
            self.delete_handler = handler

        return self

    def configure_bulk_create(
        self,
        response: Optional[List[Any]] = None,
        handler: Optional[Callable[..., Any]] = None
    ) -> 'StubCrud':
        """
        Configure bulk_create operation.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.bulk_create_response = response

        if handler is not None:
            self.bulk_create_handler = handler

        return self

    def configure_bulk_update(
        self,
        response: Optional[List[Any]] = None,
        handler: Optional[Callable[..., Any]] = None
    ) -> 'StubCrud':
        """
        Configure bulk_update operation.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.bulk_update_response = response

        if handler is not None:
            self.bulk_update_handler = handler

        return self

    def configure_bulk_delete(
        self,
        response: int = 0,
        handler: Optional[Callable[..., Any]] = None
    ) -> 'StubCrud':
        """
        Configure bulk_delete operation.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.bulk_delete_response = response

        if handler is not None:
            self.bulk_delete_handler = handler

        return self

    def list(self, **kwargs: Any) -> Any:
        """
        List resources.

        Args:
            **kwargs: Query parameters

        Returns:
            List of resources
        """
        if self.list_handler:
            return self.list_handler(**kwargs)

        return self.list_response

    def get(self, id: Any, **kwargs: Any) -> Any:
        """
        Get a resource by ID.

        Args:
            id: Resource ID
            **kwargs: Additional arguments

        Returns:
            Resource or None if not found
        """
        if self.get_handler:
            return self.get_handler(id, **kwargs)

        return self.get_response

    def create(self, data: Any, **kwargs: Any) -> Any:
        """
        Create a resource.

        Args:
            data: Resource data
            **kwargs: Additional arguments

        Returns:
            Created resource
        """
        if self.create_handler:
            return self.create_handler(data, **kwargs)

        return self.create_response

    def update(self, id: Any, data: Any, **kwargs: Any) -> Any:
        """
        Update a resource.

        Args:
            id: Resource ID
            data: Resource data
            **kwargs: Additional arguments

        Returns:
            Updated resource or None if not found
        """
        if self.update_handler:
            return self.update_handler(id, data, **kwargs)

        return self.update_response

    def delete(self, id: Any, **kwargs: Any) -> bool:
        """
        Delete a resource.

        Args:
            id: Resource ID
            **kwargs: Additional arguments

        Returns:
            True if deleted, False if not found
        """
        if self.delete_handler:
            return self.delete_handler(id, **kwargs)

        return self.delete_response

    def bulk_create(self, data: List[Any], **kwargs: Any) -> List[Any]:
        """
        Create multiple resources.

        Args:
            data: List of resource data
            **kwargs: Additional arguments

        Returns:
            List of created resources
        """
        if self.bulk_create_handler:
            return self.bulk_create_handler(data, **kwargs)

        return self.bulk_create_response

    def bulk_update(self, data: List[Any], **kwargs: Any) -> List[Any]:
        """
        Update multiple resources.

        Args:
            data: List of resource data with IDs
            **kwargs: Additional arguments

        Returns:
            List of updated resources or None for items not found
        """
        if self.bulk_update_handler:
            return self.bulk_update_handler(data, **kwargs)

        return self.bulk_update_response

    def bulk_delete(self, ids: List[Any], **kwargs: Any) -> int:
        """
        Delete multiple resources.

        Args:
            ids: List of resource IDs
            **kwargs: Additional arguments

        Returns:
            Number of deleted resources
        """
        if self.bulk_delete_handler:
            return self.bulk_delete_handler(ids, **kwargs)

        return self.bulk_delete_response


class StubAPI(API):
    """
    Stub implementation of API.

    This class provides a configurable stub implementation of the API
    that can be used for testing.
    """

    def __init__(
        self,
        client: Optional[Client] = None,
        client_config: Optional[ClientConfig] = None,
        **kwargs: Any
    ):
        """
        Initialize the stub API.

        Args:
            client: Optional client instance
            client_config: Optional client configuration
            **kwargs: Additional arguments
        """
        super().__init__(client, client_config, **kwargs)

    def _register_endpoints(self) -> None:
        """
        Register endpoints.

        This method is required by the API abstract base class.
        """
        pass
        self.endpoints: Dict[str, StubCrud] = {}

    def register_endpoint(
        self,
        name: str,
        endpoint: str,
        model: Optional[Type[Any]] = None,
        **kwargs: Any
    ) -> StubCrud:
        """
        Register an endpoint.

        Args:
            name: Name of the endpoint
            endpoint: API endpoint
            model: Optional model class
            **kwargs: Additional arguments

        Returns:
            CRUD interface
        """
        crud = StubCrud(name, endpoint, model, **kwargs)
        self.endpoints[name] = crud
        setattr(self, name, crud)
        return crud

    def __getattr__(self, name: str) -> Any:
        """
        Get an endpoint by name.

        Args:
            name: Name of the endpoint

        Returns:
            CRUD interface
        """
        if name in self.endpoints:
            return self.endpoints[name]

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class StubClient(Client):
    """
    Stub implementation of Client.

    This class provides a configurable stub implementation of the Client
    that can be used for testing.
    """

    def __init__(
        self,
        config: Union[ClientConfig, Dict[str, Any]],
        **kwargs: Any
    ):
        """
        Initialize the stub client.

        Args:
            config: Client configuration
            **kwargs: Additional arguments
        """
        super().__init__(config)

        # Default responses
        self.get_response: RawResponseSimple = {}
        self.post_response: RawResponseSimple = {}
        self.put_response: RawResponseSimple = {}
        self.delete_response: RawResponseSimple = {}
        self.patch_response: RawResponseSimple = {}

        # Custom handlers
        self.get_handler: Optional[Callable[..., RawResponseSimple]] = None
        self.post_handler: Optional[Callable[..., RawResponseSimple]] = None
        self.put_handler: Optional[Callable[..., RawResponseSimple]] = None
        self.delete_handler: Optional[Callable[..., RawResponseSimple]] = None
        self.patch_handler: Optional[Callable[..., RawResponseSimple]] = None

    def configure_get(
        self,
        response: Optional[RawResponseSimple] = None,
        handler: Optional[Callable[..., RawResponseSimple]] = None
    ) -> 'StubClient':
        """
        Configure GET method.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.get_response = response

        if handler is not None:
            self.get_handler = handler

        return self

    def configure_post(
        self,
        response: Optional[RawResponseSimple] = None,
        handler: Optional[Callable[..., RawResponseSimple]] = None
    ) -> 'StubClient':
        """
        Configure POST method.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.post_response = response

        if handler is not None:
            self.post_handler = handler

        return self

    def configure_put(
        self,
        response: Optional[RawResponseSimple] = None,
        handler: Optional[Callable[..., RawResponseSimple]] = None
    ) -> 'StubClient':
        """
        Configure PUT method.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.put_response = response

        if handler is not None:
            self.put_handler = handler

        return self

    def configure_delete(
        self,
        response: Optional[RawResponseSimple] = None,
        handler: Optional[Callable[..., RawResponseSimple]] = None
    ) -> 'StubClient':
        """
        Configure DELETE method.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.delete_response = response

        if handler is not None:
            self.delete_handler = handler

        return self

    def configure_patch(
        self,
        response: Optional[RawResponseSimple] = None,
        handler: Optional[Callable[..., RawResponseSimple]] = None
    ) -> 'StubClient':
        """
        Configure PATCH method.

        Args:
            response: Response to return
            handler: Custom handler function

        Returns:
            Self for chaining
        """
        if response is not None:
            self.patch_response = response

        if handler is not None:
            self.patch_handler = handler

        return self

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
        """
        Perform a GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response
        """
        if self.get_handler:
            return self.get_handler(endpoint, params=params)

        return self.get_response

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Perform a POST request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Response
        """
        if self.post_handler:
            return self.post_handler(endpoint, data=data, json=json, files=files)

        return self.post_response

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Perform a PUT request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Response
        """
        if self.put_handler:
            return self.put_handler(endpoint, data=data, json=json, files=files)

        return self.put_response

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        """
        Perform a DELETE request.

        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments

        Returns:
            Response
        """
        if self.delete_handler:
            return self.delete_handler(endpoint, **kwargs)

        return self.delete_response

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Perform a PATCH request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Response
        """
        if self.patch_handler:
            return self.patch_handler(endpoint, data=data, json=json, files=files)

        return self.patch_response

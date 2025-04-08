"""
FakeAPI implementation for testing with an in-memory database.
"""

import copy
import re
import uuid
from typing import Any, Dict, List, Optional, Type, Union, Callable

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig


class FakeDatabase:
    """
    In-memory database for FakeAPI.

    This class provides CRUD operations on an in-memory data store,
    with support for filtering, sorting, and pagination.
    """

    def __init__(self):
        """Initialize the in-memory database."""
        self.data: Dict[str, List[Dict[str, Any]]] = {}

    def get_collection(self, name: str) -> List[Dict[str, Any]]:
        """
        Get a collection by name.

        Args:
            name: Collection name

        Returns:
            List of resources
        """
        if name not in self.data:
            self.data[name] = []

        return self.data[name]

    def list(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_desc: bool = False,
        page: int = 1,
        page_size: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        List resources in a collection with filtering, sorting, and pagination.

        Args:
            collection: Collection name
            filters: Optional filters
            sort_by: Optional field to sort by
            sort_desc: Sort in descending order
            page: Page number (1-based)
            page_size: Page size

        Returns:
            List of resources
        """
        data = self.get_collection(collection)

        # Apply filters
        if filters:
            data = self._apply_filters(data, filters)

        # Apply sorting
        if sort_by:
            data = self._apply_sorting(data, sort_by, sort_desc)

        # Apply pagination
        if page_size:
            data = self._apply_pagination(data, page, page_size)

        return copy.deepcopy(data)

    def get(self, collection: str, id: Any) -> Optional[Dict[str, Any]]:
        """
        Get a resource by ID.

        Args:
            collection: Collection name
            id: Resource ID

        Returns:
            Resource or None if not found
        """
        data = self.get_collection(collection)

        for item in data:
            if item.get('id') == id:
                return copy.deepcopy(item)

        return None

    def create(self, collection: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a resource.

        Args:
            collection: Collection name
            data: Resource data

        Returns:
            Created resource
        """
        collection_data = self.get_collection(collection)

        # Generate ID if not provided
        if 'id' not in data:
            data['id'] = str(uuid.uuid4())

        # Create a copy to avoid modifying the original
        new_item = copy.deepcopy(data)
        collection_data.append(new_item)

        return copy.deepcopy(new_item)

    def update(self, collection: str, id: Any, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a resource.

        Args:
            collection: Collection name
            id: Resource ID
            data: Resource data

        Returns:
            Updated resource or None if not found
        """
        collection_data = self.get_collection(collection)

        for i, item in enumerate(collection_data):
            if item.get('id') == id:
                # Create a copy of the original item
                updated_item = copy.deepcopy(item)

                # Update with new data
                updated_item.update(data)

                # Ensure ID is preserved
                updated_item['id'] = id

                # Replace the item in the collection
                collection_data[i] = updated_item

                return copy.deepcopy(updated_item)

        return None

    def delete(self, collection: str, id: Any) -> bool:
        """
        Delete a resource.

        Args:
            collection: Collection name
            id: Resource ID

        Returns:
            True if deleted, False if not found
        """
        collection_data = self.get_collection(collection)

        for i, item in enumerate(collection_data):
            if item.get('id') == id:
                del collection_data[i]
                return True

        return False

    def bulk_create(self, collection: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple resources.

        Args:
            collection: Collection name
            items: List of resource data

        Returns:
            List of created resources
        """
        created_items = []

        for item in items:
            created_item = self.create(collection, item)
            created_items.append(created_item)

        return created_items

    def bulk_update(self, collection: str, items: List[Dict[str, Any]]) -> List[Optional[Dict[str, Any]]]:
        """
        Update multiple resources.

        Args:
            collection: Collection name
            items: List of resource data with IDs

        Returns:
            List of updated resources or None for items not found
        """
        updated_items = []

        for item in items:
            if 'id' not in item:
                updated_items.append(None)
                continue

            updated_item = self.update(collection, item['id'], item)
            updated_items.append(updated_item)

        return updated_items

    def bulk_delete(self, collection: str, ids: List[Any]) -> int:
        """
        Delete multiple resources.

        Args:
            collection: Collection name
            ids: List of resource IDs

        Returns:
            Number of deleted resources
        """
        deleted_count = 0

        for id in ids:
            if self.delete(collection, id):
                deleted_count += 1

        return deleted_count

    def _apply_filters(self, data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Apply filters to data.

        Args:
            data: List of resources
            filters: Filters to apply

        Returns:
            Filtered data
        """
        filtered_data = []

        for item in data:
            match = True

            for key, value in filters.items():
                # Handle nested keys with dot notation
                if '.' in key:
                    parts = key.split('.')
                    item_value = item
                    for part in parts:
                        if isinstance(item_value, dict) and part in item_value:
                            item_value = item_value[part]
                        else:
                            item_value = None
                            break
                else:
                    item_value = item.get(key)

                # Handle different filter types
                if callable(value):
                    # Function filter
                    if not value(item_value):
                        match = False
                        break
                elif isinstance(value, dict):
                    # Operator filter
                    if not self._apply_operator_filter(item_value, value):
                        match = False
                        break
                elif isinstance(value, str) and value.startswith('regex:'):
                    # Regex filter
                    pattern = value[6:]
                    if not isinstance(item_value, str) or not re.search(pattern, item_value):
                        match = False
                        break
                elif item_value != value:
                    # Exact match filter
                    match = False
                    break

            if match:
                filtered_data.append(item)

        return filtered_data

    def _apply_operator_filter(self, value: Any, operators: Dict[str, Any]) -> bool:
        """
        Apply operator filters.

        Args:
            value: Value to filter
            operators: Operator filters

        Returns:
            True if value matches all operators
        """
        for op, op_value in operators.items():
            if op == '$eq':
                if value != op_value:
                    return False
            elif op == '$ne':
                if value == op_value:
                    return False
            elif op == '$gt':
                if not value > op_value:
                    return False
            elif op == '$gte':
                if not value >= op_value:
                    return False
            elif op == '$lt':
                if not value < op_value:
                    return False
            elif op == '$lte':
                if not value <= op_value:
                    return False
            elif op == '$in':
                if value not in op_value:
                    return False
            elif op == '$nin':
                if value in op_value:
                    return False
            elif op == '$exists':
                if op_value and value is None:
                    return False
                if not op_value and value is not None:
                    return False

        return True

    def _apply_sorting(
        self,
        data: List[Dict[str, Any]],
        sort_by: str,
        sort_desc: bool
    ) -> List[Dict[str, Any]]:
        """
        Apply sorting to data.

        Args:
            data: List of resources
            sort_by: Field to sort by
            sort_desc: Sort in descending order

        Returns:
            Sorted data
        """
        def get_sort_key(item: Dict[str, Any]) -> Any:
            # Handle nested keys with dot notation
            if '.' in sort_by:
                parts = sort_by.split('.')
                value = item
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        return None
                return value
            else:
                return item.get(sort_by)

        return sorted(data, key=get_sort_key, reverse=sort_desc)

    def _apply_pagination(
        self,
        data: List[Dict[str, Any]],
        page: int,
        page_size: int
    ) -> List[Dict[str, Any]]:
        """
        Apply pagination to data.

        Args:
            data: List of resources
            page: Page number (1-based)
            page_size: Page size

        Returns:
            Paginated data
        """
        start = (page - 1) * page_size
        end = start + page_size

        return data[start:end]


class FakeCrud:
    """
    Fake CRUD implementation for FakeAPI.

    This class provides CRUD operations on a collection in the FakeDatabase.
    """

    def __init__(
        self,
        database: FakeDatabase,
        collection: str,
        model: Optional[Type[Any]] = None
    ):
        """
        Initialize the fake CRUD.

        Args:
            database: FakeDatabase instance
            collection: Collection name
            model: Optional model class
        """
        self.database = database
        self.collection = collection
        self.model = model

    def list(self, **kwargs: Any) -> Any:
        """
        List resources.

        Args:
            **kwargs: Query parameters

        Returns:
            List of resources
        """
        # Extract pagination and sorting parameters
        filters = kwargs.pop('filters', {})
        sort_by = kwargs.pop('sort_by', None)
        sort_desc = kwargs.pop('sort_desc', False)
        page = kwargs.pop('page', 1)
        page_size = kwargs.pop('page_size', None)

        # Add remaining kwargs to filters
        filters.update(kwargs)

        # Get data from database
        data = self.database.list(
            self.collection,
            filters=filters,
            sort_by=sort_by,
            sort_desc=sort_desc,
            page=page,
            page_size=page_size,
        )

        # Convert to model instances if model is provided
        if self.model:
            return [self.model(**item) for item in data]

        return data

    def get(self, id: Any, **kwargs: Any) -> Any:
        """
        Get a resource by ID.

        Args:
            id: Resource ID
            **kwargs: Additional arguments

        Returns:
            Resource or None if not found
        """
        data = self.database.get(self.collection, id)

        if data is None:
            return None

        # Convert to model instance if model is provided
        if self.model:
            return self.model(**data)

        return data

    def create(self, data: Any, **kwargs: Any) -> Any:
        """
        Create a resource.

        Args:
            data: Resource data
            **kwargs: Additional arguments

        Returns:
            Created resource
        """
        # Convert model instance to dict if needed
        if hasattr(data, '__dict__'):
            data_dict = {k: v for k, v in data.__dict__.items() if not k.startswith('_')}
        else:
            data_dict = data

        created_data = self.database.create(self.collection, data_dict)

        # Convert to model instance if model is provided
        if self.model:
            return self.model(**created_data)

        return created_data

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
        # Convert model instance to dict if needed
        if hasattr(data, '__dict__'):
            data_dict = {k: v for k, v in data.__dict__.items() if not k.startswith('_')}
        else:
            data_dict = data

        updated_data = self.database.update(self.collection, id, data_dict)

        if updated_data is None:
            return None

        # Convert to model instance if model is provided
        if self.model:
            return self.model(**updated_data)

        return updated_data

    def delete(self, id: Any, **kwargs: Any) -> bool:
        """
        Delete a resource.

        Args:
            id: Resource ID
            **kwargs: Additional arguments

        Returns:
            True if deleted, False if not found
        """
        return self.database.delete(self.collection, id)

    def bulk_create(self, data: List[Any], **kwargs: Any) -> List[Any]:
        """
        Create multiple resources.

        Args:
            data: List of resource data
            **kwargs: Additional arguments

        Returns:
            List of created resources
        """
        # Convert model instances to dicts if needed
        data_dicts = []
        for item in data:
            if hasattr(item, '__dict__'):
                data_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
            else:
                data_dict = item

            data_dicts.append(data_dict)

        created_data = self.database.bulk_create(self.collection, data_dicts)

        # Convert to model instances if model is provided
        if self.model:
            return [self.model(**item) for item in created_data]

        return created_data

    def bulk_update(self, data: List[Any], **kwargs: Any) -> List[Any]:
        """
        Update multiple resources.

        Args:
            data: List of resource data with IDs
            **kwargs: Additional arguments

        Returns:
            List of updated resources or None for items not found
        """
        # Convert model instances to dicts if needed
        data_dicts = []
        for item in data:
            if hasattr(item, '__dict__'):
                data_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
            else:
                data_dict = item

            data_dicts.append(data_dict)

        updated_data = self.database.bulk_update(self.collection, data_dicts)

        # Convert to model instances if model is provided
        if self.model:
            return [self.model(**item) if item is not None else None for item in updated_data]

        return updated_data

    def bulk_delete(self, ids: List[Any], **kwargs: Any) -> int:
        """
        Delete multiple resources.

        Args:
            ids: List of resource IDs
            **kwargs: Additional arguments

        Returns:
            Number of deleted resources
        """
        return self.database.bulk_delete(self.collection, ids)


class FakeAPI(API):
    """
    Fake API implementation with an in-memory database.

    This class simulates a real API with an in-memory database,
    supporting CRUD operations, filtering, sorting, and pagination.
    """

    def _register_endpoints(self) -> None:
        """
        Register endpoints.

        This method is required by the API abstract base class.
        """
        pass
    """
    Fake API implementation with an in-memory database.

    This class simulates a real API with an in-memory database,
    supporting CRUD operations, filtering, sorting, and pagination.
    """

    def __init__(
        self,
        client: Optional[Client] = None,
        client_config: Optional[ClientConfig] = None,
        **kwargs: Any
    ):
        """
        Initialize the fake API.

        Args:
            client: Optional client instance
            client_config: Optional client configuration
            **kwargs: Additional arguments
        """
        super().__init__(client, client_config, **kwargs)
        self.database = FakeDatabase()
        self.endpoints: Dict[str, FakeCrud] = {}

    def register_endpoint(
        self,
        name: str,
        endpoint: str,
        model: Optional[Type[Any]] = None,
        **kwargs: Any
    ) -> FakeCrud:
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
        crud = FakeCrud(self.database, name, model)
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

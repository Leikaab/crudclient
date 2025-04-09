"""
FakeAPI implementation for testing with a sophisticated in-memory database.

This module provides a realistic fake implementation of the crudclient.API class
with an in-memory database that supports relationships, filtering, sorting, pagination,
and more.
"""

from typing import Any, Dict, List, Optional, Type, Union

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig

from .data_store import DataStore


class FakeCrud:
    """
    Fake CRUD implementation for FakeAPI.

    This class provides CRUD operations on a collection in the DataStore,
    with support for relationships, filtering, sorting, pagination, and validation.
    """

    def __init__(
        self,
        database: DataStore,
        collection: str,
        model: Optional[Type[Any]] = None
    ):
        """
        Initialize the fake CRUD.

        Args:
            database: DataStore instance
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
        # Extract pagination, sorting, and filtering parameters
        filters = kwargs.pop('filters', {})
        sort_by = kwargs.pop('sort_by', None)
        sort_desc = kwargs.pop('sort_desc', False)
        page = kwargs.pop('page', 1)
        page_size = kwargs.pop('page_size', None)
        include_deleted = kwargs.pop('include_deleted', False)
        include_related = kwargs.pop('include_related', None)
        fields = kwargs.pop('fields', None)

        # Add remaining kwargs to filters
        filters.update(kwargs)

        # Get data from database
        result = self.database.list(
            self.collection,
            filters=filters,
            sort_by=sort_by,
            sort_desc=sort_desc,
            page=page,
            page_size=page_size,
            include_deleted=include_deleted,
            include_related=include_related,
            fields=fields,
        )

        data = result['data']

        # Convert to model instances if model is provided
        if self.model:
            data = [self.model(**item) for item in data]

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
        include_deleted = kwargs.pop('include_deleted', False)
        include_related = kwargs.pop('include_related', None)
        fields = kwargs.pop('fields', None)

        data = self.database.get(
            self.collection,
            id,
            include_deleted=include_deleted,
            include_related=include_related,
            fields=fields,
        )

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
        skip_validation = kwargs.pop('skip_validation', False)

        # Convert model instance to dict if needed
        if hasattr(data, '__dict__'):
            data_dict = {k: v for k, v in data.__dict__.items() if not k.startswith('_')}
        else:
            data_dict = data

        created_data = self.database.create(
            self.collection,
            data_dict,
            skip_validation=skip_validation
        )

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
        skip_validation = kwargs.pop('skip_validation', False)
        check_version = kwargs.pop('check_version', True)

        # Convert model instance to dict if needed
        if hasattr(data, '__dict__'):
            data_dict = {k: v for k, v in data.__dict__.items() if not k.startswith('_')}
        else:
            data_dict = data

        updated_data = self.database.update(
            self.collection,
            id,
            data_dict,
            skip_validation=skip_validation,
            check_version=check_version
        )

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
        soft_delete = kwargs.pop('soft_delete', False)
        cascade = kwargs.pop('cascade', False)

        return self.database.delete(
            self.collection,
            id,
            soft_delete=soft_delete,
            cascade=cascade
        )

    def bulk_create(self, data: List[Any], **kwargs: Any) -> List[Any]:
        """
        Create multiple resources.

        Args:
            data: List of resource data
            **kwargs: Additional arguments

        Returns:
            List of created resources
        """
        skip_validation = kwargs.pop('skip_validation', False)

        # Convert model instances to dicts if needed
        data_dicts = []
        for item in data:
            if hasattr(item, '__dict__'):
                data_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
            else:
                data_dict = item

            data_dicts.append(data_dict)

        created_data = self.database.bulk_create(
            self.collection,
            data_dicts,
            skip_validation=skip_validation
        )

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
        skip_validation = kwargs.pop('skip_validation', False)
        check_version = kwargs.pop('check_version', True)

        # Convert model instances to dicts if needed
        data_dicts = []
        for item in data:
            if hasattr(item, '__dict__'):
                data_dict = {k: v for k, v in item.__dict__.items() if not k.startswith('_')}
            else:
                data_dict = item

            data_dicts.append(data_dict)

        updated_data = self.database.bulk_update(
            self.collection,
            data_dicts,
            skip_validation=skip_validation,
            check_version=check_version
        )

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
        soft_delete = kwargs.pop('soft_delete', False)
        cascade = kwargs.pop('cascade', False)

        return self.database.bulk_delete(
            self.collection,
            ids,
            soft_delete=soft_delete,
            cascade=cascade
        )


class FakeAPI(API):
    client_class = Client
    """
    Fake API implementation with a sophisticated in-memory database.

    This class simulates a real API with an in-memory database that supports:
    - Entity relationships (one-to-one, one-to-many, many-to-many)
    - Advanced filtering with operators and nested fields
    - Sorting by multiple fields
    - Pagination with metadata
    - Data validation rules
    - Unique constraints
    - Soft deletes
    - Optimistic concurrency control
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
        if client_config is None:
            client_config = ClientConfig(hostname="https://api.example.com")
        super().__init__(client, client_config, **kwargs)
        self.database = DataStore()
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

    def define_relationship(
        self,
        source_collection: str,
        target_collection: str,
        relationship_type: str,
        **kwargs: Any
    ) -> 'FakeAPI':
        """
        Define a relationship between collections.

        Args:
            source_collection: Name of the source collection
            target_collection: Name of the target collection
            relationship_type: Type of relationship (ONE_TO_ONE, ONE_TO_MANY, MANY_TO_MANY)
            **kwargs: Additional relationship parameters

        Returns:
            Self for method chaining
        """
        self.database.define_relationship(
            source_collection=source_collection,
            target_collection=target_collection,
            relationship_type=relationship_type,
            **kwargs
        )
        return self

    def add_validation_rule(
        self,
        field: str,
        validator_func: Any,
        error_message: str,
        collection: Optional[str] = None
    ) -> 'FakeAPI':
        """
        Add a validation rule.

        Args:
            field: Field name to validate
            validator_func: Function that takes a value and returns True if valid
            error_message: Error message if validation fails
            collection: Optional collection name to restrict validation to

        Returns:
            Self for method chaining
        """
        self.database.add_validation_rule(
            field=field,
            validator_func=validator_func,
            error_message=error_message,
            collection=collection
        )
        return self

    def add_unique_constraint(
        self,
        fields: Union[str, List[str]],
        error_message: Optional[str] = None,
        collection: Optional[str] = None
    ) -> 'FakeAPI':
        """
        Add a unique constraint.

        Args:
            fields: Field name or list of field names that must be unique together
            error_message: Custom error message
            collection: Optional collection name to restrict constraint to

        Returns:
            Self for method chaining
        """
        self.database.add_unique_constraint(
            fields=fields,
            error_message=error_message,
            collection=collection
        )
        return self

    def set_timestamp_tracking(self, enabled: bool) -> 'FakeAPI':
        """
        Enable or disable automatic timestamp tracking.

        Args:
            enabled: Whether to track creation and update timestamps

        Returns:
            Self for method chaining
        """
        self.database.set_timestamp_tracking(enabled)
        return self

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

    def _register_endpoints(self) -> None:
        """
        Register endpoints.

        This method is required by the API abstract base class.
        """

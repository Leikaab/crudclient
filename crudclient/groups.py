"""
Module `groups.py`
=================

This module defines the ResourceGroup class, which is a base class for grouping related CRUD resources
under a common path segment. ResourceGroup inherits from Crud, allowing it to have its own CRUD operations
while also serving as a container for child resources and nested groups.

Classes:
    - ResourceGroup: Base class for grouping related CRUD resources and other ResourceGroups.
"""

from abc import ABC
from typing import Optional

from .client import Client
from .crud.base import Crud


class ResourceGroup(Crud, ABC):
    """
    Base class for grouping related CRUD resources and other ResourceGroups
    under a common path segment. A ResourceGroup can also have its own
    CRUD operations for its base path, inherited from Crud.

    ResourceGroup inherits from Crud, which means it can perform CRUD operations
    on its own path segment. Additionally, it provides methods for registering
    child endpoints (Crud instances) and child groups (ResourceGroup instances),
    enabling the creation of a hierarchical API structure.

    Attributes:
        _resource_path: The base path for the resource group in the API.
        _datamodel: The data model class for the resource group.
        _api_response_model: Custom API response model, if any.
        allowed_actions: List of allowed methods for this resource group.
    """

    def __init__(self, client: Client, parent: Optional[Crud] = None) -> None:
        """
        Initialize the ResourceGroup.

        Args:
            client: The API client instance.
            parent: The parent Crud instance (could be another ResourceGroup,
                   or None for top-level ResourceGroups instantiated directly by the API class).

        Raises:
            ValueError: If the resource path is not set.
        """
        super().__init__(client, parent)

        # Register child resources and groups
        self._register_child_endpoints()
        self._register_child_groups()

    def _register_child_endpoints(self) -> None:
        """
        Register child Crud resources.

        This method should be overridden by subclasses to register child Crud resources.
        These resources will become direct attributes of the ResourceGroup instance.

        Example in a subclass:
            self.accounts = AccountsCrud(self.client, parent=self)
        """

    def _register_child_groups(self) -> None:
        """
        Register nested ResourceGroup instances.

        This method should be overridden by subclasses to register nested ResourceGroup instances.
        These groups will become direct attributes of the ResourceGroup instance.

        Example in a subclass:
            self.vouchers = VoucherGroup(self.client, parent=self)
        """

"""
ResourceGroup implementations for Tripletex API.

This module defines ResourceGroup classes for organizing related Tripletex API
resources under common path segments, enabling a hierarchical API structure.
"""

from crudclient.groups import ResourceGroup

from .models import (
    Ledger,
    LedgerResponse,
    Voucher,
    VoucherResponse,
)
from .resources_ledger import (
    TripletexHistoricalVoucherCrud,
)


class LedgerGroup(ResourceGroup):
    """
    ResourceGroup for Tripletex ledger operations.

    This group handles operations directly on /ledger endpoint and also serves
    as a container for nested resources related to ledgers (vouchers, etc.).

    Attributes:
        _resource_path: The base path for the ledger resource group in the API.
        _datamodel: The data model class for the ledger resource group.
        _api_response_model: Custom API response model for ledger responses.
        allowed_actions: List of allowed methods for this resource group.
    """

    _resource_path = "ledger"
    _datamodel = Ledger
    _api_response_model = LedgerResponse
    allowed_actions = ["list", "read"]

    def _register_child_groups(self) -> None:
        """
        Register nested ResourceGroup instances.

        This method registers the VoucherGroup as a child of LedgerGroup,
        enabling access to voucher-related endpoints under the ledger path.
        """
        self.voucher = VoucherGroup(self.client, parent=self)


class VoucherGroup(ResourceGroup):
    """
    ResourceGroup for Tripletex voucher operations.

    This group handles operations directly on /ledger/voucher endpoint and also serves
    as a container for nested resources related to vouchers.

    Attributes:
        _resource_path: The base path for the voucher resource group in the API.
        _datamodel: The data model class for the voucher resource group.
        _api_response_model: Custom API response model for voucher responses.
        allowed_actions: List of allowed methods for this resource group.
    """

    _resource_path = "voucher"
    _datamodel = Voucher
    _api_response_model = VoucherResponse
    allowed_actions = ["list", "read"]

    def _register_child_endpoints(self) -> None:
        """
        Register child Crud resources for voucher-related endpoints.

        These resources will become direct attributes of the VoucherGroup instance,
        enabling access to voucher-specific operations like historical vouchers.
        """
        self.historical = TripletexHistoricalVoucherCrud(self.client, parent=self)

"""
CRUD resources for Tripletex ledger-related endpoints.

This module defines CRUD classes for interacting with ledger-related endpoints
in the Tripletex API, including ledgers, vouchers, and historical vouchers.
"""

from typing import Optional, Union, cast

from crudclient.types import JSONDict

from .crud import TripletexCrud
from .models import (
    HistoricalVoucher,
    HistoricalVoucherResponse,
)
from .utils import ensure_date_params


class TripletexHistoricalVoucherCrud(TripletexCrud[HistoricalVoucher]):
    """
    CRUD operations for Tripletex historical vouchers.

    This Crud class is designed to be used with a VoucherGroup parent,
    enabling operations on the /ledger/voucher/historical endpoint.
    """

    _resource_path = "historical"
    _datamodel = HistoricalVoucher
    _api_response_model = HistoricalVoucherResponse
    allowed_actions = ["list", "read", "create"]

    def list(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None, **kwargs) -> HistoricalVoucherResponse:
        """
        List all historical vouchers.

        Args:
            parent_id: The ID of the parent voucher (if applicable).
            params: Optional query parameters. May include 'dateFrom' and 'dateTo'.
            **kwargs: Additional keyword arguments.

        Returns:
            HistoricalVoucherResponse object containing a list of HistoricalVoucher objects.
        """
        # Ensure required date parameters are present
        params = ensure_date_params(params)

        # Call the parent list method with the updated params
        result = super().list(parent_id=parent_id, params=params, **kwargs)
        return cast(HistoricalVoucherResponse, result)

    def create(self, data: Union[dict, JSONDict], parent_id: Optional[str] = None, **kwargs) -> HistoricalVoucher:
        """
        Create a new historical voucher.

        Args:
            data: The data for the new historical voucher.
            parent_id: Optional parent ID if this is a nested resource.
            **kwargs: Additional parameters.

        Returns:
            The created HistoricalVoucher object.
        """
        result = super().create(data, parent_id=parent_id, **kwargs)
        return cast(HistoricalVoucher, result)
